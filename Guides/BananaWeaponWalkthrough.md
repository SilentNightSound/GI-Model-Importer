## Custom Weapon Import Walkthrough

This is a walkthrough for importing custom weapon models into Genshin Impact.

For this tutorial, I am assuming you are familiar with the basics of using GIMI (how to set it up/import/export/load); if not, please read through [Mona Hat Removal](Guides/MonaWalkthrough.md). I am also assuming basic Blender knowledge – for questions on Blender basics like how to change modes, select vertices and open certain menus please search the knowledge you need on Google/Youtube.

Weapon mods are more complicated than basic mesh edits, but less complicated than importing custom characters. ~90% of the steps remain the same for custom characters, but characters involve much more complicated vertex group/bone structures. 

I will be demonstrating three different weapon models, ordered by complexity. Generally speaking, for weapons the order of difficulty from easiest to hardest is Swords/Spears/Claymores without tassels → Swords/Spears/Claymores with tassels → Bows → Catalysts. Each weapon builds on the last in terms of complexity, so please read through in order. 

I will be using [this]( https://sketchfab.com/3d-models/banana-6d99c6c1a8bc4b3e97cebbc49d62115d) model of a Banana for all three mods (credits to Marc Ed).

First model: Banana Blade ([jump to section](#banana-blade))
Second model: Bownana
Third model: Ripe Catalyst

## Banana Blade

Let’s start with the one of the simplest types of weapons, a claymore without tassels - I am going to be replacing Serpent Spine with a giant banana

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231401-711a0bd9-b89a-4a54-aa55-9f35c12ac966.png" width="800"/>
</p>

1.	Start by importing Serpent Spine 3dmigoto data from the GI-Model-Importer-Asset Repo

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231676-a73470a7-0cc4-4977-a17a-0ba1165485a8.png" width="600"/>
</p>

2.	As a sanity check to make sure we are in the simplest category of weapons, check to make sure the weapon does not have any vertex groups. If it does, you can continue to follow along but you will need to also refer to the next two sections on how to handle the groups

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231678-1cd4d30b-274a-4a13-8deb-8da7b7ca5cf4.png" width="600"/>
</p>

3.	Import the banana using File→Import→FBX. I chose a simple model with only a single texture and component on purpose to demonstrate how the process works – more complicated models may require you to merge multiple textures and components together, and requires more advanced Blender knowledge

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231693-6007de52-ecdb-4fb7-8301-07af38e1f336.png" width="400"/> <img src="https://user-images.githubusercontent.com/107697535/183231698-8e0ab1e3-e07e-4fd3-bdc8-c31d8b2c1b05.png" width="400"/>
</p>

4.	As you can tell, the banana model and sword models are misaligned in both location and size. Translate, rotate and scale the banana until the two models overlap. The most important parts to consider are the hilts (since that is where the character will be holding the weapon) and to make sure the new weapon isn’t significantly larger/smaller than the old one (since you can potentially end up with clipping or misalignment with the actual hitbox).

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231783-eb1f397a-c017-4398-950f-15a9d8dc66c9.png" width="600"/>
</p>

5.	While this will work, we really want the models to overlap a little bit more so it actually matches up closer with the movement of the sword – we can turn on proportional editing and drag and rotate the tip of the banana to straighten it out a bit to improve the result

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231793-4f6c5365-8b45-4cb8-9543-8256a1440b25.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231811-c4b37248-dae3-42e2-9865-6554e41931da.png" width="410"/><img src="https://user-images.githubusercontent.com/107697535/183231814-55c7de2d-1d01-46c2-9da1-0deb9e5b108f.png" width="400"/>
</p>

Note that for these types of weapons, the new object does not need to overlap exactly with the old one.

6.	Now, we need add the custom 3dmigoto properties on to the new object. There are two ways to do this – you could delete all the vertices of the old model then merge the new one into it, or you could use the [custom properties transfer script](Tools/custom_property_transfer_script.txt). I’m going to use the latter method in this tutorial
7.	Open up the scripting tab, and copy the transfer script into the text box. Replace “transfer_to” and “transfer_from” with the objects you are transferring to (new object) and from (original 3dmigoto object) respectively

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231886-b906ae94-d311-48eb-bd5d-7e238f1d4dd7.png" width="1000"/>
</p>

8.	Double check the properties show up in the Custom Properties section of the new object

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231907-d9c8dd16-f9b5-4806-8671-f211f865d783.png" width="400"/>
</p>

9.	Now, we need to make sure that the new objects UV maps and color data will be exported correctly. Use the original object as a guide – SerpentSpine has two UV maps TEXCOORD.xy and TEXCOORD1.xy, along with a vertex color called COLOR

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231917-2db88099-f9c9-4967-a8b5-c5fe194cc288.png" width="400"/>
</p>

For weapons, the first TEXCOORD is for the textures:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231961-15a8ec7c-df73-4c68-ab81-b07a61419718.png" width="800"/>
</p>

While the second controls the how the weapon appears and disappears:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232042-e06c3613-cadc-4026-bba8-11d6eef1635a.png" width="800"/>
</p>

The vertex COLOR has four components: RGB and A. What exactly each component controls is outside the scope of this tutorial, but in brief A is primarily used for outline thickness while RGB is used for ambient occlusion, specular and metallic.

NOTE: If your model has multiple UV maps and textures, you will need to merge them into one before continuing. You can do this by lining the textures up side-by-side and then scaling the UV maps to match up with each component. Make sure the width and height of the final texture are powers of 2 (i.e. 1024 x 1024 or 1024x2048 or 2048x2048 etc.)

10.	The banana model we are using only has 1 UV map, which we rename to TEXCOORD.xy in order to match up with the Serpent Spine model

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232096-f47f73af-77ad-4a4b-8ee4-d608c81279d1.png" width="800"/>
</p>

11.	For the second TEXCOORD, we create a new UV map called TEXCOORD1.xy, go to the top view by pressing 7 on the numpad, select the entire mesh and then press UV→Project From View

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232109-8a88e9ac-5f87-42c4-b4ed-ff5c988dbdfe.png" width="800"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232115-ae7d3b9f-c924-4883-afdd-f18cf7618212.png" width="800"/>
</p>

We then scale and rotate the banana so it matches up with how the TEXCOORD1 of SerpentSpine originally looked. This will cause the weapon to phase in starting from the stem of the banana

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232139-6003d62f-5a15-4e1d-834f-03a0acc2f0e5.png" width="800"/>
</p>

(Note: Older version of the plugin have an issue related to TEXCOORD1 where the model outline disappears. While there are several causes for this, the most common is due to the game re-using a texture slot for both fading and outlines. Try deleting the ps-t2 and ps-t3 lines in the .ini file and see if that resolves the issue).

12.	Finally, we deal with the color. If your model already came with vertex colors, you can rename them to COLOR and be done (though note that wherever you got the model from might not be using the same values for COLOR as Genshin does, so it still might be safer to delete them and transfer over ones from a 3dmigoto mesh).

This banana model does not have vertex colors, so we first need to add a color variable. Do so by going to the data properties tab and pressing the + button. We want the name to be COLOR, the domain to be Face Corner and the Data Type to be Byte Color. You can leave the color as black for now, we will be transferring it from the original object in the next step.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232163-f9abc26d-3cb0-4fa7-8ef8-1ff0d89e1de3.png" width="400"/>
</p>

13.	Now that we have a COLOR, we need to transfer the correct values from the Serpent Spine. Select the banana, go to the modifiers tab, select add modifier→data transfer

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232193-d04a6d50-4493-431d-8be7-3bd3e243ab3f.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232201-d2802655-944c-4ceb-b694-25546ff64cc8.png" width="400"/>
</p>

Set the source as SerpentSpine, check the Face Corner Data box and Colors tab and make sure the options are All Layers and By Name for Colors:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232208-bd3a2147-8f59-4050-9518-b3388dfea2f1.png" width="400"/>
</p>

(Note: for more complicated models with multiple vertex colors, you can use the eyedropper to copy the color data from a specific part of the component instead of selecting the entire object)

Finally, press the down arrow and click Apply

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232216-70505fa2-dd30-435a-9468-a1be2e984db0.png" width="400"/>
</p>

You can double check it worked correctly by going into vertex paint mode and checking that the colors match up:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232222-ec49ff63-d7dc-40d3-bc81-ca9317df2b20.png" width="800"/>
</p>

14.	Next, we need to rotate the model relative to the original and apply transforms. Even though the models look like they overlap, Genshin rotates them during the process of drawing to the screen so we need to do so in Blender as well to counteract the effect. Select the object and rotate 90 degrees relative to the original like so:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232236-4369c7ff-3638-4a97-a1a7-e113702b86fa.png" width="600"/>
</p>

And select the object and apply all transforms (IMPORTANT! If you don’t apply transforms, the weapon will appear in a completely different orientation and scale than you might expect)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232251-83682dd2-bde9-470e-9081-1b4af92b6dd2.png" width="600"/>
</p>

(Note: Orientation can get confusing, so when in doubt about which direction is correct just try rotating both ways to see which works)

15.	We are almost done! The last part is to change the name to have “SerpentSpineHead” and remove that text from the original object so the plugin knows which object to export. Once you have named things correctly, export using the Export Genshin Mod Folder back to SerpentSpine data folder (see Mona tutorial for full steps)

If you have any issues with exporting, please refer to the [GIMI troubleshooting guide](/Guides/Troubleshooting.md#model-exporting-issues) to see if your issue shows up.

16.	At this point, it is a good idea to confirm that your model is loading into the game correctly before we start working on textures. Copy over the Mod folder and reload:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232283-3de96889-ec67-41ea-8595-a0ef20d9c654.png" width="800"/>
</p>

It looks like the shape and position are correct, so we now move on to fixing the textures.

17.	We start with the diffuse texture. Diffuse textures in genshin are .dds with type BC7 SRGB which use the alpha layer for emission. Example of the original SerpentSpine texture (part above alpha layer on left, part below on right):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232304-34589d61-5654-42ed-9dbc-29aab182fbf5.png" width="600"/>
</p>

For this part, we won’t be doing anything too fancy with the textures so we just invert the alpha channel, save as a .dds and replace the original SerpentSpineHeadDiffuse.dds (see Mona tutorial for more details on basic genshin texture editing).

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232314-ca0a08ea-34dd-4902-84c4-ea62268a1997.png" width="600"/>
</p>

Note1: Make sure that the width and height are powers of 2 (1024x1024, 2048x2048, 1024x2048, etc.), or else you might run into issues

Note2: Not all diffuse textures have emission – some don’t have an alpha channel at all. In those cases, you do not need to invert the channel and can just use the texture as is. When in doubt, check the original texture to see what it looks like and mimic it

18.	Replacing the diffuse texture and reloading:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232327-74079c8d-9f5a-44e9-bbe7-01b7e3aa250f.png" width="800"/>
</p>

Looking much better, but we can still see some reflection and shadow issues. These are being caused by the lightmap, which we will need to edit as well.

19.	If your model came with a lightmap, you can just repeat the above and save it as BC7 Linear and replace the original. This model did not come with one, however, so we need to create a basic light map. The original lightmap looked like this above and below the alpha layer:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232355-06724fe1-619e-44f8-be5d-d39474f61497.png" width="600"/>
</p>

Details of how exactly lightmaps work is beyond the scope of this tutorial and will be covered in later ones – for now, by comparison with the diffuse textures we can see that the map seems to be using purple above the alpha layer for the beige part of the sword, which is the most similar to our model. So we can just pain the entire texture that color to get a reasonable result:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232372-a244d012-b35a-446b-b729-6f8ec4bab2bb.png" width="400"/>
</p>

20.	After replacing the lightmap texture, reload the game. Banana blade complete!

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232383-1b97ed85-7965-4299-91bc-a233c5bfaa49.png" width="800"/>
</p>
