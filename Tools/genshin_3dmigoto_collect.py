# Author: SilentNightSound#7430
# Collects and organizes the relevant character model data from a frame dump, outputting it in a format
# that the Blender 3Dmigoto plugin recognizes

# Currently only works for player characters, and not yet tested on every character

import os
import sys
import argparse
import shutil
import json

def main():
    parser = argparse.ArgumentParser(description="Collects, organizes and compiles character buffer data from frame dumps")
    parser.add_argument("-vb", type=str, help="Main VB character is drawn on")
    parser.add_argument("-n", "--name", type=str, help="Name of character to use in folders and output files")
    parser.add_argument("-f", "--framedump", type=str, help="Name of framedump folder")
    parser.add_argument("-r", "--recent", action='store_true', help="Use the most recent framedump folder instead of specifying")
    parser.add_argument("-vs", type=str, default="653c63ba4a73ca8b", help="Root VS for character model")
    parser.add_argument("--force", nargs="+", help="Force parser to use specified ids")
    parser.add_argument("--ignore", action='store_true', help="Ignores duplicate objects")
    args = parser.parse_args()


    root_vs_hash = args.vs
    draw_vb_hash = args.vb
    if args.recent:
        print("Looking for most recent frame dump folder")
        frame_dump = [x for x in os.listdir(".") if "FrameAnalysis" in x][-1]
        if frame_dump:
            print(f"Found! Folder: {frame_dump}")
        else:
            print("Not found. Trying to load folder from script input")
            frame_dump = args.framedump
    else:
        frame_dump = args.framedump
    character = args.name

    object_classifications = {0: "Head", 1: "Body", 2: "Extra"}

    position_vb = ""
    blend_vb = ""
    texcoord_vb = ""
    first_vs = ""

    relevant_ids = []

    print("Creating output folder")
    if not os.path.isdir(character):
        os.mkdir(character)
    else:
        print(f"WARNING: Everything currently in the {args.name} folder will be overwritten - make sure any important files are backed up. Press any button to continue")
        input()

    frame_dump_files = os.listdir(frame_dump)

    # First pass to give us the VB for the position and blend data, as well as identify the relevant draw ids
    print("Searching for VB corresponding with root VS")
    for filename in frame_dump_files:
        if root_vs_hash in filename and "-vb0=" in filename and os.path.splitext(filename)[1] == ".txt":
            print(f"Found position VB: {filename}")
            if position_vb and not args.ignore:
                print("ERROR: found two character objects in frame dump. Exiting")
                print(position_vb, filename)
                continue
            position_vb = filename
        if root_vs_hash in filename and "-vb1=" in filename and os.path.splitext(filename)[1] == ".txt":
            print(f"Found blend VB: {filename}")
            if blend_vb and not args.ignore:
                print("ERROR: found two character objects in frame dump. Exiting")
                print(blend_vb, filename)
                continue
            blend_vb = filename

        if draw_vb_hash in filename:
            draw_id = filename.split("-")[0]
            if not first_vs and int(draw_id) > 10:
                first_vs = filename.split("vs=")[1].split("-")[0]
                print(f"Found first VS: {first_vs}")
            # The low ids that correspond to the object are a bit weird and I don't fully understand them yet
            # The higher ids should have all the info we need
            if draw_id not in relevant_ids and int(draw_id)>10:
                relevant_ids.append(draw_id)

    if not position_vb or not blend_vb:
        print("ERROR: Unable to find root position and blend VB. Exiting")
        return

    print(f"Relevant IDs: {relevant_ids}")

    # Second pass to collect IBs, texcoord VB, and diffuse/light maps
    model_data = {}
    previous_id = relevant_ids[0]
    texcoord_largest_size = -1

    # A couple of characters have unique draw call formats, this forces a specific list of ids to be parsed
    if args.force:
        print(f"Ignoring found IDs and forcing analysis on IDs {args.force}")
        relevant_ids = args.force
    for current_id in relevant_ids:

        # Draw calls for characters either come in pairs or triples
        if not args.force and int(current_id) - int(previous_id) > 1:
            print("Finished collecting information")
            break

        # Collecting IB file for portion of model being drawn on the current id
        current_id_files = [name for name in frame_dump_files if f"{current_id}-" in name]
        draw_ib = [name for name in current_id_files if "-ib=" in name and os.path.splitext(name)[1] == ".txt"]
        if len(draw_ib) != 1:
            print(f"ERROR: Unable to find corresponding IB for draw ID {current_id}. Exiting")
            return
        draw_ib = draw_ib[0]

        with open(os.path.join(frame_dump, draw_ib), "r") as f:
            first_index = -1
            for line in f.readlines():
                if "first index:"in line:
                    first_index = int(line.split(":")[1].strip())
                    break
            if first_index < 0:
                print("ERROR: Unrecognized IB format. Exiting")
                return
        print(f"ID: {current_id}, found object at index {first_index}")
        model_data[first_index] = [draw_ib]

        # Even though each object technically has its own texcoord, they are all just portions of a single vb
        # The largest file will always contain the full texcoord for every point
        texcoord_vb_candidate = [name for name in current_id_files if "-vb1=" in name and os.path.splitext(name)[1] == ".txt"]
        if len(texcoord_vb_candidate) != 1:
            print(f"ERROR: Unable to find corresponding texcoord information for draw ID {current_id}. Exiting")
            return
        texcoord_vb_candidate = texcoord_vb_candidate[0]

        texcoord_size = os.stat(os.path.join(frame_dump, texcoord_vb_candidate)).st_size
        if texcoord_size > texcoord_largest_size:
            texcoord_largest_size = texcoord_size
            texcoord_vb = texcoord_vb_candidate

        # Finally, collect textures
        # As far as I can tell, all object models have two each though they might not be unique
        # I don't know what the higher numbered textures are for, but they don't seem to have any impact
        texture_maps = [name for name in current_id_files if "-ps-t" in name and os.path.splitext(name)[1] == ".dds"]
        if len(texture_maps)<2:
            print(f"ERROR: Unable to find diffuse and lightmaps for {current_id}. Exiting")
            return

        model_data[first_index].append(texture_maps[0])
        model_data[first_index].append(texture_maps[1])

        previous_id = current_id

    if len(model_data.keys()) < 2:
        print(f"ERROR: Unable to find all model components. Only found: {model_data.keys()}. Exiting")
        return

    # Collecting this information from the .buf is simpler, but we lose out on the header information
    # Order is POSITION (R32G32B32_FLOAT), NORMAL (R32G32B32_FLOAT), TANGENT (R32G32B32A32_FLOAT)
    # Sizes are 12, 12, 16 for a total stride of 40
    # All other values ignored
    print("Collecting position data")
    position = []
    with open(os.path.join(frame_dump, position_vb), "r") as f:
        headers, data = f.read().split("vertex-data:\n")
        data = data.strip().split("\n")
        # These are not the colors and texcoord we want
        data = [line for line in data if "COLOR:" not in line and "TEXCOORD" not in line and line]
        vertex_group = []
        for i in range(len(data)):
            vertex = data[i].split(":")[1].strip().split(", ")
            vertex_group.append(vertex)
            i += 1
            if i%3 == 0:
                position.append(vertex_group)
                vertex_group = []

    # Order is BLENDWEIGHT (R32G32B32A32_FLOAT), BLENDINDICES (R32G32B32A32_SINT)
    # Sizes are 16,16 for a total stride of 32
    print("Collecting blend data")
    blend = []
    with open(os.path.join(frame_dump, blend_vb), "r") as f:
        headers, data = f.read().split("vertex-data:\n")
        data = data.strip().split("\n")
        data = [line for line in data if line]
        vertex_group = []
        for i in range(len(data)):
            vertex = data[i].split(":")[1].strip().split(", ")
            vertex_group.append(vertex)
            i += 1
            if i%2 == 0:
                blend.append(vertex_group)
                vertex_group = []

    # Some characters have one texcoord, others have two, varies from character to character
    # Order is COLOR (R8G8B8A8_UNORM), TEXCOORD (R32G32_FLOAT), *TEXCOORD1 (R32G32_FLOAT) if it exists
    # Sizes are 4, 8, *8 for a total of either 12 or 20
    print("Collecting texcoord data")
    texcoord = []
    with open(os.path.join(frame_dump, texcoord_vb), "r") as f:
        headers, data = f.read().split("vertex-data:\n")
        data = data.strip().split("\n")
        if "stride: 20" in headers:
            tex_group_count = 3
        else:
            tex_group_count = 2
            data = [line for line in data if "TEXCOORD1" not in line]
        data = [line for line in data if line]
        vertex_group = []
        for i in range(len(data)):
            vertex = data[i].split(":")[1].strip().split(", ")
            vertex_group.append(vertex)
            i += 1
            if i % tex_group_count == 0:
                texcoord.append(vertex_group)
                vertex_group = []

    if len(position) != len(blend) or len(blend) != len(texcoord):
        print(f"Error: Size mismatch between buffers. Position: {len(position)}, Blend: {len(blend)}, Texcoord: {len(texcoord)}. Exiting")

        return

    # TODO: load these headers from a separate file, or dynamically calculate them from the original .txt buffers
    print("Constructing combined buffer")
    vb_merged = ""
    if tex_group_count == 3:
        vb_merged += "stride: 92\n"
    else:
        vb_merged += "stride: 84\n"
    vb_merged += f"first vertex: 0\nvertex count: {len(position)}\ntopology: trianglelist\n"
    vb_merged += "element[0]:\n  SemanticName: POSITION\n  SemanticIndex: 0\n  Format: R32G32B32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 0\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[1]:\n  SemanticName: NORMAL\n  SemanticIndex: 0\n  Format: R32G32B32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 12\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[2]:\n  SemanticName: TANGENT\n  SemanticIndex: 0\n  Format: R32G32B32A32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 24\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[3]:\n  SemanticName: BLENDWEIGHT\n  SemanticIndex: 0\n  Format: R32G32B32A32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 40\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[4]:\n  SemanticName: BLENDINDICES\n  SemanticIndex: 0\n  Format: R32G32B32A32_SINT\n  InputSlot: 0\n  AlignedByteOffset: 56\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[5]:\n  SemanticName: COLOR\n  SemanticIndex: 0\n  Format: R8G8B8A8_UNORM\n  InputSlot: 0\n  AlignedByteOffset: 72\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    vb_merged += "element[6]:\n  SemanticName: TEXCOORD\n  SemanticIndex: 0\n  Format: R32G32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 76\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"
    if tex_group_count == 3:
        vb_merged += "element[7]:\n  SemanticName: TEXCOORD\n  SemanticIndex: 1\n  Format: R32G32_FLOAT\n  InputSlot: 0\n  AlignedByteOffset: 84\n  InputSlotClass: per-vertex\n  InstanceDataStepRate: 0\n"

    vb_merged += "\nvertex-data:\n\n"
    for i in range(len(position)):
        vb_merged += f"vb0[{i}]+000 POSITION: " + ", ".join(position[i][0]) + "\n"
        vb_merged += f"vb0[{i}]+012 NORMAL: " + ", ".join(position[i][1]) + "\n"
        vb_merged += f"vb0[{i}]+024 TANGENT: " + ", ".join(position[i][2]) + "\n"
        vb_merged += f"vb0[{i}]+040 BLENDWEIGHT: " + ", ".join(blend[i][0]) + "\n"
        vb_merged += f"vb0[{i}]+040 BLENDINDICES: " + ", ".join(blend[i][1]) + "\n"
        vb_merged += f"vb0[{i}]+072 COLOR: " + ", ".join(texcoord[i][0]) + "\n"
        vb_merged += f"vb0[{i}]+076 TEXCOORD: " + ", ".join(texcoord[i][1]) + "\n"
        if len(texcoord[i]) == 3:
            vb_merged += f"vb0[{i}]+084 TEXCOORD1: " + ", ".join(texcoord[i][2]) + "\n"
        vb_merged += "\n"

    vb_merged = vb_merged[:-1]

    # Now that we have all the buffer data, assemble the final output
    print("Constructing final buffers")
    position_vb_hash = position_vb.split("=")[1].split("-")[0]
    sorted_indexes = sorted(model_data.keys())
    count = 0
    for index in sorted_indexes:
        classification = object_classifications[count]
        print(f"{classification} object at index {index}")
        print(f"Relevant files: {model_data[index]}")
        with open(os.path.join(character, f"{character}{classification}-vb0={position_vb_hash}.txt"), "w") as f:
            f.write(vb_merged)

        ib_hash = model_data[index][0].split("=")[1].split("-")[0]
        shutil.copyfile(os.path.join(frame_dump, model_data[index][0]), os.path.join(character, f"{character}{classification}-ib={ib_hash}.txt"))
        shutil.copyfile(os.path.join(frame_dump, model_data[index][1]), os.path.join(character, f"{character}{classification}Diffuse.dds"))
        shutil.copyfile(os.path.join(frame_dump, model_data[index][2]),os.path.join(character, f"{character}{classification}LightMap.dds"))
        count += 1


    # Will need this info later to construct .ini file
    if "hash_info.json" not in os.listdir(".") or os.stat("hash_info.json").st_size == 0:
        f = open("hash_info.json", "w")
        hash_data = {}
    else:
        f = open("hash_info.json", "r+")
        hash_data = json.load(f)

    if character in hash_data:
        print("Character already exists in hash file, skipping")
        print("All operations completed, exiting")
        return

    print("Adding character hash info to hash file")
    position_vb_hash = position_vb.split("=")[1].split("-")[0]
    blend_vb_hash = blend_vb.split("=")[1].split("-")[0]
    texcoord_vb_hash = texcoord_vb.split("=")[1].split("-")[0]

    hash_data[character] = {}
    hash_data[character]["root_vs"] = root_vs_hash
    hash_data[character]["draw_vb"] = draw_vb_hash
    hash_data[character]["position_vb"] = position_vb_hash
    hash_data[character]["blend_vb"] = blend_vb_hash
    hash_data[character]["texcoord_vb"] = texcoord_vb_hash
    hash_data[character]["ib"] = ib_hash
    hash_data[character]["object_indexes"] = sorted_indexes
    hash_data[character]["first_vs"] = first_vs

    f.seek(0)
    json.dump(hash_data, f)
    f.truncate()

    print("All operations completed, exiting")


if __name__ == "__main__":
    main()
