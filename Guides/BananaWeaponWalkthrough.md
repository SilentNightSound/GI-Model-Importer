## Custom Weapon Modding Walkthrough

This is a walkthrough for importing custom weapon models into Genshin Impact.

For this tutorial, I am assuming you are familiar with the basics of using GIMI (how to set it up/import/export/load); if not, please read through [Mona Hat Removal](MonaWalkthrough.md). I am also assuming basic Blender knowledge – for questions on Blender basics like how to change modes, select vertices and open certain menus please search the knowledge you need on Google/Youtube.

Weapon mods are more complicated than basic mesh edits, but less complicated than importing custom characters. ~90% of the steps remain the same for custom characters, but characters involve much more complicated vertex group/bone structures than weapons. 

I will be demonstrating three different weapon models, ordered by complexity. Generally speaking, for weapons the order of difficulty from easiest to hardest is Swords/Spears/Claymores without tassels → Swords/Spears/Claymores with tassels → Bows → Catalysts. Each weapon builds on the last in terms of complexity, so please read through in order. 

I will be using [this]( https://sketchfab.com/3d-models/banana-6d99c6c1a8bc4b3e97cebbc49d62115d) model of a Banana for all three mods (credits to Marc Ed).

First model: Banana Blade ([jump to section](#banana-blade))  
Second model: Bownana ([jump to section](#the-bownana))  
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

6.	Now, we need add the custom 3dmigoto properties on to the new object. There are two ways to do this – you could delete all the vertices of the old model then merge the new one into it, or you could use the [custom properties transfer script](/Tools/custom_property_transfer_script.txt). I’m going to use the latter method in this tutorial
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
<img src="https://user-images.githubusercontent.com/107697535/183232193-d04a6d50-4493-431d-8be7-3bd3e243ab3f.png" width="400"/> <img src="https://user-images.githubusercontent.com/107697535/183232201-d2802655-944c-4ceb-b694-25546ff64cc8.png" width="400"/>
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

## The Bownana

Moving on to more complex models, I am going to demonstrate how to create a Bownana by replacing Prototype Crescent. This method also applies to any swords/spears/claymores with vertex groups (e.g. tassels usually). Most of the steps remain the same as the Banana Blade, but there are a few additional complexities we need to worry about.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232781-149695c9-19ae-40d5-983d-bde544e4ceaa.png" width="800"/>
</p>

1.	Import the Bow and Banana model the same way as the previous section (steps 1-3). We can confirm that the original model we are replacing falls into this section by checking if it has vertex groups

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233096-e6e169e3-eef4-4318-afb7-96d117216182.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/183233106-6fa7122a-a0cd-44fc-873e-5ad550a56ea5.png" width="300"/>
</p>

2.	Since the shape we are replacing is different, we need to also change how we modify the model so it is placed correctly:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233186-4f23dec9-1fed-4ca5-8737-4d83948922e6.png" width="300"/>
</p>

3.	Setting the 3dmigoto custom properties, TEXCOORDs and COLORs remains the same as the previous section (steps 6-13)

4.	The first major difference occurs when we need handle the original’s vertex groups. These are responsible for things like the bowstring being pulled and how the bow deforms. The bow has a total of five groups (note: group 0 has no weight at all but still must be included in order to export properly; in practice, there are only four groups you need to worry about)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233193-cd119af9-9bdc-4d34-b975-aaeaf62f85ac.png" width="800"/>
</p>

5.	If the model we are using does not need the bow string pull animation, we can just use a single group vertex group and full paint on only group 1. To do this, we go to Object data properties and add 5 vertex groups named 0,1,2,3,4 and then go to weight paint to fully paint the object on group 1:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233231-a80f39b3-3ff4-4637-9c98-6849ea35ecea.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/183233232-d2ca7009-018b-473e-ad66-7c45bfd4ddef.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233268-381443f0-4286-489d-919f-0bed57056871.png" width="800"/>
</p>

(Note: you still need to include all five groups in order for the new object to export properly)

6.	While this works, it isn’t great unless you are replacing the model with something like a gun – ideally, we still want the bownana to have a string and deform properly. If the model you are using already came with vertex groups that are similar to the ones Genshin uses, you can merge and rename them until they match up with the original. This banana model does not have any, so we need to perform an auto-weight transfer

7.	We need to give the banana a bowstring. We can either make a new one, or re-use the original string – I will be doing the latter in this tutorial. Copy the original bow, and delete everything but the string:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233287-92ad4e09-e0de-4340-bc18-4c06788c7935.png" width="300"/>
</p>

8.	Make sure the UV map name of the string and banana object match up (TEXCOORD.xy, in order for the UV maps to merge as well), then merge the two objects together by CTRL+clicking both and using CTRL+J. Also make sure the string UV map is over a region of the texture that has the correct colors. If you previously created TEXCOORD1.xy, you will need to either recreate it or move the string to the correct position.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233320-b0958745-27ea-4e7c-bcd4-d1d96c65d55c.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233326-2555eb32-0cfb-42f3-8901-c21175a99b34.png" width="400"/><img src="https://user-images.githubusercontent.com/107697535/183233328-d7b8e9e0-c657-4f94-8f23-7502c5e55844.png" width="400"/>
</p>

9.	Now that we have our bow string, it is time to assign the weights. Make sure the banana has 5 vertex groups named 0, 1, 2, 3, 4, then create a DataTransfer modifier. Select the Prototype Crescent as the source, and select the Vertex Data object and Vertex Groups tab:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233355-c230a973-86d9-4126-a227-d14d752af18d.png" width="300"/>
</p>

Click the arrow and press Apply.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233365-ebd690c7-e63b-40a8-bca6-043d20f23557.png" width="300"/>
</p>

If everything was done correctly, the bownana should now have approximately the same weights as the original:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233373-46d4c532-5cb5-45c3-8a0c-0f0d4d43b1c2.png" width="800"/>
</p>

And double checking, it looks like the string has proper physics in-game:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233380-14387251-dac0-4628-acab-ca073d5ab932.png" width="400"/>
</p>

(Note: there is an alternate method of transferring weights using the Transfer Weights option in weight paint mode – both methods should give similar results)

10.	From this point on, the rest of the steps are the same as the banana blade (steps 14-20 in previous section): rotate and apply transforms, rename, export, fix the textures, and load into game:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233408-75bba365-d62a-478f-b934-1cda4b4beb7d.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233419-5c1616e1-767f-40e0-870d-7bc6d3b68b36.png" width="800"/>
</p>
