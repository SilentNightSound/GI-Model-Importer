EN | [中文](CN_README.md)

# GI-Model-Importer
Tools and instructions on how to import custom models into Genshin Impact

#### **DISCLAIMER: Using this on official Genshin servers is very likely to get you banned. I do not recommend or condone the use of these scripts and programs on official servers, and if you do use it on official servers I take no responsibility for any consequences as a result.**

Feel free to use or modify the scripts as you wish, though please give credit if you use these programs in your projects. I am continuing to update this program/page with new features and fixes, so check back often.

For a simple walkthrough of removing a portion of a character mesh using these tools, see [Mona Walkthrough](Guides/MonaWalkthrough.md). For a more advanced example of importing a custom model, see Cybertron's great video walkthrough: https://www.youtube.com/watch?v=7ijMOjhEvBw

Model files for the importer are located at https://github.com/SilentNightSound/GI-Model-Importer-Assets

## Installation Instructions (3DMigoto)

(Note: SpecialK and 3DMigoto both use the same .dll file and perform similar functions, so it they cannot be run together. Melon and 3DMigoto are able to run together.)

1. Download 3dmigoto.zip from this repository and extract it. I have provided two versions:
   - "3dmigoto (for development).zip" is a development version intended for creating mods which has all features turned on (including the green text at the top and bottom of the screen) but is slower
   - "3dmigoto (for playing mods).zip" is a version of the program with most development features turned off and is faster (no green text), intended for releasing and playing mods

2. Depending on the location of your Genshin Impact .exe file, you may need to change this line in the d3dx.ini file to point to your own installation (the Genshin game .exe, not the Genshin launcher.exe):

<img src="https://user-images.githubusercontent.com/107697535/174322200-b1afea95-53f5-4add-be89-698f85503908.png" width="800"/>

3. Double click "3DMigoto Loader.exe" to start the loader, then start up Genshin through the GenshinImpact.exe (again, through the Genshin game .exe not the launcher.exe). If everything is correct so far, 3DMigoto should be injected into the game and you should see a green text overlay (only if using the development version, the "for playing" version does not show the green text):

![image](https://user-images.githubusercontent.com/107697535/174324967-049b9879-c537-4bd0-b190-4ad7444fb8f1.png)

<img src="https://user-images.githubusercontent.com/107697535/174325193-1f58ab2c-86f8-4ce9-8697-6e7d140b2014.png" width="800"/>

   - Note: some people have reported an issue where the loader lists that it was unable to verify if 3dmigoto was loaded. This does not mean that 3dmigoto failed to inject - if the green text and mods show up, there are no issues and you can close the command prompt

![image](https://user-images.githubusercontent.com/107697535/175563985-1e7d1298-08d0-4334-b6e8-c69769e3877a.png)

4. Installation complete! You should now be able to load custom resources and override textures and shaders with 3DMigoto. To add mods, place them in the Mods folder (one mod per character at a time) and press F10 to load them in game:

![image](https://user-images.githubusercontent.com/107697535/175611402-c3f600ca-4136-4561-b33a-f4edf6153d1a.png)



&nbsp;
## Installation Instructions (3DMigoto Blender Plugin)

In order to modify game models, you need to also setup your Blender plugins and environment. The 3DMigoto plugin works with Blender 2.80-2.92

1. Download and install [Blender](https://download.blender.org/release/Blender2.92/)
   - Version 2.93 and above will fail to import files with the message `TypeError: '_PropertyDeferred' object is not iterable`

2. Download and install the modified [3DMigoto plugin](Tools/blender_3dmigoto.py). You can install an add-on in Blender by going to Edit -> Preferences -> Add-Ons -> Install, then selecting the .py file. 

3. If done correctly, you should see 3DMigoto in the plugin list as well as new options in the import and export menus

<img src="https://user-images.githubusercontent.com/107697535/174328624-ccb14ded-57b2-4ac7-b0a0-0de118119174.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174329025-981a1a9f-7c56-4f44-804b-1b0394b8bd33.png" width="800"/>

&nbsp;
## Usage Instructions

See [Usage Instructions](Guides/UsageInstructions.md)
