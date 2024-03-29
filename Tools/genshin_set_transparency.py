# Author: HazrateGolabi#1364
# Special Thanks:
#   HummyR#8131: (For doing the actual research to make this transparency possible)
#   SilentNightSound#7430: (For GIMI and letting me to learn(steal) from his code)

# -b for body, -hd for head, -d for dress, -e for extra, -t for R G B blen factors

import os
import argparse

OpaquParts = ["Head","Body", "Dress", "Extra"]
transPart = ''

def findempty(file, lineNumber):
    for i in range (lineNumber,len(file)):
        #if str.strip(file[i]) == '':
        if file[i].strip() == '':
            return i

# Collect the ini
def collect_ini(path):
    print("Finding the ini")
    ini_file = ''
    ini_file = [x for x in os.listdir(".") if ".ini" in x and "DISABLED" not in x]
    if len(ini_file) != 1:
        print("ERROR: Unable to find *.ini file. Ensure it is in the folder, and only one *.ini file exists")
        return
    ini_file = ini_file[0]
    return ini_file

# Diabling the OLD ini
def dis_ini(file):
    print("Cleaning up old ini")
    os.rename(file, os.path.join(os.path.dirname(file), "DISABLED") + os.path.basename(file))

# doing the deed
def main():
    RChannel, GChannel, BChannel = 0.5, 0.5, 0.5
    newIni =''

    parser = argparse.ArgumentParser(description="Generates a mod with transparency effect")
    parser.add_argument("-b", "--body", action="store_true", help="Body turns transparent")
    parser.add_argument("-hd", "--head", action="store_true", help="Head turns transparent")
    parser.add_argument("-d", "--dress", action="store_true", help="Dress turns transparent")
    parser.add_argument("-e", "--extra", action="store_true", help="Extra turns transparent")
    parser.add_argument("-t", "--tfactor", type=float, help="Opacity of the RGB. with spaces between R G B", nargs=3)

    args = parser.parse_args()
    exit_Flag = True

    print("\nHello there.\nTransparency script, config by HummyR\nOnce again thanking silent for GIMI")
    if args.body:
        print("You have chosen the body to become transparent")
        transPart = "Body"
        exit_Flag = False
    if args.head:
        print("You have chosen the head to become transparent")
        transPart = "Head"
        exit_Flag = False
    if args.dress:
        print("You have chosen the dress to become transparent")
        transPart = "Dress"
        exit_Flag = False
    if args.extra:
        print("You have chosen the extra to become transparent")
        transPart = "Extra"
        exit_Flag = False
    if args.tfactor:
        RChannel = args.tfactor[0]
        GChannel = args.tfactor[1]
        BChannel = args.tfactor[2]
    
    if exit_Flag:
        print("no parts chosen, EXITING")
        return
        

    #tranparnecy Command Block
    transCommand = f'[CustomShaderTransparency]\nblend = ADD BLEND_FACTOR INV_BLEND_FACTOR\nblend_factor[0] = {RChannel}\nblend_factor[1] = {GChannel}\nblend_factor[2] = {BChannel}\nblend_factor[3] = 1\nhandling = skip\ndrawindexed = auto'

    print("Transparenting the chosen part")
    ini_file = collect_ini(".")
    if ini_file == None: #no ini, ABORTING
        return
    #Parsing ini sections
    print("Parsing ini sections")
    with open(ini_file, "r", encoding="utf-8") as f:
        fc = f.readlines()
        i = 0
        flag_firstAuto = True
        while True:
            if fc[i].find("drawindexed = auto") != -1 and flag_firstAuto:
                i += 1
                flag_firstAuto = False
                continue
            if "[TextureOverride" in fc[i]:
                if f'{OpaquParts[0]}]' in fc[i] or f'{OpaquParts[1]}]' in fc[i] or f'{OpaquParts[2]}]' in fc[i] or f'{OpaquParts[3]}]' in fc[i]:
                    if transPart not in fc[i]:
                        blockEnd = findempty(fc, i)
                        fc.insert(blockEnd, "drawindexed = auto")
                        fc.insert(blockEnd+1, '\n') 
                    elif transPart in fc[i]:
                        blockEnd = findempty(fc, i)
                        fc.insert(blockEnd, "run = CustomShaderTransparency")
                        fc.insert(blockEnd+1, '\n')
                        
            if "; .ini generated by GIMI (Genshin-Impact-Model-Importer)" in fc[i]:
                newIni += transCommand
                newIni += f'\n\n; .ini generated by GIMI (Genshin-Impact-Model-Importer)\n; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord'
                break

            newIni += fc[i]
            i += 1
        f.close()
    # Disabling the OLD ini and writing the new one
    dis_ini(ini_file)
    with open(ini_file, "w", encoding="utf-8") as f:
        f.write(newIni)


if __name__ == "__main__":
    main()
