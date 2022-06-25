## Mona Hat Removal Walkthrough

This is a walkthrough that goes through the process of deleting an object (Mona's hat) from the character mesh from start to finish.

Prior to 3Dmigoto, there was no way to cleanly remove her hat - it does not have a unique shader, so it cannot be removed in Special K; it is not a unique object in the unity object hierarchy so it cannot be removed using Melon; and the bones that are attached to it are also connected to Mona's hair meaning any attempt to change the bone structure would result in damaging Mona's hair as well.

These instructions can be generally applied to remove any part of the mesh, though in some cases there will be a hole in the model underneath (especially for larger objects) - a walkthrough on how to patch mesh holes will come later.

1. Ensure 3DMigoto and the 3DMigoto Blender plugin are installed (see [README](../README.md) on main github page)
2. Download the Mona character files from the CharacterData folder of this repo. Your folder structure should look like this:

<img src="https://user-images.githubusercontent.com/107697535/174457855-299ecb18-70d8-4ade-ae06-c178ab0b8779.png" width="800"/>

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

8. A MonaMod folder should now be generated right next to the original character folder that looks like this:

<img src="https://user-images.githubusercontent.com/107697535/174458059-363b1c56-ea76-4a01-9e1f-6e22f3b0949f.png" width="800"/>

   - (Note: another way to generate the Mod folder is to export each component separately as MonaHead and MonaBody with the 3DMigoto raw buffers option, then use the genshin_3dmigoto_generate.py script with `python .\genshin_3dmigoto_generate.py -n "Mona"`)

9. Copy the MonaMod folder into the 3DMigoto Mods folder created during setup:

<img src="https://user-images.githubusercontent.com/107697535/174458172-01751459-13a5-4e11-9827-f039dc762066.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458178-e09637de-7149-463e-bd7a-499e986cba1d.png" width="800"/>

10. Press "F10" in Genshin to reload all .ini files and apply the mod. If everything has gone according to plan, your Mona will now be hatless!

<img src="https://user-images.githubusercontent.com/107697535/174458194-426f8602-31d5-416a-96ed-d58ecdcee39d.png" width="800"/>

We can do a bit more to improve this. Notices that Mona's hair is discolored where the hat used to be - this is controlled by her head's lightmap texture. The character folder includes this file as MonaHeadLightMap.dds, and we can modify it to improve the result further.

11. Opening MonaHeadLightMap.dds in Paint.net with the dds plugin installed and removing the alpha layer, we can see that portions of Mona's hair texture are covered in shadow

<img src="https://user-images.githubusercontent.com/107697535/174458242-75283d3c-72d5-4043-b75d-6273dce32671.png" width="800"/>

12. We can smooth out and standardize the colors and re-apply the alpha layer:

<img src="https://user-images.githubusercontent.com/107697535/174458258-1c92a244-40e9-45c5-9a50-da3bfaa2bca4.png" width="800"/>

13. Finally, we can replace the MonaHeadLightMap.dds that the mod is currently using either by directly overwriting it in the MonaMod folder or putting it back in the Mona character folder and recreating the mod folder again (the plugin will pull the texture .dds from the character folder every time it runs)

<img src="https://user-images.githubusercontent.com/107697535/174458283-1bec92ab-5008-4ae6-a6f8-110d7a0dee49.png" width="800"/>

