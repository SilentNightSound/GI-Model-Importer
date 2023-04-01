# Author: SilentNightSound#7430
# Flips between the global and CN versions for censored characters (Mona, Jean, Amber, Rosaria)
# Note that these are for the recent costumes (e.g. post 2.4) - this does not swap to the older versions
#   like pre 1.4 Rosaria or interim versions like Jorts Mona)

import os
import struct
import json


def main():

    print("\nGlobal/CN Costume Model Flip\n")
    print("Converts mods for the global costumes to the CN costumes and vice-versa for Mona, Jean, Amber and Rosaria\n")
    print("Running the program will flip from one to the other, and running again will flip it back")

    print("This program will work on ini found in the current directory and all subdirectories")
    print("It will also ignore any ini that has DISABLED in the name")
    print("Please ensure that any mods you are swapping only contains a single .ini and a single Blend.buf\n")

    # Only characters that have a remapping are valid
    with open("remap.json", "r", encoding="utf8") as f:
        remap_data = json.load(f)

    # I originally had a fancier structure for the json, but I realized a big file containing all the characters gave
    #   basically all the required data
    with open("all_hash_data.json", "r", encoding="utf8") as f:
        char_data = json.load(f)
        char_hashes = {}
        # Minor issue - the json file doesn't specify which index is main body and which is face/other components
        # It is set to default to 0 for main in collect and 100% of dumps are organized this way but something to note
        for char in char_data:
            char_hashes[char_data[char][0]["draw_vb"]] = char

    # Generalized to all subdir so it works on merged mods
    for root, dirs, files in os.walk("."):

        # Searching and sanity checks
        ini_files = [file for file in files if os.path.splitext(file)[1] == ".ini" and "DISABLED" not in file]
        if len(ini_files) != 1:
            continue
        ini_file = ini_files[0]
        print(f"Found {root}\\{ini_file}")

        blend_files = [file for file in files if os.path.splitext(file)[1] == ".buf" and "Blend.buf" in file]
        if len(ini_files) != 1:
            print("\tUnable to find corresponding blend file, skipping\n")
            continue
        blend_file = blend_files[0]
        print(f"Found {root}\\{blend_file}")

        with open(os.path.join(root, ini_file), "r", encoding="utf-8") as f:
            ini_data = f.read()

        source_char, target_char, vg_remap = identify_characters(char_hashes, remap_data, ini_data)
        if not source_char:
            continue

        with open(os.path.join(root, blend_file), "rb") as f:
            blend_data = f.read()

        if len(blend_data) % 32 != 0:
            print("ERROR: Blend file format not recognized")
            return

        # By this point we should be in a valid mod folder that has a remap and have chosen a character to remap to
        remapped_blend = remap(blend_data, vg_remap)

        print("Correcting ini file")
        hash_types = ["draw_vb", "position_vb", "blend_vb", "texcoord_vb", "ib"]
        for hash_type in hash_types:
            source_buffer_hash = char_data[source_char][0][hash_type]
            target_buffer_hash = char_data[target_char][0][hash_type]
            ini_data = ini_data.replace(source_buffer_hash, target_buffer_hash)

        # Format is slightly different for textures
        # This isn't 100% accurate since it uses position instead of texture type (more reliable than name however),
        #   but for this specific script it is enough
        for i in range(len(char_data[source_char][0]["texture_hashes"])):
            for j in range(len(char_data[source_char][0]["texture_hashes"][i])):
                source_texture_hash = char_data[source_char][0]["texture_hashes"][i][j][2]
                target_texture_hash = char_data[target_char][0]["texture_hashes"][i][j][2]
                ini_data = ini_data.replace(source_texture_hash, target_texture_hash)

        # Special case for face textures
        if len(char_data[source_char]) > 1 and char_data[source_char][1]["component_name"] == "Face" and \
            len(char_data[target_char]) > 1 and char_data[target_char][1]["component_name"]  == "Face":
            source_face_texture_hash = char_data[source_char][1]["texture_hashes"][0][1][2]
            target_face_texture_hash = char_data[target_char][1]["texture_hashes"][0][1][2]
            ini_data = ini_data.replace(source_face_texture_hash, target_face_texture_hash)
        print("Ini file correction complete")

        # Correct indices
        # Only needed for Rosaria lol
        for i in range(len(char_data[source_char][0]["object_indexes"])):
            if char_data[source_char][0]["object_indexes"][i] != char_data[target_char][0]["object_indexes"][i]:
                # Technically this isn't 100% accurate since first_index could potentially be the same between objects,
                #   but the chances of that happening are very very low
                ini_data = ini_data.replace(f'match_first_index = {char_data[source_char][0]["object_indexes"][i]}',
                                 f'match_first_index = {char_data[target_char][0]["object_indexes"][i]}')

        # Finally, save results
        # No backups, we balling
        print("Saving results")
        with open(os.path.join(root, ini_file), "w", encoding="utf-8") as f:
            f.write(ini_data)

        with open(os.path.join(root, blend_file), "wb") as f:
            f.write(remapped_blend)
        print(f"Transfer complete, mod has been remapped to {target_char}\n\n")

    print("All operations complete, exiting")


# Identify source and target characters
def identify_characters(char_hashes, remap_data, ini_data):
    for source_char_hash in char_hashes:
        if source_char_hash in ini_data:
            source_char = char_hashes[source_char_hash]
            if source_char in remap_data:
                choices = [x for x in remap_data[source_char]]
                print(f"Mod identified as {source_char}, remapping exists for {choices}")
                # TODO: implement choice here
                target_char = choices[0]
                vg_remap = remap_data[source_char][target_char]
                return source_char, target_char, vg_remap
            else:
                print(f"Mod identified as {source_char} but no remapping available. Skipping\n\n")
                return "", "", []

    print("Unable to identify mod, skipping")
    return "", "", []

# Remap the VG groups in the blend file
def remap(blend_data, vg_remap):
    print("Beginning Remap")
    remapped_blend = bytearray()
    for i in range(0, len(blend_data), 32):
        blendweights = [struct.unpack("<f", blend_data[i + 4 * j:i + 4 * (j + 1)])[0] for j in range(4)]
        blendindices = [struct.unpack("<I", blend_data[i + 16 + 4 * j:i + 16 + 4 * (j + 1)])[0] for j in range(4)]
        outputweights = bytearray()
        outputindices = bytearray()
        for weight, index in zip(blendweights, blendindices):
            if weight != 0:
                index = int(vg_remap[index])
            outputweights += struct.pack("<f", weight)
            outputindices += struct.pack("<I", index)
        remapped_blend += outputweights
        remapped_blend += outputindices
    print("Remap Complete")
    return remapped_blend

if __name__ == "__main__":
    main()

