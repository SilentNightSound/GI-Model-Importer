# GI-Model-Importer
Scripts and instructions on how to override models for Genshin Impact

#### **DISCLAIMER: Using this on official Genshin servers is very likely to get you banned. I do not recommend or condone the use of these scripts and programs on official servers, and if you do use it on official servers I take no responsibility for any consequences as a result.**
&nbsp;

This repo explains various methods of modifying meshes in Genshin Impact using 3Dmigoto. Unlike SpecialK which is limited to texture modifications, 3dMigoto allows you to override both model and texture data.

## Installation Instructions (3DMigoto)

(Note: SpecialK and 3DMigoto both use the same .dll file and perform similar functions, so it is unlikely that they can run simultaneously. It might be possible by chaining the .dlls together, but 3Dmigoto can do everything SpecialK can so running both together is not required for any mods. Melon and 3DMigoto are able to run together.)

1. Grab the latest version of 3dMigoto from https://github.com/bo3b/3Dmigoto/releases/download/1.3.16/3Dmigoto-1.3.16.zip (3Dmigoto-1.3.16.zip is the latest as of the time of writing, NOT 1.3.8)
2. Extract the zip file, and copy the contents of the "x64" directory into the "loader\x64" directory. 
3. Create a folder called "Mods". Your final directory structure should look like this:

<img src="https://user-images.githubusercontent.com/107697535/174320467-f5bd5969-86c7-45ae-ad07-d554aa6cc70e.png" width="800"/>

4. Download the d3dx.ini and d3d11.dll from this repository and override the oned in "loader\x64"
5. Depending on the location of your Genshin Impact .exe file, you may need to change this line in the d3dx.ini file to point to your own installation (the game .exe, not the launcher.exe):

<img src="https://user-images.githubusercontent.com/107697535/174322200-b1afea95-53f5-4add-be89-698f85503908.png" width="800"/>

6. Double click "3DMigoto Loader.exe" to start the loader, then start up Genshin through the GenshinImpact.exe (again, through the game .exe not the launcher.exe). If everything is correct so far, 3Dmigoto should be injected into the game and you should see a green text overlay:

![image](https://user-images.githubusercontent.com/107697535/174324967-049b9879-c537-4bd0-b190-4ad7444fb8f1.png)

<img src="https://user-images.githubusercontent.com/107697535/174325193-1f58ab2c-86f8-4ce9-8697-6e7d140b2014.png" width="800"/>

7. Installation complete! You should now be able to load custom resources and override textures and shaders with 3DMigoto.

&nbsp;
## Installation Instructions (3DMigoto Blender Plugin)

In order to modify game models, you need to also setup your Blender plugins and environment. The 3DMigoto plugin works with Blender 2.80-2.92 (confirmed that plugin fails on v2.93 and higher)

1. Download and install Blender (https://download.blender.org/release/Blender2.92/)
   - Version 2.93 and above will fail to import files with the message `TypeError: '_PropertyDeferred' object is not iterable`
2. Download and install the 3DMigoto plugin from https://github.com/SilentNightSound/GI-Model-Importer/blob/main/blender_3dmigoto.py. You can install an add-on in Blender by going to Edit -> Preferences -> Add-Ons -> Install, then selecting the .py file. 
3. If done correctly, you should see 3DMigoto in the plugin list as well as new options in the import and export menus

<img src="https://user-images.githubusercontent.com/107697535/174328624-ccb14ded-57b2-4ac7-b0a0-0de118119174.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174329025-981a1a9f-7c56-4f44-804b-1b0394b8bd33.png" width="800"/>

&nbsp;
## Usage Instructions

See https://github.com/SilentNightSound/GI-Model-Importer/blob/main/UsageInstructions.md
