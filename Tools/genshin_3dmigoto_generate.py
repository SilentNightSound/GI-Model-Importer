# Author: SilentNightSound#7430
# Splits the output of the 3dmigoto blender plugin into the required buffers, along with generating
# the required .ini file for performing the override

import os
import sys
import argparse
import struct
import shutil
import json
import math

def main():
    parser = argparse.ArgumentParser(description="Splits blender 3dmigoto output into required buffers")
    parser.add_argument("-n", "--name", type=str, help="Name of character to use in folders and output files")
    parser.add_argument("--hashfile", type=str, default="hash.json", help="(Deprecated) Name of hash info file")
    parser.add_argument("--original_tangents", action="store_true", help="(Experimental) Attempts to correct tangents by using original body data")
    args = parser.parse_args()

    if not os.path.isdir(args.name):
        print(f"ERROR: Unable to find {args.name} folder. Ensure the folder exists. Exiting")
        return

    char_hash = load_hashes(args.name, args.hashfile)
    create_mod_folder(args.name)

    # Previous version had all these hardcoded at the end; now, we dynamically assemble the ini file as we add components
    vb_override_ini = ""
    ib_override_ini = ""
    vb_res_ini = ""
    ib_res_ini = ""
    tex_res_ini = ""

    for component in char_hash:

        # Support for custom names was added so we need this to retain backwards compatibility
        if "component_name" in component:
            component_name = component["component_name"]
        else:
            component_name = ""

        # Old version used "Extra" as the third object, but I've replaced it with dress - need this for backwards compatibility
        if "object_classifications" in component:
            object_classifications = component["object_classifications"]
        else:
            object_classifications = ["Head", "Body", "Extra"]

        current_name = f"{args.name}{component_name}"

        print(f"\nWorking on {current_name}")

        # Components without draw vbs are texture overrides only
        if component["draw_vb"]:

            with open(os.path.join(args.name, f"{current_name}{object_classifications[0]}.fmt"), "r") as f:
                stride = int([x.split(": ")[1] for x in f.readlines() if "stride:" in x][0])

            offset = 0
            position, blend, texcoord = bytearray(), bytearray(), bytearray()
            ib_override_ini += f"[TextureOverride{current_name}IB]\nhash = {component['ib']}\nhandling = skip\ndrawindexed = auto\n\n"
            for i in range(len(component["object_indexes"])):
                if i+1>len(object_classifications):
                    current_object = f"{object_classifications[-1]}{i + 2 - len(object_classifications)}"
                else:
                    current_object = object_classifications[i]

                print(f"\nCollecting {current_object}")

                # This is the path for components which have blend data (characters, complex weapons, etc.)
                if component["blend_vb"]:
                    print("Splitting VB by buffer type, merging body parts")
                    x,y,z = collect_vb(args.name, current_name, current_object, stride)
                    position += x
                    blend += y
                    texcoord += z
                    position_stride = 40

                # This is the path for components without blend data (simple weapons, objects, etc.)
                # Simplest route since we do not need to split up the buffer into multiple components
                else:
                    position += collect_vb_single(args.name, current_name, current_object, stride)
                    position_stride = stride

                print("Collecting IB")
                print(current_name, current_object, offset)
                ib = collect_ib(args.name, current_name, current_object, offset)
                with open(os.path.join(f"{args.name}Mod", f"{current_name}{current_object}.ib"), "wb") as f:
                    f.write(ib)
                ib_override_ini += f"[TextureOverride{current_name}{current_object}]\nhash = {component['ib']}\nmatch_first_index = {component['object_indexes'][i]}\nib = Resource{current_name}{current_object}IB\n"
                ib_res_ini += f"[Resource{current_name}{current_object}IB]\ntype = Buffer\nformat = DXGI_FORMAT_R32_UINT\nfilename = {current_name}{current_object}.ib\n\n"

                if len(position)%position_stride != 0:
                    print("ERROR: VB buffer length does not match stride")

                offset = len(position)//position_stride

                # Older versions can only manage diffuse and lightmaps
                if "texture_hashes" in component:
                    texture_hashes = component["texture_hashes"][i]
                else:
                    texture_hashes = [["Diffuse", ".dds", "_"], ["LightMap", ".dds", "_"]]

                print("Copying texture files")

                for j, texture in enumerate(texture_hashes):
                    shutil.copy(os.path.join(args.name, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                os.path.join(f"{args.name}Mod", f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                    ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n"
                    tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                ib_override_ini += "\n"


            if args.original_tangents:
                print("Replacing tangents with closest originals")
                head_file = [x for x in os.listdir(args.name) if f"{current_name}{current_object}-vb0" in x]
                if not head_file:
                    print("ERROR: unable to find original file for tangent data. Exiting")
                    return
                head_file = head_file[0]
                with open(os.path.join(args.name, head_file), "r") as f:
                    data = f.readlines()
                    raw_points = [x.split(":")[1].strip().split(", ") for x in data if "+000 POSITION:" in x]
                    tangents = [x.split(":")[1].strip().split(", ") for x in data if "+024 TANGENT:"in x]
                    if len(raw_points[0]) == 3:
                        points = [(float(x), float(y), float(z)) for x,y,z in raw_points]
                    else:
                        points = [(float(x), float(y), float(z)) for x, y, z, _ in raw_points]
                    tangents = [(float(x), float(y), float(z), float(a)) for x, y, z, a in tangents]
                    lookup = {}
                    for x,y in zip(points, tangents):
                        lookup[x] = y

                    tree = KDTree(points, 3)

                    i = 0
                    while i < len(position):
                        if len(raw_points[0]) == 3:
                            x,y,z = struct.unpack("f", position[i:i+4])[0],  struct.unpack("f", position[i+4:i+8])[0],  struct.unpack("f", position[i+8:i+12])[0]
                            result = tree.get_nearest((x,y,z))[1]
                            tx,ty,tz,ta = [struct.pack("f", a) for a in lookup[result]]
                            position[i+24:i+28] = tx
                            position[i+28:i+32] = ty
                            position[i+32:i+36] = tz
                            position[i+36:i+40] = ta
                            i+=40
                        else:
                            x, y, z = struct.unpack("e", position[i:i+2])[0],  struct.unpack("e", position[i+2:i+4])[0],  struct.unpack("e", position[i+4:i+6])[0]
                            result = tree.get_nearest((x, y, z))[1]
                            tx, ty, tz, ta = [(int(a*255)).to_bytes(1, byteorder="big") for a in lookup[result]]

                            position[i + 24:i + 25] = tx
                            position[i + 25:i + 26] = ty
                            position[i + 26:i + 27] = tz
                            position[i + 27:i + 28] = ta
                            i += 28

            if component["blend_vb"]:
                print("Writing merged buffer files")
                with open(os.path.join(f"{args.name}Mod", f"{current_name}Position.buf"), "wb") as f, \
                        open(os.path.join(f"{args.name}Mod", f"{current_name}Blend.buf"), "wb") as g, \
                        open(os.path.join(f"{args.name}Mod", f"{current_name}Texcoord.buf"), "wb") as h:
                    f.write(position)
                    g.write(blend)
                    h.write(texcoord)

                vb_override_ini += f"[TextureOverride{current_name}Position]\nhash = {component['position_vb']}\nvb0 = Resource{current_name}Position\n\n"
                vb_override_ini += f"[TextureOverride{current_name}Blend]\nhash = {component['blend_vb']}\nvb1 = Resource{current_name}Blend\nhandling = skip\ndraw = {len(position) // 40},0 \n\n"
                vb_override_ini += f"[TextureOverride{current_name}Texcoord]\nhash = {component['texcoord_vb']}\nvb1 = Resource{current_name}Texcoord\n\n"
                vb_override_ini += f"[TextureOverride{current_name}VertexLimitRaise]\nhash = {component['draw_vb']}\n\n"

                vb_res_ini += f"[Resource{current_name}Position]\ntype = Buffer\nstride = 40\nfilename = {current_name}Position.buf\n\n"
                vb_res_ini += f"[Resource{current_name}Blend]\ntype = Buffer\nstride = 32\nfilename = {current_name}Blend.buf\n\n"
                vb_res_ini += f"[Resource{current_name}Texcoord]\ntype = Buffer\nstride = {stride-72}\nfilename = {current_name}Texcoord.buf\n\n"
            else:
                with open(os.path.join(f"{args.name}Mod", f"{current_name}.buf"), "wb") as f:
                    f.write(position)
                vb_override_ini += f"[TextureOverride{current_name}]\nhash = {component['draw_vb']}\nvb0 = Resource{current_name}\n\n"
                vb_res_ini += f"[Resource{current_name}]\ntype = Buffer\nstride = {stride}\nfilename = {current_name}.buf\n\n"


        # This is the path for components with only texture overrides (faces, wings, etc.)
        # Theoretically possible to combine with the above to cut down on code, but results in lots of messy if statements
        else:
            for i in range(len(component["object_indexes"])):
                if i>2:
                    current_object = f"{object_classifications[2]}{i-1}"
                else:
                    current_object = object_classifications[i]

                print(f"\nTexture override only on {current_object}")

                if component["texture_hashes"]:
                    texture_hashes = component["texture_hashes"][i]
                else:
                    texture_hashes = [{"Diffuse": "_"}, {"LightMap": "_"}]

                print("Copying texture files")
                # Stopgap measure to prevent warnings from showing up on faces since they share hashes for higher numbered textures
                if component["component_name"] == "Face":
                    j = 0
                    texture = texture_hashes[j]
                    ib_override_ini += f"[TextureOverride{current_name}{current_object}{texture[0]}]\nhash = {texture[2]}\n"
                    shutil.copy(os.path.join(args.name, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                os.path.join(f"{args.name}Mod", f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                    ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n\n"
                    tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                else:
                    for j, texture in enumerate(texture_hashes):
                        ib_override_ini += f"[TextureOverride{current_name}{current_object}{texture[0]}]\nhash = {texture[2]}\n"
                        shutil.copy(os.path.join(args.name, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                    os.path.join(f"{args.name}Mod", f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                        ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n\n"
                        tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                ib_override_ini += "\n"


    print("Generating .ini file")
    ini_data = f"; {args.name}\n\n"
    ini_data += f"; Overrides -------------------------\n\n" + vb_override_ini + ib_override_ini
    ini_data += f"; Resources -------------------------\n\n" + vb_res_ini + ib_res_ini + tex_res_ini
    ini_data += f"\n; .ini generated by GIMI (Genshin-Impact-Model-Importer)\n" \
        f"; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord"

    with open(os.path.join(f"{args.name}Mod", f"{args.name}.ini"), "w") as f:
        print("Writing ini file")
        f.write(ini_data)

    print("All operations completed, exiting")



def load_hashes(name, hashfile):
    if hashfile not in os.listdir(name):
        print("WARNING: Could not find hash.info in character directory. Falling back to hash_info.json")
        if "hash_info.json" not in os.listdir("."):
            print(f"ERROR: Cannot find hash.json or hash_info.json. Exiting")
            sys.exit()
        # Backwards compatibility with the old hash_info.json
        with open("hash_info.json", "r") as f:
            hash_data = json.load(f)
            char_hashes = [hash_data[name]]
    else:
        with open(os.path.join(name, hashfile), "r") as f:
            char_hashes = json.load(f)

    return char_hashes


def create_mod_folder(name):
    if not os.path.isdir(f"{name}Mod"):
        print(f"Creating {name}Mod")
        os.mkdir(f"{name}Mod")
    else:
        print(
            f"WARNING: Everything currently in the {name}Mod folder will be overwritten - make sure any important files are backed up. Press any button to continue")
        input()

def collect_vb(folder, name, classification, stride, ignore_tangent=True):
    position = bytearray()
    blend = bytearray()
    texcoord = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.vb"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            # This gave me a lot of trouble - the "tangent" the game uses doesn't seem to be any sort of tangent I'm
            #   familiar with. In fact, it has a lot more in common with the normal
            # Setting this equal to the normal gives significantly better results in most cases than using the tangent
            #   calculated by blender
            import binascii
            if ignore_tangent:
                position += data[i:i + 24]
                position += data[i+12:i+24] + bytearray(struct.pack("f", 1))
            else:
                position += data[i:i+40]
            blend += data[i+40:i+72]
            texcoord += data[i+72:i+stride]
            i += stride
    return position, blend, texcoord


def collect_ib(folder, name, classification, offset):
    ib = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.ib"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack('1I', struct.unpack('1I', data[i:i+4])[0]+offset)
            i += 4
    return ib


def collect_vb_single(folder, name, classification, stride, ignore_tangent=True):
    result = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.vb"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            if ignore_tangent:
                result += data[i:i + stride - 4] + data[i+8:i+12]
            else:
                result += data[i:i+stride]
            i += stride
    return result

# Parsing the headers for vb0 txt files
# This has been constructed by the collect script, so its headers are much more accurate than the originals
def parse_buffer_headers(headers, filters):
    results = []
    # https://docs.microsoft.com/en-us/windows/win32/api/dxgiformat/ne-dxgiformat-dxgi_format
    for element in headers.split("]:")[1:]:
        lines = element.strip().splitlines()
        name = lines[0].split(": ")[1]
        index = lines[1].split(": ")[1]
        data_format = lines[2].split(": ")[1]
        bytewidth = sum([int(x) for x in re.findall("([0-9]*)[^0-9]", data_format.split("_")[0]+"_") if x])//8

        # A bit annoying, but names can be very similar so need to match filter format exactly
        element_name = name
        if index != "0":
            element_name += index
        if element_name+":" not in filters:
            continue

        results.append({"semantic_name": name, "element_name": element_name, "index": index, "format": data_format, "bytewidth": bytewidth})

    return results


# https://github.com/Vectorized/Python-KD-Tree
# A brute force solution for finding the original tangents is O(n^2), and isn't good enough since n can get quite
#   high in many models (upwards of a minute calculation time in some cases)
# So we use a simple KD structure to perform quick nearest neighbor lookups
class KDTree(object):
    """
    Usage:
    1. Make the KD-Tree:
        `kd_tree = KDTree(points, dim)`
    2. You can then use `get_knn` for k nearest neighbors or
       `get_nearest` for the nearest neighbor
    points are be a list of points: [[0, 1, 2], [12.3, 4.5, 2.3], ...]
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup.
        Parameters
        ----------
        points : list<point>
            A list of points.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance
            between the two points.
            If omitted, it uses the default implementation.
        """

        if dist_sq_func is None:
            dist_sq_func = lambda a, b: sum((x - b[i]) ** 2
                                            for i, x in enumerate(a))

        def make(points, i=0):
            if len(points) > 1:
                points.sort(key=lambda x: x[i])
                i = (i + 1) % dim
                m = len(points) >> 1
                return [make(points[:m], i), make(points[m + 1:], i),
                        points[m]]
            if len(points) == 1:
                return [None, None, points[0]]

        def add_point(node, point, i=0):
            if node is not None:
                dx = node[2][i] - point[i]
                for j, c in ((0, dx >= 0), (1, dx < 0)):
                    if c and node[j] is None:
                        node[j] = [None, None, point]
                    elif c:
                        add_point(node[j], point, (i + 1) % dim)

        import heapq
        def get_knn(node, point, k, return_dist_sq, heap, i=0, tiebreaker=1):
            if node is not None:
                dist_sq = dist_sq_func(point, node[2])
                dx = node[2][i] - point[i]
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, tiebreaker, node[2]))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, tiebreaker, node[2]))
                i = (i + 1) % dim
                # Goes into the left branch, then the right branch if needed
                for b in (dx < 0, dx >= 0)[:1 + (dx * dx < -heap[0][0])]:
                    get_knn(node[b], point, k, return_dist_sq,
                            heap, i, (tiebreaker << 1) | b)
            if tiebreaker == 1:
                return [(-h[0], h[2]) if return_dist_sq else h[2]
                        for h in sorted(heap)][::-1]

        def walk(node):
            if node is not None:
                for j in 0, 1:
                    for x in walk(node[j]):
                        yield x
                yield node[2]

        self._add_point = add_point
        self._get_knn = get_knn
        self._root = make(points)
        self._walk = walk

    def __iter__(self):
        return self._walk(self._root)

    def add_point(self, point):
        """Adds a point to the kd-tree.

        Parameters
        ----------
        point : array-like
            The point.
        """
        if self._root is None:
            self._root = [None, None, point]
        else:
            self._add_point(self._root, point)

    def get_knn(self, point, k, return_dist_sq=True):
        """Returns k nearest neighbors.
        Parameters
        ----------
        point : array-like
            The point.
        k: int
            The number of nearest neighbors.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distances.
        Returns
        -------
        list<array-like>
            The nearest neighbors.
            If `return_dist_sq` is true, the return will be:
                [(dist_sq, point), ...]
            else:
                [point, ...]
        """
        return self._get_knn(self._root, point, k, return_dist_sq, [])

    def get_nearest(self, point, return_dist_sq=True):
        """Returns the nearest neighbor.
        Parameters
        ----------
        point : array-like
            The point.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distance.
        Returns
        -------
        array-like
            The nearest neighbor.
            If the tree is empty, returns `None`.
            If `return_dist_sq` is true, the return will be:
                (dist_sq, point)
            else:
                point
        """
        l = self._get_knn(self._root, point, 1, return_dist_sq, [])
        return l[0] if len(l) else None


def find_closest(lines, x,y,z):
    i = 0
    closest_distance = math.inf
    closest_tangent = []
    while i<len(lines)-1:
        distance = abs(x-lines[i][0]) + abs(y-lines[i][1]) + abs(z-lines[i][2])
        if distance < closest_distance:
            closest_distance = distance
            closest_tangent = lines[i+1]
        i+=2
    return closest_tangent


if __name__ == "__main__":
    main()
