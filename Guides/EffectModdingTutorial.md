## 3DMigoto GIMI Effect and Shader Tutorial

This tutorial will go over the process of changing Genshin’s effects such as skill effects, lighting effects, and any in-game objects that are not controlled through textures or buffers. Learning how shaders work will significantly increase the range of what you are able to mod.

This effect modding tutorial is more difficult than my previous ones on basic mesh editing/importing and texture editing, but reading those ones is not a pre-requisite for understanding this tutorial. 

I have arranged this tutorial roughly in order of increasing difficulty, so even reading the first section will hopefully be enough to make simple edits. Later sections will require basic programming knowledge.

I will go through three examples of increasing complexity: 

-	Changing a character’s attack/skill color (see https://gamebanana.com/mods/409181 for an example of recoloring Ganyu’s ice attacks)
-	Creating an effect which toggles between multiple colors over time (see https://gamebanana.com/mods/418434 for an example of a Christmas tree that changes what color the lights are)
-	Demonstrating how to create basic effect animations (see https://gamebanana.com/mods/420434 for an example of animated lines on Cyber Bodysuit Raiden)

## Prerequisites

Have the 3dmigoto GIMI Dev version installed (green text needs to be visible).

## Important Note

By default, I have disabled the ability for GIMI to dump shaders since they can mess with mods. You can re-enable them by ensuring that the line `marking_actions` in d3dx.ini contains `hlsl` and `asm` in the list.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211983955-7a13e1a0-542e-435f-ab67-aa5e78031bd7.PNG" width="600"/>
</p>

Also, if you have issues with mods after trying out things in this tutorial try emptying the ShaderFixes folder – sometimes a dumped shader can cause certain mods to malfunction.

Let’s begin!

## Changing Character Attack Colors (Diluc’s Flames)

For the first section, I will demonstrate how to recolor Diluc’s flames. This section is basic/intermediate difficulty, and does not require any prior coding/shader knowledge.

1.	First, I recommend traveling somewhere where there are as few objects on screen as possible but the effect you are looking for will still show up. You will see why shortly, but the more objects on screen the longer it will take to hunt for the shaders we are looking for. The starting beach area is always a good choice

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211985874-1e3a43e6-bb5e-48e1-9b8c-c99a199595a0.png" width="600"/>
</p>

2.	Once you have a good location, trigger the effect you are looking for and enter the pause menu. In this case, we are interested in the flame effect from Diluc’s skill, so we press e then pause (note: for effects that show up only when the game isn’t paused, it is still possible to get them just a little more difficult – I will explain how later)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986006-20e3e92b-29c4-4f3e-8808-bf151fb72e97.png" width="600"/>
</p>

3.	Now, we are going to press `1` and `2` on the numpad to cycle through the Pixel Shaders (`PS`). There are two types of shaders – Vertex Shaders (`VS`) which control where things are drawn on-screen, and Pixel Shaders (`PS`) which decide how they look and draw textures/colors. Since we are interested in the color, we want the PS

4.	When you find the right `PS`, the effect will vanish in-game. For example, here is the shader that controls the center flame of the swing:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986075-16734f42-e46b-46ab-a46f-b2a8ac8c0821.png" width="600"/>
</p>

While this one controls the surrounding flame clouds:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986124-523e0fe5-f134-4fcd-b8ad-588bcf158f06.png" width="600"/>
</p>

We will start with these two.

5.	Pressing `3` on the numpad will copy the PS hash to your clipboard, and save the shader into the ShaderFixes folder. The hashes of the above two shaders are `e75b3ffb93a1d268` and `dd0757868249aaa5` (Note: you can press numpad `+` to reset buffers to 0 if you need to quickly go back to the starting point). Note that shader hashes can change between versions, so your hashes may not be the same values

6.	The shaders should now show up in ShaderFixes with a name like `hash-ps_replace.txt`. 

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986246-48a6ccdb-e779-4e13-8b1e-ce02bcb1b044.png" width="400"/>
</p>

If they don’t show up after pressing `3` on the numpad, make sure you put `hlsl` and `asm` in the `marking_actions` as mentioned in the Important Note at the top and have refreshed with `F10`:

Also note that a small number of shaders will not decompile properly into `hlsl` (high level shader language), and will instead revert back to `asm` (assembly). These shaders will still work, but they will be more unwieldy to edit. I won’t cover asm in this tutorial, but the concepts are the same – the syntax of the shaders are just harder to read.

7.	Open them up with your text editor of choice (Notepad/Notepad++/Sublime Text/whatever). The file will look daunting at first, but don’t worry – you don’t need to understand the details in order to make basic changes (I will go more into details of how this file works in the later sections).

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986377-e2fd3418-f673-4cf8-9ff1-938faf945c76.png" width="400"/>
</p>

8.	For now, we are most interested in messing around with the inputs and outputs. These are listed right under main – this file takes 9 inputs (numbered `v0`, `v1`, `v2`,…`v8`) and has one output (`o0`).

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986455-0a5ca895-c3a7-4066-a59f-be71fe2634e6.png" width="300"/>
</p>

9.	Usually it is simplest to start with the output. It has a type of `float4` which means it has an `x`,`y`,`z` and `w` component and takes a floating point (i.e. decimal) number as input. We can experiment to see what it does by putting a line at the end of the code to forcibly set the value to a constant:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986560-b25728ae-e24a-4fe1-929e-0d49bf02dadf.png" width="300"/>
</p>

(`//` and `/* */` indicate comments in the code and are ignored by the program)

Basically what we are doing is overwriting what the game is calculating for the value and substituting in our own (3dmigoto will automatically load and replace any shaders from the ShaderFixes folder).

(Note: 3dmigoto also exports the asm code below the hlsl code – when I say the “bottom”, I mean right before the `return` statement, the `/*~~~~~~~~~~~~` and `Generated by Microsoft (R) D3D Shader Disassembler` lines not after. Everything after that point is commented out, and will not run by default. If you see things like `div`, `mul` and `mov` you have gone too far) 

10.	Save the file, then press `F10` in game to reload (make sure to also press `+` to reset buffers!). This is what happens:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986773-ee66b8c6-2d80-44fc-b1cf-fa8e41f4f9db.png" width="600"/>
</p>

The central line has turned black, while the sparks have turned green. If you familiar with how colors are stored you might have a guess what `o0.x` represents, but we can continue checking to be sure:

Setting the `x` and `z` components to 0, and `y` to 1:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986865-67fb5c91-3c25-4df7-8821-c5b11c3531fa.png" width="300"/>
</p>

Sets everything to green:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986940-01ebfc18-ef72-4c60-b7e2-91985bf9c2b1.png" width="600"/>
</p>

While setting `x` and `y` to 0 and `z` to 1

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986994-c3070f3f-9eb5-480a-b8ed-13ab90076c80.png" width="300"/>
</p>

Sets the color to blue:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987033-f9a1b299-9676-4687-9ae9-808db2b84b3d.png" width="600"/>
</p>

Or in other words `o0.xyz` correspond to the RGB colors of the effect. It isn’t always the case that `o0` is the color – some shaders have multiple outputs, so the color might be on `o1` or `o2` etc; thankfully, this shader is fairly simple and only has one output `o0`.

(If you are wondering what `w` represents, it seems to be related to the wideness/emission of the effect:)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987161-edd09e67-99e8-42ff-9653-9aafadda4531.png" width="600"/>
</p>


11.	Now that we know what the values correspond to, we can make basic changes to the colors. For example, setting all three `o0.xyz` to 0 causes Diluc’s flames to become black:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987214-bc9c7a29-1bf0-483d-bb9d-7cba39afd1da.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987253-b4480e4e-b3f3-4726-b66d-cb8e5c698815.png" width="600"/>
</p>

Or we can turn them to purple by setting `r` and `b` to 1, and leaving `g` as 0:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987317-f0237be8-da62-43d1-8d0f-7f6447872f09.png" width="600"/>
</p>

And note we aren’t limited to just setting constants either – we can shift the color hue as well. This reduces the amount of red in the attacks while giving more green and a lot more blue to create a salmon pink color:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987374-be4661b0-46aa-4829-82c0-2274175a8b6e.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987415-bf5057ee-1c20-4e19-8195-0c3ace4fd26f.png" width="600"/>
</p>

Note that unlike the cases where we forcibly set a constant value, the flame texture is still visible here.

We can even do fancier things like set the values to mathematical expressions, but I will go over that in the final section.

Instead of changing the output it is also possible to change the effects by changing the input using a similar method (putting the lines right after when they are normally loaded and overriding the game’s values), though you will need to experiment to deduce which variable changes what.

12.	This is the basic process to change effect colors – find the hash, dump it, then modify either the input or output. However, if you have been following along you may have noticed that not all the flame textures have been replaced – there are still more we need to dump:

`0fa220b5adced192` is the sparks:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987510-3d411b42-0e3a-4d69-8081-e8b2ebf8707f.png" width="600"/>
</p>

`bf7eb60b256538c7` is the flames along the sword:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987559-c100eec0-4a7f-4039-8873-bfb3b2d9308e.png" width="600"/>
</p>

`439c03865c4ce77e` is the bird:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987610-6a3362cf-bcb9-4d9f-b1a7-a47feb245bc4.png" width="600"/>
</p>

`7690cf4aa6647c6c` is the sword glow during ult:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987673-309f0467-ba0f-40ae-94cc-256912c056c0.png" width="600"/>
</p>

Collecting all the different shaders is what takes the majority of the time when editing textures.

13.	Even turning all of the above black, you may have noticed that there are still flame effects that show up during the ult where we cannot pause the game:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987723-01d3c4ba-f86d-4139-a0d2-468af27e8229.png" width="600"/>
</p>

Getting these shaders is more annoying, but not impossible. The first method is to enable something like infinite burst energy in grasscutter and cast the ult over and over while cycling. This will take some time, but should work for anything that is repeatable.

For effects that only show up in cutscenes or are hard to reproduce, however, the fastest method is to do a frame dump. See the texture modding tutorial for more details on how to perform frame dumps, but essentially you press `F8` while the effect is on-screen to perform the dump at the same time as the effect is visible. 

Unfortunately, since we do not know the shader hash it will need to be a full dump so make sure you have 5-10GB of space free and as few objects on screen as possible.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987810-78fc6d7f-1f98-4474-8e59-86d155378fda.png" width="300"/>
</p>

When you have the frame analysis folder that is created after pressing `F8`, you can look through it to see when the effect is drawn. The `o0` and `o1` files show what is being drawn each ID, and are very useful to isolate the exact ID an effect is drawn on screen.

Example: `000351-o0=3315d2b5-vs=eb65cb4eba57132b-ps=7690cf4aa6647c6c.dds` looks like this in my frame dump:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987902-faaa47f5-db4e-42b6-96c4-ea3629da0480.png" width="600"/>
</p>

While `000352-o0=3315d2b5-vs=f6a1f24f9c9b28c2-ps=a69e25f25a6c8e04.dds` looks like this:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987954-5e042475-bddd-4168-a834-0cfb55578c49.png" width="600"/>
</p>

So we know that that in this frame, draw call `000352` is responsible for the glowing effect on the ground. We can also get the hash from the filename, `ps=a69e25f25a6c8e04`.

Using this method we can find the remaining hashes:

`000353-o0=3315d2b5-vs=f50ce30bb0caf55c-ps=4d4da8a4cbe1149a.dds`

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988024-d44e4331-8232-43d7-b536-9784b0fb6ee4.png" width="600"/>
</p>

And `000365-o0=3315d2b5-vs=72ce1e39ede0982f-ps=622a52d3edcf0363.dds`

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988083-9efb97a2-9d6d-48fc-8faa-878dc85f48c7.png" width="600"/>
</p>

14.	Now that we have the remaining hashes, we need to actually dump them. Press numpad `+` to reset buffers, cast the ult, then start cycling with numpad `1`/`2` while the effect is on-screen. Even though the effect will have left the screen by the time we reach the hash, as long as we started cycling when the effect was on-screen it will show up in the list and be available to dump:

Example of PS `4d4da8a4cbe1149a` showing up even though the ult isn’t active:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988198-9a6ddd0e-e55b-4783-8602-d21bca4d61c0.png" width="600"/>
</p>

Using this technique, we can dump the remaining shaders `a69e25f25a6c8e04`, `4d4da8a4cbe1149a` and `622a52d3edcf0363`:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988253-5f67709e-62b5-4a17-ad21-3dd99de90bd3.png" width="600"/>
</p>

15.	Modding complete! Or…maybe not. If you switch to another pyro character such as Hu Tao, you may notice an issue:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988307-de6a26dd-a26a-45ea-a760-4c694ed82dca.png" width="600"/>
</p>

We have set ALL flames to black, not just Diluc’s. Also, if someone else created a mod that changed another character’s flames like Hu Tao’s or Klee’s, it would overlap with the Diluc one as well. 

16.	We want a way to limit the effect to only show up when Diluc is on-field. There are a couple of ways we can do this, but they all follow the same basic principle – we identify some condition that is caused whenever Diluc is on the field, then only apply the effects if that condition is true.

This is a somewhat more advanced topic which will make more sense after you play around with the shaders more and read the later sections – if you have issues understanding this, try reading the following sections and coming back later.

First, we need identify a hash that is unique to Diluc. For simplicity, I am going to use Diluc’s `VB` hash `56159d74` (`VB` can be cycled with numpad `/` and `*`, and copied with numpad `-`):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988418-a6af34f5-b9dc-4446-aa84-44ddf93a435c.png" width="600"/>
</p>

17.	Next, we construct an `.ini` which we will use to selectively apply the effects. We define a variable called `$ActiveCharacter`, and set it equal to 0 at the start of every frame (`[Present]` runs once per frame at the start). We only set the value equal to 1 whenever Diluc is on-field, indicated by the VB hash being matched:

```
[Constants]
global $ActiveCharacter

[Present]
post $ActiveCharacter = 0

[TextureOverrideDilucVB]
hash = 56159d74
match_priority = 1
$ActiveCharacter = 1
```
The `match_priority` here is just to ensure this effect does not interfere with any loaded Diluc mods – if you are adding this effect as part of a mod and not separately, you won’t need to include it.

18.	Now, there are two ways to we can isolate the shader. The easier of the two is to simply define a custom shader and perform the replacement, then create a `shaderoverride` and only run the custom shader when Diluc is the active character:

```
[ShaderOverrideDilucFlame]
hash = 4d4da8a4cbe1149a
if $ActiveCharacter == 1
	run = CustomShaderDilucFlame
endif

[CustomShaderDilucFlame]
ps = 4d4da8a4cbe1149a-ps_replace.txt
handling = skip
drawindexed = auto
```

This will usually work, but 3dmigoto sometimes does not properly compile the `hlsl` if done this way leading to errors. Also, it will not work with `asm`. But the pros are that the shader can be bundled together in the mod folder with the rest of the mod, and it will not interfere if another mod tries to modify the same shader.

The other method is to pass a custom variable to the shader, and only perform the effect if the variable matches. The next section will go over this in more detail, but essentially you want a section like this for each shader:

```
[ShaderOverrideDilucFlame]
hash = 0fa220b5adced192
x160 = $ActiveCharacter
```

Then to define a new constant in the shader:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988660-d2ffb89b-67bc-4583-afc3-3b5bd6270230.png" width="400"/>
</p>

And only perform the effect if that constant is equal to 1 (e.g. the character is on-screen):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988744-da6a9f46-aa2c-4dc9-8050-7d225adb241e.png" width="400"/>
</p>

With this, Diluc keeps the effect:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988793-72e1a43c-25e5-4b4a-b024-2a2aae0d99ee.png" width="600"/>
</p>

While Hu Tao’s are normal:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988856-0cb0690a-b65f-4db7-96e3-75e0f04dfde5.png" width="600"/>
</p>

## Passing Custom Values into Shaders (Cycling colors)

In this section, I will demonstrate how to load custom values from the `.ini` files to shaders, and how you can use this to effects that cycle between multiple colors. I will also demonstrate how to find the parts of the shader that control emission, something that is more challenging than just effect colors.

This section is medium-advanced difficulty – I will assume you have read most of the previous section, and have at least some basic familiarity with the `.ini` files and shaders (e.g. knowing how to open them, and at least vaguely understand the different parts). Basic programming knowledge will be helpful.

1. Like before, we start by collecting the shader hashes, this time for Zhongli’s pillar:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990319-6809dcff-aa24-46de-8d50-56e21511f384.png" width="600"/>
</p>

Unlike with Diluc, this hash won’t cause the entire pillar to disappear – just the textures. This is because it is drawn using multiple shaders, so even if we skip one parts of the object will still be drawn (in this case, the outline of the pillar remains).

The hash in this case is `4c99fec14dca7797` – press `3` to dump the shader to ShaderFixes.

Our ultimate goal here is to change the color of the yellow geo effect while leaving the other parts the same.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990446-34c57fcf-fb0a-495a-adf0-4c3834236f0f.png" width="200"/>
</p>

2. Opening up the shader, we can see it is more complicated than the previous one with 9 inputs and 6 outputs. This is because the shader is responsible for doing multiple things like drawing the texture, handling the emission, calculating shading, etc.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990505-a83e9b5d-e53f-4d81-8bf1-4b88224c4b3f.png" width="300"/>
</p>

We start by trying the same method as before – setting each of the outputs to constants to learn about what they control.

3. `o0` appears to have something to do with outlines, making them thicker and thinner (a bit hard to see, but can use `F9` to toggle back and forth between modded and unmodded):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990621-0a6ae9bb-00d8-4da2-b533-bc49e373b2d4.png" width="200"/>
</p>

`o1.xyz` seem to correspond to colors RGB like before, and `w` seems to control brightness 

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990706-ae3443bf-e591-49a0-a071-6725d806bb0e.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990739-c4ebdbbe-de56-4f48-a223-6f3dba5c59ce.png" width="600"/>
</p>

`o2` also seems to control color:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990811-c07390a1-2d01-4d98-b220-8914a03b2b34.png" width="600"/>
</p>

`o3`-`o5` are unclear, but seem to affect the line thickness.

However, you may have noticed an issue – all of these options change the color of the entire pillar, not just the yellow geo line! We have to dig a bit deeper to find where that is handled.

4. Before we go further, let me explain the most important symbols in the shader in more detail:

- `v0`,`v1`,`v2`..etc. are the input data in the vb files that is loaded in – that is to say, data related to things like vertex position, vertex colors (different from texture colors!), uv maps, blendweights, etc.
- `o0`, `o1`, `o2`… are the output targets, and are what is actually drawn to the screen (or in the case of vertex shaders `VS`, what is passed to the pixel shader `PS`)
- `t0`, `t1`, `t2`… are the textures – things like dds textures typically, though they can also be buffers in some cases. Whenever you see `ps-t0`, `vs-t0`, `ps-t1`, `vs-t1`, etc. in .ini files this is what they correspond to
- `r0`, `r1`, `r2`… are the registers – these are temporary variables that the shader uses to store the results of calculations
- `cb0`, `cb1`, `cb2`… are the constant buffers – these are values passed by the game to the shader that represent values of the current game state like global location of objects or time passed since the game started

With this in mind, we can focus to the part of the code we are interested in instead of trying to understand all 200+ lines. 

We are interested in the glow of Zhongli’s pillar. Looking at the textures for the pillar, we can see that the diffuse texture contains the glowing part above the alpha layer and is loaded in slot 0 (is the first hash from the hash.json of the pillar, or by looking in a created mod and seeing the diffuse is loaded as `ps-t0`):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991323-68087da3-c621-4238-a994-50e3859837a5.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991357-5a0c0cee-eb64-410c-875f-db1576e107b9.png" width="300"/>
</p>

Hence, we are interested in any part of the code that involves the variable `t0` which corresponds to the diffuse texture. Specifically, we are most interested in anything that involves the w component, since that is what represents the glowing portion.

5. `t0` is loaded in twice in the shader: once around line 100 into the variable `r2`:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991507-ed958308-a38f-40dc-a056-5d663f389052.png" width="400"/>
</p>

And once around line 235 into the variable `r0`:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991578-04bb9823-8bb5-4523-a0f5-2b81e4f32502.png" width="400"/>
</p>

There are ways to tell which is correct by reading the code, but experimenting with each will also work:

Setting `r2.x` as a constant in the first block:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991690-68c079f5-5111-4b09-90ae-e7120338b791.png" width="300"/>
</p>

Turns the pillar green, but leaves the geo effect normal:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991731-c2bbb878-2a7b-401d-8d79-0020e46e92e5.png" width="600"/>
</p>

So we should probably look near the second block instead. The color is most likely represented by a variable with 3 components (one for each color channel), and the nearest one to that block is the `r1` that shows up 3 lines down:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991835-9983b92e-4ee2-4541-b546-2a5a9a560ed8.png" width="300"/>
</p>

If we set `r1.x` to 1 here:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991910-4e13e1e6-ac7c-4b7d-879e-305903c5632a.png" width="300"/>
</p>

We get:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991957-54261de6-263f-491b-bfa9-e1cdd4bf7ffd.png" width="600"/>
</p>

Success! This `r1` value is what controls the RGB of the pillar glow (we set the red component to 0).

(Note: this does not mean that `r1` is always responsible for the pillar glow color everywhere in the code, just that it holds the pillar glow at this specific point in time. Register values are reused by the shader when performing calculations, so the “meaning” of what each one represents can change from line to line unlike the inputs and outputs).

This same basic principle can be used in other situations to find what part of the shader controls what output – start with some component you know is tied to whatever you are looking for (such as a texture, or a specific vb value), then search the surrounding shader code and experiment to find it. 

6. One color is boring however – what if we could set the color to whatever we wanted? Actually, it is possible to pass custom values from the `.ini` files to the shader.

First, define the variables you want to use near the top of the file under 3dmigoto declarations (180 was chosen arbitrarily, though ideally you should pick numbers over 100 so they don’t accidentally interfere with the ones the game uses)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992100-bce019e7-bf54-442e-a4b3-52f856352fb4.png" width="400"/>
</p>

Next, we set the R, G and B below the t0 line we found in the previous part

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992193-e24ab261-b997-4cb7-9a9c-59e02a9bff5f.png" width="300"/>
</p>

(NOTE: the `r1` has an `x`,`z` and `w` component not an `x`,`y`, and `z` component. They still correspond to RGB though, just the letters are different)

Finally, in the .ini we are going to set the three values whenever we see the `IB` for the pillar:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992258-b40caa68-9a4e-4d16-bfd6-63b60ad8e7b5.png" width="200"/>
</p>

(You can find the pillar `IB` by using numpad `7`/`8` to cycle until you find the one that makes the pillar vanish, or by looking in hash.json):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992424-ddbab70d-4fdd-42e8-996b-4c8cde2337f3.png" width="600"/>
</p>

Success! We have set the lines to red:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992488-bc79ec9e-2155-4142-8b00-89cd264c6308.png" width="600"/>
</p>

And we can set them to other colors just by changing the .ini values; this will set them to purple:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992526-3ad6084c-60b6-402d-b265-d59e9aa09757.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992599-f58f70da-1ebb-41c5-8f1f-bf0f690a1c5d.png" width="600"/>
</p>

However, note that this isn’t perfect – we have lost some of the animated effects in exchange for custom colors. I will go over ways to implement animations in the final section of this tutorial.

7. We can still do more with this. One color is great, but what if we could have it automatically cycle between them? 3dmigoto has a special variable called `time` which represents the number of seconds that have passed since the game has started. We can use this to cycle between colors automatically over time:

```
[TextureOverridePillarIB]
hash = 34e18b4f
if time % 3 <= 1
	x180 = 1
	y180 = 0
	z180 = 0
else if time % 3 <= 2
	x180 = 0
	y180 = 1
	z180 = 0
else
	x180 = 0
	y180 = 0
	z180 = 1
endif
```

What this does is take the current time and puts it into 1 of 3 buckets, then sets the pillar to red, green or blue depending on the current time (cycling every 3 seconds). By changing the numbers you can set it to cycle faster or slower, or add/remove colors, etc.

8. Finally, similar to before we can load the shader in the `.ini` instead of putting it in shaderfixes:

```
[TextureOverridePillarIB]
hash = 34e18b4f
run = CustomShaderPillarColor

[CustomShaderPillarColor]
if time % 3 <= 1
	x180 = 1
	y180 = 0
	z180 = 0
else if time % 3 <= 2
	x180 = 0
	y180 = 1
	z180 = 0
else
	x180 = 0
	y180 = 0
	z180 = 1
endif
ps = 4c99fec14dca7797-ps_replace.txt
handling = skip
drawindexed = auto
```

This will mostly work, but there is an glitch in the compilation here that will cause the pillar to leave a residue for ~1 second after disappearing:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992799-823cb1d7-cb97-469a-b1d0-6d80affed8a8.png" width="600"/>
</p>

It is also possible to restrict this shader specifically to when Zhongli is on-field, though in this case I don’t know of any other object that shares this shader so it isn’t as important as it was for Diluc’s flames.
