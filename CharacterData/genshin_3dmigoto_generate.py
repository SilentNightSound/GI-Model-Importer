# Author: SilentNightSound#7430
# Splits the output of the 3dmigoto blender plugin into the required buffers, along with generating
# the required .ini file for performing the override

import os
import argparse
import struct
import shutil
import json

def main():
    parser = argparse.ArgumentParser(description="Splits blender 3dmigoto output into required buffers")
    parser.add_argument("-n", "--name", type=str, help="Name of character to use in folders and output files")
    parser.add_argument("--hashfile", type=str, default="hash_info.json", help="Name of hash info file")
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
    with open(os.path.join(args.name, f"{args.name}Head.fmt"), "r") as f:
        headers = f.read()
        if "stride: 84" in headers:
            extra_flag = False
        else:
            extra_flag = True

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
    ini_data += f"[Resource{args.name}HeadDiffuse]\nfilename = {args.name}HeadDiffuse.dds\n\n"
    ini_data += f"[Resource{args.name}HeadLightMap]\nfilename = {args.name}HeadLightMap.dds\n\n"
    ini_data += f"[Resource{args.name}BodyDiffuse]\nfilename = {args.name}BodyDiffuse.dds\n\n"
    ini_data += f"[Resource{args.name}BodyLightMap]\nfilename = {args.name}BodyLightMap.dds\n\n"
    if extra_flag:
        ini_data += f"[Resource{args.name}ExtraDiffuse]\nfilename = {args.name}ExtraDiffuse.dds\n\n"
        ini_data += f"[Resource{args.name}ExtraLightMap]\nfilename = {args.name}ExtraLightMap.dds\n\n"

    with open(os.path.join(f"{args.name}Mod", f"{args.name}.ini"), "w") as f:
        print("Writing ini file")
        f.write(ini_data)

    print("All operations completed, exiting")



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


if __name__ == "__main__":
    main()
