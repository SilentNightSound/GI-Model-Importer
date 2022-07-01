# Author: SilentNightSound#7430
# Forcibly sets the COLOR of a texcoord output to a certain value
# Use if having outline issues around the character rims

import os
import argparse
import struct
import shutil
import json
import math

def main():
    parser = argparse.ArgumentParser(description="Splits blender 3dmigoto output into required buffers")
    parser.add_argument("-n", "--name", type=str, help="Name of character to use in folders and output files")
    parser.add_argument("-r", type=int, default=None, help="R color value")
    parser.add_argument("-g", type=int, default=None, help="G color value")
    parser.add_argument("-b", type=int, default=None, help="B color value")
    parser.add_argument("-a", type=int, default=None, help="A color value (controls outline thickness)")
    parser.add_argument("--stride", type=int, help="Width in bytes of data for one vertex")

    args = parser.parse_args()

    if args.name not in os.listdir("."):
        print(f"ERROR: Cannot find {args.name}. Please ensure it is in the same folder. Exiting")
        return

    if args.r != None and (args.r < 0 or args.r > 255):
        print("ERROR: R value must be between 0 and 255")
    if args.g != None and (args.g < 0 or args.g > 255):
        print("ERROR: G value must be between 0 and 255")
    if args.b != None and (args.b < 0 or args.b > 255):
        print("ERROR: B value must be between 0 and 255")
    if args.a != None and (args.a < 0 or args.a > 255):
        print("ERROR: A value must be between 0 and 255")


    with open(args.name, "rb") as f, open(f"{os.path.splitext(args.name)[0]}Modified.buf", "wb") as g:
        print("Setting COLOR values")
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            if args.r != None:
                data[i]   = args.r
            if args.g != None:
                data[i+1] = args.g
            if args.b != None:
                data[i+2] = args.b
            if args.a != None:
                data[i+3] = args.a
            i += args.stride

        print("Writing results to new file")
        g.write(data)

    print("All operations complete, exiting")


if __name__ == "__main__":
    main()
