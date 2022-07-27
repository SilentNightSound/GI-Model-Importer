# Troubleshooting 

A list of common issues and frequently asked questions for the GIMI tools.

#### Before attempting anything on this page, make sure you are using the most up-to-date versions of the plugins, character data, and programs. Most issues I see are from people using older versions of the tools.


## Installation Issues


Three most common issues are:

- Double check you have the correct Genshin game .exe location in the d3dx.ini file. Genshin has two .exe, one for the launcher and one for the game itself - you want the latter
- If the green text is not showing up, make sure you are using the Development version. The for-playing version does not have green text 
- Make sure you are running both the GIMI loader and Genshin as administrator

There is no problem if the 3dmigoto loader console window closes after the game loads, that is the intended behavior.

If you get a message like "Unable to verify if 3dmigoto successfully loaded", that does not mean the program failed to inject just that the loader cannot tell. You can close the window without issue if it appears to be working in-game (in fact, you should since leaving this window open can lead to computer slowdowns).

![image](https://user-images.githubusercontent.com/107697535/181086591-24f5be97-b6b0-4483-b694-2bc258c0d9e9.png)

3dmigoto can be run with other types of Genshin modding tools or loaders - just run the 3dmigoto loader first, then whatever other program you have after.

I have occasionally noticed an issue where 3dmigoto will fail to inject even if everything is setup correctly - in those cases, re-attempting the injection fixes the issue.


## Model Importing Issues

If you do not see anything in the folder, make sure you are loading in data from the ModelData folder and not the Mod folder (currently, loading files from Mod folders not supported). The correct folder should contain vb and ib .txt files

<img src="https://user-images.githubusercontent.com/107697535/181100111-99222d8e-c0bf-4f02-bc5d-9748435eb1fc.png" width="300"/>

### If you get this error when loading a model, you are using an outdated plugin. The old plugin only supported Blender 2.80-2.92

![image](https://user-images.githubusercontent.com/107697535/181087328-1a3769dc-ab8b-4d2d-b35c-2a42c3ea6bf8.png)

Almost all other errors are due to an issue with the model you are trying to load. Most common is 4D normals, which is due to the model dumping a component of the model and incorrectly labelling it as a normal.


## Model Exporting Issues

Before troubleshooting, double check you have done everything in the following list:

- Objects you are trying to export in the Blender scene are named ObjectHead, ObjectBody, ObjectDress and ObjectExtra, and there is only one of each (how many you have depends on how many the original model had)
- You are exporting back into the ObjectData folder the original model came from (NOT the Mod folder), and are exporting it as Object.vb. Double check the folder you are exporting to has hash.json
- You are trying to export the same number of components as the model you are replacing originally had
- None of the objects you are exporting in the scene are completely empty (need at least one face on all objects, can shrink it down to hide it)
- All of the objects have the 3dmigoto custom properties, either by merging with an object that was originally imported using the plugin or by using the custom property transfer script (https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Tools/custom_property_transfer_script.txt)
- UV maps are named TEXCOORD.xy, TEXCOORD1.xy, TEXCOORD2.xy...etc., up to the original number the model had
- The model has vertex colors, and the color component is called COLOR

Now, on to the most commonly seen issues. You can get more details on what is going wrong when exporting by opening up the console window:

<img src="https://user-images.githubusercontent.com/107697535/181120815-a4edf981-3a9c-4b7e-a4ff-971525fc51a4.png" width="600"/>

- ### This is a result of either not exporting back to the ObjectData folder, or not exporting it as Object.vb

<img src="https://user-images.githubusercontent.com/107697535/181119266-3dad9f81-e06a-483a-b8da-ad3a7749fd15.png" width="600"/>

- ### This is usually a result of incorrect naming, make sure to call it Object.vb

<img src="https://user-images.githubusercontent.com/107697535/181120923-0400c672-9fea-45b4-8200-f439680a0882.png" width="600"/>

- ### This is because a certain component has too many matching names (e.g. HuTaoBody shows up twice in the scene). Remove or rename components until only one with the name remains

![image](https://user-images.githubusercontent.com/107697535/181121033-179fefe9-db4f-49bc-a8f5-29cfa047fcd6.png)

- ### If you get this error when using the custom property transfer script, make sure you are replacing the names in blender

![image](https://user-images.githubusercontent.com/107697535/181121317-19ded6ec-0e39-430e-a476-ae3335ced1a9.png)

- ### This is because the COLOR component is missing or mis-named. Ensure vertex color exists and is named correctly

![image](https://user-images.githubusercontent.com/107697535/181121492-9d1e4bdd-7cb0-46ee-bceb-8621e92577fd.png)

- ### This one is due to the model you are using having more than 64k vertices. Either remove parts, or use decimate

![image](https://user-images.githubusercontent.com/107697535/181123500-2afc4794-e982-4d95-8a42-c4e914341d30.png)

- ### This one is because one of your objects is completely empty. Make sure to have at least one face so the UV maps can export properly

![image](https://user-images.githubusercontent.com/107697535/181129949-fb92afe5-240e-4baa-bf8e-145345d02456.png)

- ### This one is a bug from an old version of the plugin, make sure to update 

<img src="https://user-images.githubusercontent.com/107697535/181120616-55ae3885-181f-4f82-8282-c080ddccbb4b.png" width="600"/>


## In-game Model Issues

This is the trickiest part of troubleshooting - there are many, many things that can go wrong when importing a model into game. I will try and cover some of the most common categories of problems that occur

- ### Mod doesn't load at all

Ensure 3dmigoto is actually running, and that you have placed the mod in the correct Mod folder. Also make sure to press F10 in-game to reload any changed mods. Finally, if all else fails try emptying your ShaderCache and ShaderFixes folders, since sometimes those can cause issues when loading mods.

- ### Mod loads, but some parts of it are not being drawn

<img src="https://user-images.githubusercontent.com/107697535/181122972-385a6fef-e925-4f80-8469-65be168ef678.png" width="300"/>

This is due to vertex limits on the model. Anything with blend weights/vertex groups has a quirk where the vertex limits need to actually be raised in the 3dmigoto dll in order for it to work properly. I raised it for most characters, but have missed a few - still looking into methods of setting it for all objects.


- ### Large number of warnings about mod conflicts

<img src="https://user-images.githubusercontent.com/107697535/181122365-2280b266-3313-4807-b2a5-be23bf92b650.png" width="300"/>

This is caused by the game attempting to load more than one file to the same hash. This usually is a result of using two mods for the same character at the same time, but an older version of the tools also had a bug where shared face components were overwritten in multiple places.

To fix, remove any duplicate mod folders. If you are sure that you have removed them all and the warnings still show up, go into the .ini file the warning mentions and delete or comment out the lines.


- ### Mod loads, but does not show up in game/Errors when loading mod

<img src="https://user-images.githubusercontent.com/107697535/181129048-51bc2c88-3614-4490-980a-ac26308e97dd.png" width="600"/>

Unlike warnings, errors usually indicate that the program has failed to load in the mod. The cause can very, but some common ones are:

1) Incorrect names (name in .ini file does not match file in folder, like different extension)  
2) Textures have wrong format (look at original to see what format, usually dds and must have heights/widths that are powers of 2 and have integer ratios like 1024x1024, 2048x2048, 1024x2048, etc.)  
3) Did not paint/transfer any vertex groups on the new model, when the old model had vertex groups

- ### Objects load in with the wrong orientation

<img src="https://user-images.githubusercontent.com/107697535/181124642-22c9ca43-5dc7-46df-aab8-63ad20dde1ae.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181126765-89546874-3ebc-42bb-9b64-a5584a6d6154.png" width="300"/> 

This is because the object in blender imported by the 3dmigoto and the one you are replacing it with are using different coordinate spaces. Even if they seem to line up in blender, you may actually need to rotate and translate relative to the 3dmigoto model to get the correct orientation. Most commonly, rotate character models 90 degrees so they are facing upwards, then select all and apply all transforms.

Example of correct orientation between original (Kazuha) and new (Noelle)

<img src="https://user-images.githubusercontent.com/107697535/181127089-41f5ba37-5882-4666-a7e5-70814876ace5.png" width="300"/>

- ### Model is completely FUBAR

<img src="https://user-images.githubusercontent.com/107697535/181131070-f19c14d4-2e59-4bf2-8a59-a41ee45ddc24.png" width="150"/> <img src="https://user-images.githubusercontent.com/107697535/181132251-1f118616-c011-4af9-9bb3-21000ac5ba3b.png" width="150"/> <img src="https://user-images.githubusercontent.com/107697535/181132357-f7721ddc-201d-4fb6-8b3a-5d546059c224.png" width="300"/>

Very likely due to vertex group issues. The vertex group number, order and positions need to match up between the new model and the old. Confirm that all the vertex groups are there in the new model, that they are in the correct order (e.g. 4 6 7 8 5 should be 4 5 6 7 8) and that there are no gaps (e.g. 4 7 8 9 -> 4 5 6 7 8 9).

- ### Model is slightly FUBAR

<img src="https://user-images.githubusercontent.com/107697535/181132663-e1dd363a-51e3-488b-8c4c-09a35fcfc00a.png" width="150"/>" ![image](https://user-images.githubusercontent.com/107697535/181132608-84c4082c-1d0a-44c8-94ed-f06a3f62c014.png)

Still vertex group issues - double check the above, as well as ensure that the weight for the new model in that section matches up with that of the original model

- ### Incorrect textures

<img src="https://user-images.githubusercontent.com/107697535/181128459-e09c9d4a-2b04-4a5c-b338-2f46c455f0b7.png" width="300"/><img src="https://user-images.githubusercontent.com/107697535/181128502-b5587610-b61c-4b50-b60c-a73f68e89bab.png" width="100"/>

This can be due to a large variety of reasons. Most common ones are:

1) Not naming the uv map as TEXCOORD.xy  
2) Reversed normals  
3) Damaged or incorrect ObjectTexcoord.buf
4) Forgot to replace textures with new ones, so it is still loading up the old ones from the original model  

