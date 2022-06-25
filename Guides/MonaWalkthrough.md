EN | [中文](CN_MonaWalkthrough.md)

## Mona Hat Removal Walkthrough

This is a walkthrough that goes through the process of deleting an object (Mona's hat) from the character mesh from start to finish.

Prior to 3Dmigoto, there was no way to cleanly remove her hat - it does not have a unique shader, so it cannot be removed in Special K; it is not a unique object in the unity object hierarchy so it cannot be removed using Melon; and the bones that are attached to it are also connected to Mona's hair meaning any attempt to change the bone structure would result in damaging Mona's hair as well.

These instructions can be generally applied to remove any part of the mesh, though in some cases there will be a hole in the model underneath (especially for larger objects) - a walkthrough on how to patch mesh holes will come later.

1. Ensure 3DMigoto and the 3DMigoto Blender plugin are installed (see [README](../README.md) on main github page)
2. Download the Mona character files and hash_info.json from the CharacterData folder of this repo. Your folder should look like this:

<img src="https://user-images.githubusercontent.com/107697535/175789338-b187f6c6-2d6d-4a97-beb2-6cccdd556e2d.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174457572-77532f14-02ab-4bfb-904d-fe2ad251d84a.png" width="800"/>

3. We are now going to load the model into Blender. Under File->Import there is an option to import 3DMigoto Frame Analysis Dumps. If you do not see this option, ensure the 3DMigoto plugin is installed and activated

<img src="https://user-images.githubusercontent.com/107697535/174457627-5b52357a-0983-4dd5-bf64-301ada192a07.png" width="800"/>

4. Navigate to the character folder and select all the .txt files. Leave all settings as default and press import.

<img src="https://user-images.githubusercontent.com/107697535/174457693-c5fa6ef1-799a-471a-ba2d-7ecc55decc8f.png" width="800"/>

5. If everything has been setup correctly, you should see Mona's model imported into the viewport. It consists of two objects, the head and body

<img src="https://user-images.githubusercontent.com/107697535/174457712-3499f864-50cb-4b18-b01e-bf88a5d8fd5e.png" width="800"/>

6. We want to remove the hat, so select the head mesh and enter edit mode. Highlight all the vertices of the hat, then delete them

<img src="https://user-images.githubusercontent.com/107697535/174457736-387f6a53-1d33-4a5b-88c5-972d52e05304.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174457765-c59e3e10-0187-4578-9b0b-21dd47d316e7.png" width="800"/>

7. Now that Mona is hatless, we want to export the models. Ensure that there is a single object named "MonaHead" and one that named "MonaBody" (and optionally one named "CharExtra" for characters that have a third part - Mona only has two). The option to export is under File->Export->Exports Genshin Mod folder. Navigate to the character folder you loaded the original data from, and export the model as "Mona.vb"

<img src="https://user-images.githubusercontent.com/107697535/175569818-4d150043-555c-41a7-90ca-3d0e05c1c3f5.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/175570101-9717b9eb-7ef9-4e1c-82e2-f6871497f5f6.png" width="800"/>

8. A MonaMod folder should now be generated right next to the original character folder that looks like this (if the mod folder does not generate, double check you have hash_info.json):

<img src="https://user-images.githubusercontent.com/107697535/174458059-363b1c56-ea76-4a01-9e1f-6e22f3b0949f.png" width="800"/>

   - (Note: another way to generate the Mod folder is to export each component separately as MonaHead and MonaBody with the 3DMigoto raw buffers option, then use the genshin_3dmigoto_generate.py script with `python .\genshin_3dmigoto_generate.py -n "Mona"`)

9. Copy the MonaMod folder into the 3DMigoto Mods folder created during setup:

<img src="https://user-images.githubusercontent.com/107697535/174458172-01751459-13a5-4e11-9827-f039dc762066.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458178-e09637de-7149-463e-bd7a-499e986cba1d.png" width="800"/>

10. Press "F10" in Genshin to reload all .ini files and apply the mod. If everything has gone according to plan, your Mona will now be hatless!

<img src="https://user-images.githubusercontent.com/107697535/174458194-426f8602-31d5-416a-96ed-d58ecdcee39d.png" width="800"/>

We can do a bit more to improve this. Notices that Mona's hair is discolored where the hat used to be - this is controlled by her head's lightmap texture. The character folder includes this file as MonaHeadLightMap.dds, and we can modify it to improve the result further.

11. In order to edit the dds textures, we use Paint.net with the DDS extension (https://forums.getpaint.net/topic/111731-dds-filetype-plus-04-11-2022/) and any extension that allows us to edit the alpha layer (https://forums.getpaint.net/topic/1854-alpha-mask-import-plugin-20/ or https://forums.getpaint.net/topic/110805-modify-channels-v111-2022-03-07/ - I will use the former in this walkthrough, and for an example with the latter see https://github.com/zeroruka/GI_Assets/wiki/Creating-Skins)

12. Opening MonaHeadLightMap.dds, we can remove the alpha layer by clicking on Effects->Alpha Mask and making sure all options are unselected and pressing OK:

<img src="https://user-images.githubusercontent.com/107697535/175790813-24c1e522-41d1-42f5-a661-f25f7787dd4a.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/175790898-f26b3f1d-6ed2-4f71-b186-c94ddf44174b.png" width="800"/>

13. We can now see that portions of Mona's hair texture are darker. We can smooth these out in order to remove the shadows from Mona's hair:

<img src="https://user-images.githubusercontent.com/107697535/174458242-75283d3c-72d5-4043-b75d-6273dce32671.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458258-1c92a244-40e9-45c5-9a50-da3bfaa2bca4.png" width="800"/>

14. We can then re-apply the alpha layer by clicking on Effects->Alpha Mask with the entire image selected and checking the "Invert Mask" option:

<img src="https://user-images.githubusercontent.com/107697535/175790958-5530e001-655b-4966-9e03-23be7dd93c7d.png" width="800"/>

   - Note: A small amount of information related to emissions and blush has been lost compared to the original because we are inverting the alpha channel of the entire image - if you want to keep emission effects when re-applying, see https://www.youtube.com/watch?v=1y8oZ1TFZtg for an example of using masks to selectively apply the inversion to only parts of the image (tutorial is for Special K, but 3dmigoto functions the same)

15. Export the image by saving as a .dds, making sure to use "BC7 (Linear, DX 11+)" and setting Generate Mip Maps (Note: Lightmaps use BC7 Linear when exporting, Diffuse maps use BC7 SRGB)

<img src="https://user-images.githubusercontent.com/107697535/175790979-3f20d159-0eec-4fc0-947d-0cd6b02c95c9.png" width="800"/>

16. Finally, we can replace the MonaHeadLightMap.dds that the mod is currently using either by directly overwriting it in the MonaMod folder or putting it back in the Mona character folder and recreating the mod folder again (the plugin will pull the texture .dds from the character folder every time it runs)

<img src="https://user-images.githubusercontent.com/107697535/174458283-1bec92ab-5008-4ae6-a6f8-110d7a0dee49.png" width="800"/>

