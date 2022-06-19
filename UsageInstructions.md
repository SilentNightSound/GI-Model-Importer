## Usage Instructions

Below is a summary of how to use 3Dmigoto's various features, as well as how to mod Genshin meshes and textures. For now it is just text descriptions, but I will be adding more screenshots and walkthroughs in the future. I have organized the content approximately in difficulty from easiest to hardest - I recommend reading through the instructions in order, since later sections rely on understanding how previous sections work. 

No specific knowledge is required as a prerequisite, but I recommend being familiar with Blender.

Note that this project is still under development, so expect bugs and missing features. Please let me know if any section has errors or is unclear.

I highly recommend these videos as an introduction to modding with 3Dmigoto: https://www.youtube.com/watch?v=zWE0xP4MgR8 and https://www.youtube.com/watch?v=z2nvJzkwHHQ. While Genshin has several quirks to its structure that makes it more complicated to mod, a large amount of the information contained in those videos is still relevant and can supplement these explanations with more details and visuals.

### TLDR 

(AKA I don't want to read through everything to understand how it works and just want to perform basic model edits)

(See https://github.com/SilentNightSound/Genshin-Model-Override/blob/main/MonaWalkthrough.md for a step-by-step walkthrough of this with removing Mona's hat)

1. In blender, go to File -> Import -> 3DMigoto Frame Analysis Dump (vb.txt + ib.txt)
2. Select the files from the CharacterData folder of this repo for the character you want (all characters have at least a head and body, but some also have additional bits like skirts which I have labelled as extra). Leave all options as default and press Import
3. Perform modifications you want to the model, with the following restrictions/notes:
   - The number of vertices and edges for each model part cannot exceed that of the original model (Note: there is currently a bug in the program where the 3Dmigoto plugin will export around 10% more vertices than the original model has, so in reality you are limited to around 90% of the original. Going over will prevent portions from being drawn and break textures. I'm working on fixing this)
   - Adding in new vertices or geometry is much more complicated than deleting parts of the mesh (e.g. filling in the holes in a character model after removing clothing). If you are trying to patch holes, I recommend either re-arranging existing vertices to cover them (if the hole is small enough) or trying to copy from another Genshin model (see Localized Model Overrides for details)
   - Character's faces are stored separately - these scripts and instructions do not yet support face modifications
   - Do not change the vertex groups, vertex colors, or custom properties of the objects otherwise the export will fail
   - It is possible to connect the texture maps to the object in Blender, but you will likely have to convert the .dds to a .png in order for Blender to recognize it and then later convert back to .dds
4. Select the head object and go to File -> Export -> 3DMigoto Raw Buffers (.vb + .ib). Press export, leaving all options as default, and name the file CharHead.vb
5. Repeat step 4 for the body object, naming it CharBody.vb, and the extra object (if it exists), naming it CharExtra.vb
6. (optional) Perform any edits to the character's diffuse and lightmaps
7. Run the genshin_3dmigoto_generate.py script one folder up from where the results from steps 5 and 6 were imported with the command `python genshin_3dmigoto_generate.py -n Char`. This generates the CharMod folder
8. Move the generated CharMod folder into the Mods directory of the launcher you created during the installation step
9. Press F10 in game to load the mod

Each character can only have one corresponding folder at a time in the Mods directory - if you want to load a new model for a character, the old one needs to be removed from the Mods folder first.

&nbsp;
### Hunting for Buffers

Pressing 0 on the number pad while 3Dmigoto is active turns hunting mode on  (green text overlay, default) or off (no text overlay).

With hunting mode turned on, you can cycle through the various buffers and shaders that Genshin is currently using to draw objects to the screen. Selected buffers/shaders will have their draw calls skipped, showing you what portions of the screen they are responsible for drawing. 

Pressing the + button resets all the currently selected buffers back to zero, and it is a good habit to reset between searches or reloads since otherwise it can get confusing as to what is actually being selected.

I recommend performing hunting in the character menu, since otherwise the number of objects quickly becomes overwhelming.

- Pressing / and * on the numpad cycles through the Vertex Buffers (VB), which contain information on the vertices for the objects being drawn to the screen. You can copy the hash of the currently selected VB with numpad -
- Pressing 7 and 8 on the numpad cycles through the Index Buffers (IB), which contain information on how vertices are connected to form the model. You can copy the hash with numpad 9
- Pressing 4 and 5 on the numpad cycles through the Vertex Shaders (VS), which contain information on how vertices/faces are positioned on the screen. Use numpad 6 to copy the hash
- Pressing 1 and 2 on the numpad cycles throught the Pixel Shaders (PS), which contain information on how textures and colors are applied to the objects. Use numpad 3 to copy the hash

&nbsp;
### Removing Buffers and Shaders

Once you have found an buffer or shader that you want to have skipped, you can tell 3DMigoto to always skip the draw call for that object even when it is not selected.

To do so, create a .ini file in the Mods folder (any name is fine for the .ini), and add the following to it for VB/IB skips:

```
[TextureOverrideX]
hash = Y
handling = skip
```
Where X is any name you want and the hash corresponds to the one found while hunting (Note: these are buffers not textures, but the naming convention refers to both as "textures").

And the following for VS/PS skips:

```
[ShaderOverrideX]
hash = Y
handling = skip
```

Same logic applies for X/Y as for the one for buffer overrides.

Note that some objects might have multiple buffers or shaders associated with them - if parts of the object remain after placing the above code in the .ini file (such as shadows, reflections, outlines), cycle through the buffers and shaders again to see if there are any other ones that are responsible for drawing that part.

This functionality can be useful if the portion of the character model you are trying to remove is drawn by a specific VB/IB/VS/PS - SpecialK has a similar functionality in its shader section.

&nbsp;
### Replacing Textures

Replacing a texture for a model (similar to how Special k does) is simple:

1. Hunt down the IB that corresponds to drawing the model. You know you have found the correct one when the model disappears.
2. Create a texture override section similar to what was created in the Removing Buffers and Shaders section, but instead use the following to replace the textures:

```
[TextureOverrideX]
hash = Y
ps-t0 = ResourceDiffuse
ps-t1 = ResourceLightMap

[ResourceDiffuse]
filename = TextureDiffuseMap.dds

[ResourceLightMap]
filename = TextureLightMap.dds

```
Note that we do not use handling=skip here since we do actually want the game to perform the draw call. We also need to load our new texture maps into memory by creating a resource object. 

Some objects do not have a corresponding lightmap, and some objects (like characters) have multiple texture maps on a single buffer (see next section).

&nbsp;
### Removing Buffers for Multi-Index Objects and Frame Analysis Dumps

Sometimes, multiple objects are drawn on a single buffer. One example is character models - the head and body are separate objects, but they are both drawn using the same VB/IB so if you skip that buffer you will end up skipping the draw call for the entire object. Likewise, if you try and replace any aspect of the buffer you will only replace one and not the other.

At this point, there is nothing more we can do from the hunting menu - we have to start digging deeper into the draw calls. By pressing F8, we can perform a frame analysis dump to get more information. This will dump all the buffers relating to drawing a single frame to a folder called FrameAnalysis-timestamp, as well as to a file called log.txt which explains what commands were executed.

- Note1: Frame dumps can be quite large (several GB), so be careful not to press F8 in an area with many objects. Doing it in a dense area like a city will probably just cause your game to crash. I recommend performing it from the character menu.
- Note2: A frame dump may cause the game to pause for an extended period. Depending on your hardware, it can be from a few seconds to an upward of a minute
- Note3: I have enabled both txt and buf dumps in the d3dx.ini file, as well as a few other options that give more information - the default .ini has the frame analysis turned off

With the frame dump, we can perform a search for the hash corresponding to the IB we are interested in. This will result in several -ib .txt files, which you can open to see where the index for certain objects begin and end. You can then specify a overrides on a single object with:

```
[TextureOverrideX]
hash = Y
match_first_index = Z
handling = skip
```
Where Z is the index of the object in the buffer you are matching.


&nbsp;
### Deletions and Modifications of Model Vertices

Section still under construction, see TLDR for walkthrough

Once we have the frame dump, we can extract the character models from the buffer in order to make edits. Normally, this would involve finding the VB/IB hash that involves drawing the character, collecting the corresponding files from the frame dump, importing the corresponding buffer into Blender using the 3Dmigoto plugin, making edits, then exporting a modified version and overriding the model with:

```
[TextureOverrideX]
hash = Y
vb0 = ResourceVB
ib = ResourceIB
handling = skip
drawindexed = auto

[ResourceVB]
type = Buffer
stride = 40
filename = File.vb

[ResourceIB]
type = Buffer
format = DXGI_FORMAT_R16_UINT
filename = File.ib

```

Where the stride represents the size in bytes of all the data corresponding to a single vertex (is listed in the dump headers) and format is the size of a single index value.

In this case, we skip the game's draw call using handling = skip, then substitute our own draw call with the new resources with drawindexed = auto (which automatically calculates the parts of the object to draw from the ib file and buffer descriptions). These new VB and IB resources are then passed to the shaders which calculate their positions and apply textures.

Genshin is not so simple, sadly. Genshin actually splits the properties of character objects across multiple different buffers - at least six, to be precise. One for positional/face data (position, normal, tangent), one for blend (blendweight, blendindices), one for textures (color, texcoord), one for drawing the object (contains the position data for the object for this specific frame, and is recalculated each frame), and at least two for specifying indices (some characters have two, some have three depending on the complexity of their model).

Furthermore, most of those buffers actually have different hashes and are not just a single hash object split into different buffer slots. Which means if we override on one hash the model will break unless we override the correct data on every single related buffer at the same time.

To add more difficulty, the headers that 3dmigoto exports are actually wrong as well. The headers that are exported contain information about all the vertex data, not just the ones that are currently in the buffer. This leads to a mismatch between the header numbering/byte offsets and the actual data, meaning you have to recalculate what the actual data is directly from the raw buffers.

Having fun yet? There's more! In addition to placing multiple objects on a single buffer then splitting the properties of that buffer between several, it also uses the higher buffer slots (VB1+) and the pointlist topology, neither of which 3Dmigoto supports so you have to convert back to formats it does.

And even if you do all the above and export it into Blender, 3Dmigoto will output the results in a format that cannot be ingested back in into the game. So you have to reverse the above process to split it back up into its parts.

Anyway, I wrote scripts that handles most of this. You can just run the genshin_3dmigoto_collect.py script on a frame dump with just the main draw VB and it will find the related buffer files and organize/format them correctly. Likewise, running genshin_3dmigoto_generate on a 3Dmigoto export from Blender will split it into the correct buffer files and format the .ini file so everything loads properly. Take a look in those files if you are interested in the specifics of how this works.



&nbsp;
### Localized Model Overrides

Still under development, see videos at the top of this page for more explanations and a walkthrough in a different game

- New geometry/meshes from other models will not have the correct weights or vertex groups
- Import the model, position it close to/overlapping where you want it to be, and transfer the vertex groups and colors to it. Also make sure it has texture uv values assigned
- Works best on while patching small holes in the model after removing parts of the mesh, or replacing parts of the mesh with others (e.g. shoe -> foot)
- Will work best if the model you are getting the patch from is also from the game and the same body type, or a model derived from a game model. Can use models from other sources, but may have to change the format to match
- Larger holes or objects will not have the vertex weights transferred correctly since Blender will not be able to interpolate. In these cases, you will have to do it manually or find an object from another game model that already has the correct groups set

&nbsp;
### Complete Model Overrides

Still under development, see videos at the top of this page for more explanations. I do not yet have this working reliably, so try at your own peril. Some tips/observations I have found during my experiments:

- Basic concept is to overlap the model you are replacing with the new one as closely as possible, then transferring the vertex groups, weights, colors and custom properties over
- Model needs to be approximately the same complexity (vertex/edges) and shape otherwise the transfer will not work well. Even if the models are very similar, may still run into issues.
- Models that are too far removed from the original are not possible since there is no way to assign the blend indices and vertices in a way that makes sense (can still be doable if you give up on animations working correctly/at all)
- Complicated hair structure is a nightmare. There is a reason almost every character in Genshin has simple hair. Unless you are amazing with blender, I recommend just assigning all the hair to the head vertex group and giving up on trying to get wavy hair movement working (or stick with the original hair)
- Make sure that all the vertices in the model have weight/are assigned to a group, and that the groups are correct. Often, the weight transfer can end up transferring the hand and arm groups to incorrect areas since they are so close to the body (would be better to T-pose model, but I'm not sure yet how to load pose information from the constant buffers). Fingers are also problematic
- Models only use 2 UV maps - one for the head, and one for the body. Some characters actually use a third for things like skirts, but that is just a duplicate copy of the body texture and I'm not sure if it can be modified (testing to come)
- Which UV a specific vertex uses depends on which object the game assigns it to. As far as I can tell, the game hardcodes a certain index value for each character and separates based on that. Currently looking into ways to change this and increase flexibility 
- May have to rotate the model relative to the original if is face down when loaded (not sure what causes this, shows up with mmd models)