- ### Very bright/glowing textures

<img src="https://user-images.githubusercontent.com/107697535/181130063-abafbd57-c44b-409e-b502-36957a96d776.png" width="300"/>

This is most likely due to the texture map you are using having no alpha channel. Refer to the walkthroughs on this repo for details, but basically make sure you have a transparent layer on top of any texture files (the top layer is used to control emission and makes things bright, the bottom layer is used to draw the model colors and patterns).

- ### Thick or abnormal color outlines

![image](https://user-images.githubusercontent.com/107697535/181130423-54b0b03a-3f8f-4b66-99f8-36a98bca16ee.png) <img src="https://user-images.githubusercontent.com/107697535/181130493-1efae42a-2a48-4e69-807e-7865776fda9b.png" width="150"/> 

This is due to an incorrect vertex COLOR value. Two methods to fix: 
1) Copy over the COLOR data from a part of the model that has correct outlines on the original (see https://youtu.be/z2nvJzkwHHQ?t=4753 for details)
2) Remove the outlines by using this script: https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Tools/genshin_remove_outlines.py


- ### Other issues

You probably won't come across any of these in normal use, but I just want to show off my collection of cursed images

Incorrect strides in .ini file

<img src="https://user-images.githubusercontent.com/107697535/181133398-29294888-5c86-4477-9627-de6e11814e0e.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181133297-6ffdc6ba-df60-403d-be09-95f2ab62f889.png" width="300"/>

Mismatched IB and VB

<img src="https://user-images.githubusercontent.com/107697535/181133473-a3ee5ff1-f138-4b0a-aa03-3cad5b592a0e.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181133485-372ddb47-9de6-4506-957c-017ed524737e.png" width="300"/>

Overriding on VB instead of IB

<img src="https://user-images.githubusercontent.com/107697535/181133582-ca88149a-8a9b-4838-a9f0-9e9008a55fe7.png" width="300"/>

## Model Dumping Issues

Section coming soon, the model dumping script is still experimental.
