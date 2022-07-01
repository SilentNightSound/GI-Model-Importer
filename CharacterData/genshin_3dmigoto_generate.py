# Author: SilentNightSound#7430
# Splits the output of the 3dmigoto blender plugin into the required buffers, along with generating
# the required .ini file for performing the override

import os
import argparse
import struct
import shutil
import json
import math

def main():
    parser = argparse.ArgumentParser(description="Splits blender 3dmigoto output into required buffers")
    parser.add_argument("-n", "--name", type=str, help="Name of character to use in folders and output files")
    parser.add_argument("--hashfile", type=str, default="hash_info.json", help="Name of hash info file")
    parser.add_argument("--original_tangents", action="store_true", help="(Experimental) Attempts to correct tangents by using original body data")
    args = parser.parse_args()

    if args.hashfile not in os.listdir("."):
        print(f"ERROR: Cannot find {args.hashfile}. Please ensure it is in the same folder. Exiting")
        return

    with open(args.hashfile, "r") as f:
        hash_data = json.load(f)
        if args.name not in hash_data:
            print(f"ERROR: Character hash information not found in {args.hashfile}. Please either manually add hash information or use genshin_3dmigoto_collect.py to generate it from a frame dump. Exiting")
            return

        char_hashes = hash_data[args.name]

    if not os.path.isdir(args.name):
        print(f"ERROR: Unable to find {args.name} folder. Ensure the folder exists. Exiting")
        return

    if f"{args.name}Head.vb" not in os.listdir(args.name):
        print(f"ERROR: Unable to find {args.name}Head.vb. Ensure it exists in the {args.name} folder. Exiting")
        return

    if not os.path.isdir(f"{args.name}Mod"):
        print(f"Creating {args.name}Mod")
        os.mkdir(f"{args.name}Mod")
    else:
        print(f"WARNING: Everything currently in the {args.name}Mod folder will be overwritten - make sure any important files are backed up. Press any button to continue")
        input()


    # TODO: actually use these headers instead of just hardcoding values
    # Need to check the format to see if there are two texcoord or just one
    # For now, the third and fourth objects are just treated as a special case. If there are ever characters with 5 objects,
    #   I will generalize this code to work with N objects
    with open(os.path.join(args.name, f"{args.name}Head.fmt"), "r") as f:
        headers = f.read()
        if "stride: 84" in headers:
            extra_flag = False
        else:
            extra_flag = True
        if len([x for x in os.listdir(args.name) if "Extra2" in x]) > 0:
            print("Found second extra object")
            extra2_flag = True
        else:
            extra2_flag = False

    print("Splitting VB by buffer type, merging body parts")
    position, blend, texcoord = collect_vb(args.name, "Head", extra_flag)
    head_ib = collect_ib(args.name, "Head", 0)

    if len(position)%40 != 0:
        print("ERROR: VB buffer length does not match stride")
    body_start_offset = len(position)//40
    x,y,z = collect_vb(args.name, "Body", extra_flag)
    position += x
    blend += y
    texcoord += z
    body_ib = collect_ib(args.name, "Body", body_start_offset)
    if extra_flag:
        extra_start_offset = len(position)//40
        x, y, z = collect_vb(args.name, "Extra", extra_flag)
        position += x
        blend += y
        texcoord += z
        extra_ib = collect_ib(args.name, "Extra", extra_start_offset)

        if extra2_flag:
            extra2_start_offset = len(position) // 40
            x, y, z = collect_vb(args.name, "Extra2", extra2_flag)
            position += x
            blend += y
            texcoord += z
            extra2_ib = collect_ib(args.name, "Extra2", extra2_start_offset)

    if args.original_tangents:
        print("Replacing tangents with closest originals")
        head_file = [x for x in os.listdir(args.name) if f"{args.name}Head-vb0" in x]
        if not head_file:
            print("ERROR: unable to find original file for tangent data. Exiting")
            return
        head_file = head_file[0]
        with open(os.path.join(args.name, head_file), "r") as f:
            data = f.readlines()
            points = [x.split(":")[1].strip().split(", ") for x in data if "+000 POSITION:" in x]
            tangents = [x.split(":")[1].strip().split(", ") for x in data if "+024 TANGENT:"in x]
            points = [(float(x), float(y), float(z)) for x,y,z in points]
            tangents = [(float(x), float(y), float(z), float(a)) for x, y, z, a in tangents]
            lookup = {}
            for x,y in zip(points, tangents):
                lookup[x] = y

            tree = KDTree(points, 3)

            i = 0
            while i < len(position):
                x,y,z = struct.unpack("f", position[i:i+4])[0],  struct.unpack("f", position[i+4:i+8])[0],  struct.unpack("f", position[i+8:i+12])[0]
                result = tree.get_nearest((x,y,z))[1]
                tx,ty,tz,ta = [struct.pack("f", a) for a in lookup[result]]
                position[i+24:i+28] = tx
                position[i+28:i+32] = ty
                position[i+32:i+36] = tz
                position[i+36:i+40] = ta
                i+=40

    print("Writing merged buffer files")
    with open(os.path.join(f"{args.name}Mod", f"{args.name}Position.buf"), "wb") as f, \
            open(os.path.join(f"{args.name}Mod", f"{args.name}Blend.buf"), "wb") as g, \
            open(os.path.join(f"{args.name}Mod", f"{args.name}Texcoord.buf"), "wb") as h:
        f.write(position)
        g.write(blend)
        h.write(texcoord)

    with open(os.path.join(f"{args.name}Mod", f"{args.name}Head.ib"), "wb") as f, \
            open(os.path.join(f"{args.name}Mod", f"{args.name}Body.ib"), "wb") as g:
        f.write(head_ib)
        g.write(body_ib)

    if extra_flag:
        with open(os.path.join(f"{args.name}Mod", f"{args.name}Extra.ib"), "wb") as h:
            h.write(extra_ib)
        if extra2_flag:
            with open(os.path.join(f"{args.name}Mod", f"{args.name}Extra2.ib"), "wb") as h:
                h.write(extra2_ib)


    print("Copying texture files")
    shutil.copy(os.path.join(args.name, f"{args.name}HeadDiffuse.dds"), os.path.join(f"{args.name}Mod", f"{args.name}HeadDiffuse.dds"))
    shutil.copy(os.path.join(args.name, f"{args.name}HeadLightMap.dds"), os.path.join(f"{args.name}Mod", f"{args.name}HeadLightMap.dds"))
    shutil.copy(os.path.join(args.name, f"{args.name}BodyDiffuse.dds"), os.path.join(f"{args.name}Mod", f"{args.name}BodyDiffuse.dds"))
    shutil.copy(os.path.join(args.name, f"{args.name}BodyLightmap.dds"), os.path.join(f"{args.name}Mod", f"{args.name}BodyLightMap.dds"))
    if extra_flag:
        shutil.copy(os.path.join(args.name, f"{args.name}ExtraDiffuse.dds"),
                    os.path.join(f"{args.name}Mod", f"{args.name}ExtraDiffuse.dds"))
        shutil.copy(os.path.join(args.name, f"{args.name}ExtraLightMap.dds"),
                    os.path.join(f"{args.name}Mod", f"{args.name}ExtraLightMap.dds"))

        if extra2_flag:
            shutil.copy(os.path.join(args.name, f"{args.name}Extra2Diffuse.dds"),
                        os.path.join(f"{args.name}Mod", f"{args.name}Extra2Diffuse.dds"))
            shutil.copy(os.path.join(args.name, f"{args.name}Extra2LightMap.dds"),
                        os.path.join(f"{args.name}Mod", f"{args.name}Extra2LightMap.dds"))


    # TODO: Populate template file instead of hardcoded
    print("Generating .ini file")
    ini_data = f"; {args.name}\n\n"

    ini_data += f"; Overrides -------------------------\n\n"
    ini_data += f"[TextureOverride{args.name}Position]\nhash = {char_hashes['position_vb']}\nvb0 = Resource{args.name}Position\n\n"
    ini_data += f"[TextureOverride{args.name}Blend]\nhash = {char_hashes['blend_vb']}\nvb1 = Resource{args.name}Blend\nhandling = skip\ndraw = {len(position)//40},0 \n\n"
    ini_data += f"[TextureOverride{args.name}Texcoord]\nhash = {char_hashes['texcoord_vb']}\nvb1 = Resource{args.name}Texcoord\n\n"
    ini_data += f"[TextureOverride{args.name}IB]\nhash = {char_hashes['ib']}\nhandling = skip\ndrawindexed = auto\n\n"
    ini_data += f"[TextureOverride{args.name}Head]\nhash = {char_hashes['ib']}\nmatch_first_index = {char_hashes['object_indexes'][0]}\nib = Resource{args.name}HeadIB\nps-t0 = Resource{args.name}HeadDiffuse\nps-t1 = Resource{args.name}HeadLightMap\n\n"
    ini_data += f"[TextureOverride{args.name}Body]\nhash = {char_hashes['ib']}\nmatch_first_index = {char_hashes['object_indexes'][1]}\nib = Resource{args.name}BodyIB\nps-t0 = Resource{args.name}BodyDiffuse\nps-t1 = Resource{args.name}BodyLightMap\n\n"
    if extra_flag:
        ini_data += f"[TextureOverride{args.name}Extra]\nhash = {char_hashes['ib']}\nmatch_first_index = {char_hashes['object_indexes'][2]}\nib = Resource{args.name}ExtraIB\nps-t0 = Resource{args.name}ExtraDiffuse\nps-t1 = Resource{args.name}ExtraLightMap\n\n"
        if extra2_flag:
            ini_data += f"[TextureOverride{args.name}Extra2]\nhash = {char_hashes['ib']}\nmatch_first_index = {char_hashes['object_indexes'][3]}\nib = Resource{args.name}Extra2IB\nps-t0 = Resource{args.name}Extra2Diffuse\nps-t1 = Resource{args.name}Extra2LightMap\n\n"

    ini_data += f"; Resources -------------------------\n\n"
    ini_data += f"[Resource{args.name}Position]\ntype = Buffer\nstride = 40\nfilename = {args.name}Position.buf\n\n"
    ini_data += f"[Resource{args.name}Blend]\ntype = Buffer\nstride = 32\nfilename = {args.name}Blend.buf\n\n"
    if extra_flag:
        ini_data += f"[Resource{args.name}Texcoord]\ntype = Buffer\nstride = 20\nfilename = {args.name}Texcoord.buf\n\n"
    else:
        ini_data += f"[Resource{args.name}Texcoord]\ntype = Buffer\nstride = 12\nfilename = {args.name}Texcoord.buf\n\n"

    ini_data += f"[Resource{args.name}HeadIB]\ntype = Buffer\nformat = DXGI_FORMAT_R16_UINT\nfilename = {args.name}Head.ib\n\n"
    ini_data += f"[Resource{args.name}BodyIB]\ntype = Buffer\nformat = DXGI_FORMAT_R16_UINT\nfilename = {args.name}Body.ib\n\n"
    if extra_flag:
        ini_data += f"[Resource{args.name}ExtraIB]\ntype = Buffer\nformat = DXGI_FORMAT_R16_UINT\nfilename = {args.name}Extra.ib\n\n"
        if extra2_flag:
            ini_data += f"[Resource{args.name}Extra2IB]\ntype = Buffer\nformat = DXGI_FORMAT_R16_UINT\nfilename = {args.name}Extra2.ib\n\n"
    ini_data += f"[Resource{args.name}HeadDiffuse]\nfilename = {args.name}HeadDiffuse.dds\n\n"
    ini_data += f"[Resource{args.name}HeadLightMap]\nfilename = {args.name}HeadLightMap.dds\n\n"
    ini_data += f"[Resource{args.name}BodyDiffuse]\nfilename = {args.name}BodyDiffuse.dds\n\n"
    ini_data += f"[Resource{args.name}BodyLightMap]\nfilename = {args.name}BodyLightMap.dds\n\n"
    if extra_flag:
        ini_data += f"[Resource{args.name}ExtraDiffuse]\nfilename = {args.name}ExtraDiffuse.dds\n\n"
        ini_data += f"[Resource{args.name}ExtraLightMap]\nfilename = {args.name}ExtraLightMap.dds\n\n"
        if extra2_flag:
            ini_data += f"[Resource{args.name}Extra2Diffuse]\nfilename = {args.name}Extra2Diffuse.dds\n\n"
            ini_data += f"[Resource{args.name}Extra2LightMap]\nfilename = {args.name}Extra2LightMap.dds\n\n"

    with open(os.path.join(f"{args.name}Mod", f"{args.name}.ini"), "w") as f:
        print("Writing ini file")
        f.write(ini_data)

    print("All operations completed, exiting")


# https://github.com/Vectorized/Python-KD-Tree
# A brute force solution for finding the original tangents is O(n^2), and isn't good enough since n can get quite
#   high in many models (upwards of a minute calculation time in some cases)
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

def collect_vb(name, classification, extra_flag):
    position = bytearray()
    blend = bytearray()
    texcoord = bytearray()
    with open(os.path.join(name, f"{name}{classification}.vb"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            position += data[i:i+40]
            blend += data[i+40:i+72]
            if extra_flag:
                texcoord += data[i+72:i+92]
                i += 92
            else:
                texcoord += data[i+72:i+84]
                i += 84
    return position, blend, texcoord


def collect_ib(name, classification, offset):
    ib = bytearray()
    with open(os.path.join(name, f"{name}{classification}.ib"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack('1H', struct.unpack('1H', data[i:i+2])[0]+offset)
            i += 2
    return ib


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
