# Animated Texture Tutorial

Hello everyone. Recently, I wrote a library to add animated texture/glow support (SilentFX) to games supported by 3dmigoto. It currently only works for Stella Sora (extending the RabbitFX library by CaveRabbit), with no current plans to extend to other games at this time.

With this library, you can do things like:

- Texture controlled brightness
- Glow thresholding
- Localized hue shifting
- Linear uv movement (+wrapping)
- Radial uv movement (radius/angle)
- Glow layering
- Automatic glow/hue ramping
- Texture masking

And more! This guide will go over how each of these works via 8 basic examples (intended to explain the basics of how to use the commands), 8 intermediate examples (showing some practical applications to create effects) and 8 advanced examples (more complicated, layered effects that show what the library is capable of)

See the attached example zip the code for all 24 examples. You can use left and right arrow keys when the mod is visible to move through examples covered in this guide, and up and down to move through the sections (Basic/Intermediate/Advanced); the example currently active will be displayed on the bottom left corner.


## Overview of textures and commands 

High-level TLDR of all the commands. Each of these will be explained in more detail in the tutorial section. See addendum for additional notes on texture colorspaces

; Control texture for animations. Red channel controls Glowmap1, Green controls Glowmap2  
; For Glowmaps, `0.0` is always inactive, and `1.0` is always active  
; Blue channel is dynamic hue shift, Alpha channel is mesh cutout  
; Expects BC7 Linear colorspace  
`Resource\RabbitFX\FXMap`  

; RGB channels control color of glow, alpha channel controls glow intensity  
; When both maps overlap, Glowmap 2 takes priority over 1. It is required to specify Glowmap - Glowmap2 is optional  
; Expects BC7 SRGB colorspace  
`Resource\RabbitFX\Glowmap`  
`Resource\RabbitFX\Glowmap2`  


; Hue, saturation, and value shifts for the textures. Affect both glowmap1 and glowmap2  
; h ranges from `0` to `360`, s and v range from `0` to `100`  
`$\rabbitfx\h`  
`$\rabbitfx\s`  
`$\rabbitfx\v`  

; Brightness of the glow. `1.0` is default glow, greater than `1.0` will increase glow intensity  
`$\RabbitFX\Brightness`  

; Time and radius control when the animation is active - a glowmap is active when the corresponding FX channel value is within `[time - radius, time + radius]`  
; Both time and radius must be greater than 0. Time must be between 0 and 1  
`$\RabbitFX\Time1`  
`$\RabbitFX\Radius1`  

; AnimationMode controls how the glow functions. At `0`, it turns on/off; if non-zero, it will ramp up to the maximum value then back down  
; It also serves as a multiplier to the final glow amount. >`1.0` will increase the glow, `0` to `1.0` will decrease it  
; Dynamic hue requires this value to be non-zero, and will gradually hue shift to the target and back  
; Value can be negative; a negative number makes the hue shift occur in the opposite direction, but is otherwise treated the same as if it was positive  
`$\RabbitFX\AnimationMode1`  

; Default behaviour when animation is inactive. Setting `0` has the texture continue to appear, setting `1` makes it vanish  
; Setting `-1` will make only the parts that correspond to an fx value of 0 vanish (ie parts that are always inactive)
; Setting `2` is a special value, which causes glowmap1 to always cutout (intended use is to be used together with `cutout2 = 2` to use glowmap1 as a maskr; see Addendum for details)
`$\RabbitFX\cutout1`  

; Same as above, but for glowmap2. Not required if not setting glowmap2  
; If both glowmap1 and glowmap2 are active, these take priority. If not specified, they are all set to `0` 
; Setting `2` makes only glowmap2 parts that overlap glowmap1 parts appear; see Addendum for details
`$\RabbitFX\Time2`  
`$\RabbitFX\Radius2`  
`$\RabbitFX\AnimationMode2`  
`$\RabbitFX\cutout2`  

; Scrolls UV maps along X and Y by the value specified (1.0 represents a full cycle) for glowmap1 and glowmap2  
; Negative values scroll in the opposite direction  
`$\RabbitFX\movex1`  
`$\RabbitFX\movey1`  
`$\RabbitFX\movex2`  
`$\RabbitFX\movey2` 

; Expands/contracts UVs, and rotates them relative to the centerpoint
; Radius default is 1; smaller decreases size, larger increases size. Angle ranges from 0 to 2pi in radians
`$\RabbitFX\mover1`  
`$\RabbitFX\moveangle1`  
`$\RabbitFX\mover2`  
`$\RabbitFX\moveangle2`  

; Stella Sora only
; Set to 1 to remove object shadow and background shadow
; I added this at the very end, so examples don't use it - it removes the shadowy background you see in a lot of the examples, along with the shadow on the ground
`$\RabbitFX\removeshadow`
`$\RabbitFX\removebackgroundshadow`

; Sets textures and runs texfx  
`run = CommandList\RabbitFX\SetTextures`  
`run = CommandList\RabbitFX\Run`  

; Resets rabbitfx to default after, use after you are done to ensure next calls are clean  
; Should go after any `drawindexed` calls
`run =  CommandList\RabbitFX\Cleanup`

Simple reference example of setting the above commands:

```
Resource\RabbitFX\FXMap = ref ResourceFXMap
Resource\RabbitFX\Glowmap = ref ResourceGlowmap
Resource\RabbitFX\Glowmap2 = ref ResourceGlowmap2

$\RabbitFX\Brightness = 15.0
$\RabbitFX\Time1 = time%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\AnimationMode1 = -1
$\RabbitFX\cutout1 = 1

$\RabbitFX\movex1 = time*0.1%1
$\RabbitFX\movey1 = time*0.1%1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
```


It is also possible to set diffuse and lightmap textures using RabbitFX (e.g. `Resource\RabbitFX\Diffuse`, `Resource\RabbitFX\LightMap`) though this feature is not available for all games (see addendum for details). Some games may use alternate methods, such as slotfix for zzz or ofix for genshin. For this guide, we will be using the following two commands:
```
Resource\RabbitFX\Diffuse = ref ResourceDiffuse
Resource\RabbitFX\LightMap = ref ResourceLightMap
```

To set the diffuse and lightmap textures.


## Basic Use

The following examples will go through the basic usage of the library. I will demonstrate them on a flat plane for simplicity, but the concepts will work on a mesh of any shape. These examples are meant to illustrate how the commands work and so are very basic (mostly using glowing dots for simplicity) - if are already familiar with the library or the notes in the overview make sense you can skip to the intermediate section for some practical examples.

Before we begin, a note on where to call RabbitFX: you want to call it in the override that actually draws the model, before the draw call. Look for where `drawindexed = X, Y, 0` or `drawindexed = auto` is, and it should go right before. That section will also very likely have an ib = ResourceIB section somewhere as well.

Example in stella sora:
```
[TextureOverrideChitoseBodyC]
hash = 5db120a6
match_first_index = 16041
ib = ResourceChitoseBodyCIB
; Code can go here
drawindexed = 6, 0, 0
```

In this case, you can put the code anywhere before the `drawindexed` line.

There may be several of these sections for different body parts; you can set ib = null to see what each part controls. It is also possible to swap the textures between drawindexed calls if making a complex toggle mod using XXMI.



### 1) On/off glow

The first example is a simple on/off glow toggle for a circle. We want the dot to glow for half a second, then not glow for half a second

https://github.com/user-attachments/assets/935e6284-3681-412e-86f0-e488b230634d


(NOTE: The circle is shaking slightly since it is connected to the character and the character is breathing; that movement isn't part of the tutorial, please ignore it)

We use a simple red circle as our Diffuse texture and Glowmap1:

<p align="center">
<img width="250" alt="BasicExample1_1" src="https://github.com/user-attachments/assets/aee9ebac-401c-459a-b16b-917a3274ccc1" />
</p>

(NOTE: For these simple cases, we will use the same Glowmap and Diffuse. We will go over cases where they are different later on)

And for our FX texture, we use a texture with the red channel = 127 (this corresponds to 50% red, or a value of `0.5` since the max is `255`):

<p align="center">
<img width="250" alt="BasicExample1_2" src="https://github.com/user-attachments/assets/fbd7b335-8fa7-4be6-9c6b-e42ce94c5be3" />
</p>

(IMPORTANT! The color of the FX texture is *unrelated* to the colors that show up on-screen. When we use red = 127 here, it isn't related to the actual color red, it just represents a value of 50% in the channel we use to control Glowmap1 - the fact that channel is colored red is irrelevant)

Glowmap1 is active whenever the red channel (in this case, `127` or `0.5`) of the FX texture is in the range `[time + radius, time - radius]`. So if time is currently `0.45` and radius is `0.1`, it would be the range `[0.35, 0.55]` and glow would be turned on (`0.5` is between `0.35` and `0.55`)

(IMPORTANT2! For the FX channels, a channel with value `0` is always inactive and a channel with value `1` is always active regardless if it is in the range `[time + radius, time - radius]`. Be careful when using these `0` or `1`)

(IMPORTANT3! The alpha channel of the fxmap is used to control visibility of the mesh. Alpha = 0 means invisible, alpha > 0 is visible. In the above texture, the entire mesh except for the dot is invisible. This is important when you are applying glow on top of an object where you want the non-glowing parts to still show up - set any non-glowing section to fully black with alpha > 0 to make it still visible)

For time, we want a full cycle to take 1 second. 3dmigoto provides the time variable, but it is in number of seconds since the program started; we want to move it into the range `[0,1]`. We can do that via:

`$\RabbitFX\Time1 = time%1`

which returns the decimal portion of time (`%1` is modulo 1, and basically means "take the remainder after dividing by 1"). This would cause the time to loop between `0` and `1`, with a full loop taking one second (for example, `45.3` seconds since the program started would become the value `0.3`; half a second later would be `45.8` which would become `0.8`; half a second later would be `46.3` which would become 0.3 again)

For the radius, we want the midpoint to be within the range `[time + radius, time - radius]` 50% of the time. Since radius is half the range, we set it to 0.25

The result is that for the first `0.25` seconds, the light will be off. For the next `0.5` s, the light will be on. And for the final `0.25` s the light will be off. Then the cycle repeats, resulting in `0.5`s on, `0.5`s off.


The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceSingleDot
Resource\RabbitFX\Glowmap = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample1

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = time%1
$\RabbitFX\Radius1 = 0.25

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```
(NOTE: The X,Y,Z in `drawindexed` will vary depending on the mod. It may be `drawindexed = auto` in some cases)

(IMPORTANT4! It's always good practice to run `CommandList\RabbitFX\Cleanup` after you are done drawing the mesh. This ensures values don't bleed into future calls. For example, if a future rabbitfx command forgot to set Brightness, this ensures it uses the default (`1.0`) instead of what we set in this example (`5.0`))


### 2) Visible/Nonvisible Glow

The second example is a modification of the first - we will now have the glow active for one second and inactive for one second, and when not active it will vanish completely instead of remaining visible.

https://github.com/user-attachments/assets/1b54d886-ef30-4c50-b847-671347420112

The diffuse/glowmap/FX textures are the same as example 1.

For the time, we now want it to take 2 seconds to cycle. We can do this by dividing by 2, which essentially makes it move twice as slowly (it will now take 2 full seconds to cover the same distance it used to cover in 1 second):

`$\RabbitFX\Time1 = (time/2)%1`

And more generally, the equation is `(time/cycle length)%1`. So if we wanted a cycle to last 4 seconds, it would be `time/4`; if a cycle is half a second, it would be `time/0.5`.

Next, to have the circle vanish, we set cutout1. This value controls what happens when the glow is inactive. When set to `0`, the objects remain visible when inactive; when set to `1`, they vanish.

`$\RabbitFX\cutout1 = 1`

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceSingleDot
Resource\RabbitFX\Glowmap = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample2

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\cutout1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```


### 3) Ramping Glow

For the third example, we will examine how we can cause the glow to ramp up over time instead of being a binary on/off. The diffuse/glowmap/FX textures are the same as example 1.

https://github.com/user-attachments/assets/de3abf99-4266-4d41-a673-62295213e391

The variable `AnimationMode1` controls several things and is quite complex - it is what decides whether the glow behaviour is on/off vs ramp, it is used as a multiplier to the final glow, it allows for dynamic hue shifting and controls the hue shift direction. For now, we just care about the first two aspects - by setting it to a non-zero value, the glow will ramp up to the final value then back down to 0 as it fades out.

`$\RabbitFX\AnimationMode1 = 1`

The value we set it to will also multiply the final glow amount (similar to how alpha works on the glowmap texture). For this case, we will use 1 but setting it higher or lower can be used to give additional control on the glow intensity

The glow at any given time is relative to where the FX channel is in `[time + radius, time - radius]` - it will be minimum at the edges, and maximum at the center.


The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceSingleDot
Resource\RabbitFX\Glowmap = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample3

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```


### 4) Dynamic Hue

For the fourth example, we will slightly modify the third example to show how we can adjust the hue while the glow is ramping up.

https://github.com/user-attachments/assets/b56577fc-c121-4110-8866-4dea51df9e31

For this example, we change the FX map and give it a blue channel of `63` (`0.25`). The blue channel controls how much hue shift is applied when it is active - `0.25` means that it applies a maximum shift of `25%` or 90 degrees.

<p align="center">
<img width="250" alt="BasicExample4_1" src="https://github.com/user-attachments/assets/8cdc0a84-531b-4342-bed0-8251a91c7791" />
</p>

The latter two abilities of `AnimationMode1` are related to hue shifting. When non-zero, if blue channel is also non-zero, the hue shift will gradually increase to the value of the blue channel (reaching maximum at the same time the brightness reaches maximum).

If we set `AnimationMode1` negative, it reverses the direction of the hue shift (but otherwise acts the same as if it was positive). So with a red circle, a AnimationMode will shift it towards yellow while a negative one will shift it towards purple

<p align="center">
<img width="235" height="196" alt="BasicExample4_2" src="https://github.com/user-attachments/assets/e23bedfc-99d0-4821-ada3-2f631320aa0d" />
</p>


The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceSingleDot
Resource\RabbitFX\Glowmap = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample4

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/4)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\AnimationMode1 = -1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```

Aside: that there is an alternate way to get this effect - instead of using the blue channel of the FX texture, we could instead pass a number to `$\rabbitfx\h`. This will work in this case because we are hue adjusting the entire texture; it won't work in cases where we only want to hue adjust part of it. For example, the following is something that cannot be done using only `$\rabbitfx\h` since different parts get different shifts:

https://github.com/user-attachments/assets/275b0498-1bb8-4781-996f-9e7b2b89c121

If your goal is to continuously shift the colors to make a rainbow effect however, it is better to use a texture that already has a rainbow gradient and use `$\rabbitfx\h` (see advanced application section for example)

### 5) Second Dot

Next, we demonstrate how we can use two glow maps simultaneously. We will add a second dot that is flashing twice as fast as the first one.

https://github.com/user-attachments/assets/10157072-53d7-4994-9879-6a322e45be0c

(Note: the residue that appears briefly is due to dds compression issues. See addendum for ways to minimize this effect) 

All of the animation parameters and glowmaps have secondary versions that end with "2" but otherwise function the same as the ones with "1". So we can set the second dot with:

```
Resource\RabbitFX\Glowmap2 = ref ResourceDoubleDot

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time2 = time%1
$\RabbitFX\Radius2 = 0.25
$\RabbitFX\cutout2 = 1
```

We also need to update the fx map - the green channel controls Glowmap2 (and functions the same way as Glowmap1):

<p align="center">
<img width="250" alt="BasicExample5" src="https://github.com/user-attachments/assets/29860a1d-7f15-4d5e-937e-28be7b8fbab7" />
</p>

The reason we need to use a second glowmap here is because we want the two dots to flash at different speeds. If they were the same speed, we could just add the dot to the first glowmap. Note that the library is currently limited to a max of two independent glowmaps - while adding a third dot that blinks with a different speed to the first two isn't impossible, it's not as simple since there is no Glowmap3 and would require some very creative coding. I recommend trying to limit any animations to at most two independent glowmaps/speeds.

In situations where the effects from glowmap1 and glowmap2 overlap, glowmap2 will take priority. For cutout, think of the textures being layered like glowmap2 > glowmap1 > diffuse - if cutout2 is set, when glowmap2 is inactive you will essentially be able to see through it to the layer "below". So if glowmap1 is active or has cutout1 not set, you will see glowmap1 below. If glowmap1 is inactive and has cutout1 set, you will either see the original diffuse texture (if alpha > 0 on glowmap1) or the mesh will be cut out and not visible (alpha = 0).

See Addendum for a more detailed list of what texture is visible under what circumstances.


The final code is:
```
Resource\RabbitFX\Diffuse = ref ResourceDoubleDot
Resource\RabbitFX\Glowmap  = ref ResourceDoubleDot
Resource\RabbitFX\Glowmap2 = ref ResourceDoubleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample5

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\cutout1 = 1
$\RabbitFX\AnimationMode1 = -1
$\RabbitFX\Time2 = time%1
$\RabbitFX\Radius2 = 0.25
$\RabbitFX\cutout2 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```


### 6) Multiple Glowing Dots in Sequence

Gradually getting more complex, in the next example we create a basic sequence by setting different circles to different channel values

https://github.com/user-attachments/assets/f6558c30-d5ec-4093-8e6c-58c9a58e6ed3

We now have 3 dots - I have set them to values of 60, 120 and 180 in the red channel.

<p align="center">
<img width="250"  alt="BasicExample6" src="https://github.com/user-attachments/assets/cd5e2d2e-9295-467d-b363-fa400aa6e5b0" />
</p>

Trying something like (I set radius to 0.3 to highlight a few issues that we will solve shortly):
```
Resource\RabbitFX\Diffuse = ref ResourceTripleDot
Resource\RabbitFX\Glowmap = ref ResourceTripleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample6

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/3)%1
$\RabbitFX\Radius1 = 0.3
$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X,Y,Z
run = CommandList\RabbitFX\Cleanup
```
Almost works, but you may notice some issues:

https://github.com/user-attachments/assets/8ca3f2ad-8fd6-49ac-ba82-27e7a5e46562

The first issue is that there is a slight overlap between the lights being on; this is because the radius is too large and the ranges are overlapping. We can fix this by making sure the radius is lower than the distance between the channels (in this case, `0.25`).

The second issue, the behaviour of the top and bottom dot is a bit odd. Instead of starting from 0, the glow seems to start partially active. And when the cycle reaches the end point, the glow suddenly turns off instead of gradually reaching 0.

This is due to behaviour near the edges for ramping glow - something with a red channel of `60` on the fx map corresponds to ~`0.25`. The amount of glow is basically where this number is in the range `[time-radius, time+radius]`, reaching the minimum value at the edges. In this example, time starts at 0, so the range is `[-0.3, 0.3]` so the point `0.25` is already within the range when the animation starts

The same issue is causing the issue for the last dot - when time reaches `1.0`, it's still in the range `[time-radius, time+radius]` so it suddenly stops.


There are a couple of solutions here. First is to adjust the channel to be further from the edges. Second is to shrink the radius. Both of these basically ensure the dot doesn't remain active when the cycle begins or ends. But it might mess with spacing or timing

The more general solution is to adjust the start and endpoints of time. I mentioned before that time needs to be between `0` and `1`, but that is only half-correct. It will still function if you pass something below `0` or above `1`, it just won't activate any glowmap unless it is in the range `[0,1]`. But we *can* use this to create a buffer zone for the start and stop points.

Let's say for example we want time to go from `-0.5` to `1.5`, while still keeping the same overall cycle time. First, we multiply the output of `(time/3)%1` by `2` to put it in the range `[0,2]`; then, we subtract 0.5 to put it in the range `[-0.5, 1.5]`

Or more generally the equation is: 

`(upperbound-lowerbound)*((time/cyclelength)%1) + lowerbound` 

for creating a cycle between lowerbound and upperbound with length cyclelength. 

Just be aware that since we are changing the size of the range, you may need to adjust the cyclelength timing (even though this cycle still takes `3` seconds, it spends `1.5` seconds out of bounds and `1.5` seconds in-bounds - if you wanted `3` seconds in-bounds, you would need a cyclelength of `6` instead). Also be careful with setting lowerbound and upperbound too far away from the original 0 and 1 boundaries. You can see that with `0.5`, the animation will already spend more than half the time inactive - something like `-0.1` and `1.1` is probably better in this case to minimize that effect:

`$\RabbitFX\Time1 = 1.2*((time/3)%1) - 0.1`

We also adjust the radius to be `0.1`:

https://github.com/user-attachments/assets/b3bf7a1f-ab0a-4af1-b09d-86c3af3b252c

That fixes the issue with the edges, but it is still the wrong direction. The issue here is that time is going from 0...1 when it should be going from 1...0. This has a simple solution - just do 1-time instead of time. So the general question to reverse the direction is:

`(upperbound-lowerbound)*(1 - (time/cyclelength)%1) + lowerbound`

or in this case:

`$\RabbitFX\Time1 = 1.2*(1-(time/3)%1) - 0.1`

https://github.com/user-attachments/assets/de017ad4-be39-48a6-9ae8-ec55b645462e

(You could also flip all the channel values in the FX map, both ways will work)

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceTripleDot
Resource\RabbitFX\Glowmap = ref ResourceTripleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample6

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = 1.2*(1-(time/3)%1) - 0.1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = X, Y, Z
run = CommandList\RabbitFX\Cleanup
```


### 7) Basic Scrolling Movement

Now, we show how to move textures vertically and horizontally.

https://github.com/user-attachments/assets/44391b99-8bcb-4c82-97ae-e42a095a81eb

There are two values associated with movement: `moveX1` and `moveY1` (+the corresponding ones for glowmap2, moveX2 and moveY2). These represent the amount to shift the UV maps of the texture in the X and Y direction - the exact direction depends on how the mesh UV is laid out (positive might be scrolling left or right, you will need to double check. By default, it should be right and up for most uv maps). You can pass in any number, but note that the range is `[-1.0, 1.0]` - anything with an absolute value larger than `1.0` will just be shifted back into this range (so `1.6` will be treated as `0.6`, `-5.3` is `-0.3`, etc. Think of `1.6` as meaning "move 1 full cycle then 0.6 of a cycle" which results in a movement of 0.6)

By setting moveX1 and moveY1 to static values, we can give a constant offset; by setting them to dynamic ones, we can create movement. The simplest dynamic value to use is time:

`$\RabbitFX\movex1 = (time/5)%1`

This will cause the dot to move to the right, taking 5 seconds to return to where it started. Meanwhile:

`$\RabbitFX\movey1 = 1-(time/20)%1`

This will cause the dot to slowly move down, taking 20 seconds to complete a full cycle.

It's possible to use this in tandem with the previous effects and a second glowmap to create fairly complex movement - we will explore some more advanced applications in the intermediate and advanced sections

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample7

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\AnimationMode1 = 1

$\RabbitFX\movex1 = (time/5)%1
$\RabbitFX\movey1 = 1-(time/20)%1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```


(Note: ResourceBlack is just a full-black texture. Some characters use diffuse alpha as cutout already, so by passing a full-black texture we avoid that issue. If you are having an issue similar to this:

https://github.com/user-attachments/assets/c4df560a-4359-4863-ba81-95ddc5ac41e8

try messing with the Diffuse texture)


### 8) Combined

In this last example, I'll use every single feature: one set of circles will be gradually travelling to the right, while glowing in sequence; another will be moving diagonally and popping in and out of existence

https://github.com/user-attachments/assets/ec91c6af-4569-4f0f-b846-af12496e6337

For the circles moving to the right, I'll use the triple dot from example 6; for the travelling dot, it will be the one from example 7.

The new FX map is:

<p align="center">
<img width="250"  alt="BasicExample8" src="https://github.com/user-attachments/assets/304ab45f-bd11-42e9-acc1-b8ac37b01809" />
</p>

The final code (mostly a combination of examples 6 and 7) is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceTripleDot
Resource\RabbitFX\Glowmap2 = ref ResourceSingleDot
Resource\RabbitFX\FXMap   = ref ResourceBasicExample8

$\RabbitFX\Brightness = 10
$\RabbitFX\Time1 = 1.2*(1-(time/3)%1) - 0.1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\AnimationMode1 = 1
$\RabbitFX\Cutout1 = -1

$\RabbitFX\Time2 = (time/2)%1
$\RabbitFX\Radius2 = 0.25
$\RabbitFX\AnimationMode2 = 1

$\RabbitFX\movex1 = (time/5)%1

$\RabbitFX\movex2 = (time/10)%1
$\RabbitFX\movey2 = 1-(time/2)%1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```

The only thing to note here is we use `-1` for cutout, which works similarly to `0` except it cuts out any parts that are always inactive (if we didn't set this, then the green parts would appear black since they have alpha > 0)


## Intermediate Examples

The following examples will show some more complex use cases that use multiple features at the same time. I would recommend at least skimming the basic examples in the first section to learn the syntax before trying these. Most of these intermediate examples will still be using solid objects like planes or spheres, but the concepts can be applied to any mesh shape (the plane is to help visualize how the UVs will function on more complicated shapes - when troubleshooting complicated animations, it can be helpful to think of how it will look like on a flat surface). See the advanced section for examples with non-basic geometry.


### 1) Stoplight

The first intermediate example will be a warm up - a modification of Beginner example #6 to create a stoplight. It will flash green, yellow, then red in sequence with yellow being shorter (5 seconds total loop, with red and green taking 2 second and yellow 1 seconds), the first practical application of the tool:

https://github.com/user-attachments/assets/86ff78de-33ee-4830-a4e0-bddf9c8b044a

We start with the code from example 6. First, we recolor the glowmap to match the stoplight colors:

<p align="center">  
<img width="350" alt="IntermediateExample1_1" src="https://github.com/user-attachments/assets/4d639315-6635-4af6-8a9f-f059e2c455bb" />
</p>

The green and red dots are on glowmap1, while the yellow dot is on glowmap2. Note that we could have also made all 3 a single color then used the hue shift feature of the FX map to accomplish the same thing. Which way is better depends on the use case.

Next, we adjust the FX map. We want the yellow light (middle) to be on a separate glowmap since it will be active for a shorter period than the other two lights, but otherwise the values remain the same. Unlike previous examples, we want the light to be active when the cycle starts/ends, so we choose `50` and `205` for the color values of red channel (`0.2` and `0.8` of `255`; we will show why these numbers are used when we talk about timing). The yellow light should be halfway in the cycle, so we pick `127` as the green channel.

<p align="center">  
<img width="250" alt="IntermediateExample1_2" src="https://github.com/user-attachments/assets/28cb31cb-00c1-4503-886a-62fe3acc2a31" />
</p>

Now, we need to get the timing correct. All lights will be operating on a 5 second loop, but we want glowmap2 to be active for only half the time of glowmap1. We can do this by having `radius2` be half the size of `radius1`. For `radius1`, since we want each light to take up 2 seconds out of 5 seconds, it means the radius should cover 40% of the total range or a `radius1` of 0.2 (and thus, to ensure the lights are active at the start and end of the cycle they must be within 0.2 of the edges). `Radius2` is thus 0.1.

https://github.com/user-attachments/assets/ba1f585e-3bee-44f1-a4bf-40522c049297

Now that the logic is correct, we adjust the location and sizes of the dots to match up with the (completely non-sus) stoplight:

<p align="center"> 
<img width="250" alt="IntermediateExample1_3" src="https://github.com/user-attachments/assets/11876bda-5f42-44a2-a2c8-1bbc1691814d" />
<img width="250" alt="IntermediateExample1_4" src="https://github.com/user-attachments/assets/e65cd992-3d33-4316-82a7-3c81af071127" />
<img width="250" alt="IntermediateExample1_5" src="https://github.com/user-attachments/assets/f239dfdb-aa22-4c72-91b2-159238959475" />
</p>

The only thing of note here is to make sure the FX map (3rd image) has black wherever the stoplight mesh is - otherwise, it will be cut out and not visible (an alternate option is to put it on the diffuse map instead and cut out to display it).

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceStoplight1
Resource\RabbitFX\Glowmap2 = ref ResourceStoplight2

Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample1

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/5)%1
$\RabbitFX\Radius1 = 0.2

$\RabbitFX\Time2 = (time/5)%1
$\RabbitFX\Radius2 = 0.1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```


### 2) Gradient Glow

The next intermediate example will show how to create a smoother version of movement compared to the on/off we have been using so far. We use it to make a glowing animated circuit:

https://github.com/user-attachments/assets/8a1f9616-63e5-41b6-a52e-a04f2a565631

In the earlier sections, we used discrete values of FX channels to make things blink in sequence. We can use gradients instead for a smooth motion. Assuming time is increasing from 0 to 1, then FX values closer to 0 will turn on sooner than ones closer to 1, and the amount of the effect active at any given time depends on the size of the radius. An example of an FX map with this property, where the further points from the "front" of the texture have lower values:

<p align="center"> 
<img width="300" alt="IntermediateExample2_1" src="https://github.com/user-attachments/assets/fc154717-9d89-4d82-bdc0-801bad1a8dd8" />
</p>

There are a few common issues to be aware of: if your animation is behaving oddly near the edges, make sure the lowest and highest FX channels don't begin/end within the range `[time-radius, time+radius]` (see basic example 6 for details). If the movement isn't smooth, double check you are saving the format as linear (srgb will create a curve of values which will cause the speed to be non-uniform) and that the gradient is smooth (depending on how you create it, it might end up scrunched near the edges).

https://github.com/user-attachments/assets/6b9191e4-dfb6-4c38-a298-756e006079a8

Now, let's go over something that is slightly tricky - what if we want the glowing part to be green when active but gray when inactive? This is actually more complicated than it sounds - cutout will make the mesh invisible when not active, instead of displaying the original diffuse (see Addendum for full combination of situations).

We can't really use the hue shift here, since there is no way to shift from gray -> green. We can instead put it on Glowmap2 and have it defer to Glowmap1 which is just a gray line, but that requires us to sacrifice an entire glowmap (and we need glowmap2 later for other stuff).

The overall simplest way to do this that keeps flexibility is to do a second draw; we first draw the texture with the gray lines, then draw the animated ones on top with cutout.  So the code would look like:

```
Resource\RabbitFX\Glowmap = ref ResourceCircuitInactive
Resource\RabbitFX\FXMap   = ref ResourceBlack
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0

Resource\RabbitFX\Glowmap = ref ResourceCircuitTwoLines
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample2_1
$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/5)%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 1
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
```

The first call draws the inactive lines, while the second call is drawing the glowing lines on top while cutting out any non-active components. This is a very common use case, and can actually be used to go above the default limit of two maps if your animation is complex enough to require it (e.g. normally you are limited to only two speeds, but you can in theory create as many as you want by just drawing the mesh multiple times and overlapping them. Just be careful if the mesh is very complex since repeating large `drawindexed` can lead to performance issues). We will see some cases in the advanced section where we use this trick.

https://github.com/user-attachments/assets/08b966d6-8ebe-4e21-870f-4c16af729f65


To control how much of the line is visible at once, one can either change the radius (like `0.1` vs `0.4` - a smaller radius means less is active) or make the gradient less steep (a gradient between `30` and `230` will cause a radius of `0.1` to only have `10%` active at once; a gradient between

Smaller radius/steep gradient:
<p align="center"> 
<img width="300" alt="IntermediateExample2_2" src="https://github.com/user-attachments/assets/7cd0ca15-c683-4947-b756-59494935ac71" />
</p>

Larger radius/flat gradient:
<p align="center"> 
<img width="300" alt="IntermediateExample2_3" src="https://github.com/user-attachments/assets/9bea5ae9-be22-4f20-9bb0-9780d9151d98" />
</p>

It's also possible to use a non-linear gradient to cause the size of the line to grow and shrink as it travels.


The speed the effect travels depends on the value we pass in to time - the faster `time` moves between `0` and `1` (ie the shorter the cycle time), the faster the line will appear to move

3 second cycle:

https://github.com/user-attachments/assets/424dc7de-8054-42f1-8839-86124a49370a

10 second cycle:

https://github.com/user-attachments/assets/783b93c8-12ed-49c0-a8ff-c0a9d687d24b


Since the gradient can be controlled via texture, the size of the line can be different between two lines even if they are on the same glowmap. In comparison, if one wanted a different speed one has to use glowmap2 instead (and we can have a maximum of two distinct speeds in any animation, ignoring any trickery like multiple overlapping draws).

To demonstrate this concept, we set the two glowmaps to different speeds and have an assortment of different lines:

<p align="center"> 
<img width="300" height="815" alt="IntermediateExample2_4" src="https://github.com/user-attachments/assets/67fac20c-55f0-4876-a562-b0d81d4119f4" />
</p>

https://github.com/user-attachments/assets/e08b43ad-6bde-4375-9f6d-85d56dbd0449

The last intermediate example (number 8) and first expert example (number 1) will demonstrate how to put this effect on a character to create the animated effect that is similar to the one from the effect tutorial.

The final code is

```
Resource\RabbitFX\Diffuse = ref ResourceBlack

Resource\RabbitFX\Glowmap = ref ResourceCircuitInactive
Resource\RabbitFX\FXMap   = ref ResourceBlack
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0

Resource\RabbitFX\Glowmap = ref ResourceCircuitTwoLines
Resource\RabbitFX\Glowmap2 = ref ResourceCircuitMultiLinesRed

Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample2_2
$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/7)%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 1

$\RabbitFX\Time2 = (time/4)%1
$\RabbitFX\Radius2 = 0.05
$\RabbitFX\Cutout2 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0

run = CommandList\RabbitFX\Cleanup
```



### 3) Rotating emoji sphere

An example of using this animation on a non-flat texture, to create the illusion of a rotating sphere.

https://github.com/user-attachments/assets/b4080d32-e777-491a-86d4-37d50f7d64b9

Instead of using a flat plane, we export a standard blender sphere. We want the face to appear on sides of it, so we can use a texture like this as our glowmap:

<p align="center"> 
<img width="250" alt="IntermediateExample3_1" src="https://github.com/user-attachments/assets/068e8f91-d06e-4226-8283-b6396a473dd7" />
</p>

For the FX map, it will just be all black - remember that we don't need to use glow in all our textures, it's possible to use this library purely for animation.

<p align="center"> 
<img width="250" alt="IntermediateExample3_2" src="https://github.com/user-attachments/assets/135c49b6-a847-471f-8c48-e1ea274e05b8" />
</p>

Finally, to make the image scroll we set `movex1` to cycle every 5 seconds with `(time/5)%1`

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceThinkingEmoji
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample3

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\AnimationMode1 = 1

$\RabbitFX\movex1 = (time/5)%1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 2880, 22944, 0
run = CommandList\RabbitFX\Cleanup
```

It's also possible to do this by creating a rotation shader and spinning the points (and would be required if the sphere had additional parts sticking out), but for a uniform sphere this way is lighter in terms of both code and performance impact.


### 4) Glowing Eyes Sucrose

The title says it all. Run

https://github.com/user-attachments/assets/ebd8be71-297c-4252-8e30-3982638f2dae

Here, we demonstrate how to create basic animated tattoos.

For Glowmap1, we use a static image of sucrose. For Glowmap2, we use the glowing eyes overlay. We want sucrose to always be visible (of course), so the FX map will all black on any section that overlaps with her. For the eyes, we want gradually increase in intensity from the inside outwards, then fade back the same way - we can use the same idea as example 2, by using a gradiant on the FX map (note that we try to avoid going all the way to the edges (`0` and `255`) so we don't get any odd edge behaviour):

<p align="center"> 
<img width="250" alt="IntermediateExample4_1" src="https://github.com/user-attachments/assets/4dd0d7b9-8b81-4d8c-9d64-222029c3a2df" />
<img width="250" alt="IntermediateExample4_2" src="https://github.com/user-attachments/assets/97f6f028-7ef9-4ee6-9bfe-558620b825d4" />
<img width="250" alt="IntermediateExample4_3" src="https://github.com/user-attachments/assets/6362e1fc-0049-4392-a9e7-171ab90a8c3a" />
</p>

https://github.com/user-attachments/assets/ed5de0d7-7c93-4752-acf0-174f571ecdc1

This will half work, but the problem is that it will fade from the inside out, which is the opposite of what we want (we want it to appear inside-out, then fade outside-in). We will go over how to do this in more detail in example 6, but for now the basic idea is that once we reach the maximum glow, we want the time variable to start travelling backwards instead of continuing forward. That will ensure the center remains in the range, while the edges gradually fade

The simplest way to do this is with an if/else statement, that reverses the direction when time is above 0.5:

```
if 1.3*((time/6)%1)-0.3 > 0.5
	$\RabbitFX\Time2 = 1.3*(1 - (time/6)%1)-0.3
else
	$\RabbitFX\Time2 = 1.3*((time/6)%1)-0.3
endif
```

Also note that we still have an entire glowmap to play around with - we can add some light gradient glow effect on sucrose herself by adjusting the FX map:

<p align="center"> 
<img width="250" alt="IntermediateExample4_4" src="https://github.com/user-attachments/assets/cb75eb81-bbe4-4697-8416-5220cbce85ca" />
</p>

Which will cause some of the seams on her clothing to have a moving glow (as you can see in the original video at the top of this example).


### 5) Digital Clock

We create a simple digital clock that counts seconds up to 60. This example shows how you can mix this library with ini coding to create more complex effects (remember that ini coding can be very powerful! Lots of basic animations and effects can be created with nothing but if/else statements and texture swaps).

https://github.com/user-attachments/assets/8e59a437-0f36-465c-b2fa-58b7a4a738b6

To start, we will count from 0 to 9. This requires 10 images in total (20 if you also count the corresponding FX textures):

<p align="center"> 
<img width="500" alt="IntermediateExample5" src="https://github.com/user-attachments/assets/24f1b320-e9d8-4d21-bac3-b8a61446c65d" />
</p>

Next, we decide which to load into the glowmap depending on the value of time.  A cycle lasts 10 seconds, and each number gets a one-second slice of that time. So we can do something like:

```
$digit = (time/10)%1
if $digit >= 0 && $digit < 0.1 
	Resource\RabbitFX\Glowmap = ref Resource0Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_0
elif $digit >= 0.1 && $digit < 0.2 
	Resource\RabbitFX\Glowmap = ref Resource1Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_1
elif $digit >= 0.2 && $digit < 0.3 
	Resource\RabbitFX\Glowmap = ref Resource2Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_2
elif $digit >= 0.3 && $digit < 0.4 
	Resource\RabbitFX\Glowmap = ref Resource3Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_3
elif $digit >= 0.4 && $digit < 0.5 
	Resource\RabbitFX\Glowmap = ref Resource4Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_4
elif $digit >= 0.5 && $digit < 0.6 
	Resource\RabbitFX\Glowmap = ref Resource5Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_5
elif $digit >= 0.6 && $digit < 0.7 
	Resource\RabbitFX\Glowmap = ref Resource6Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_6
elif $digit >= 0.7 && $digit < 0.8 
	Resource\RabbitFX\Glowmap = ref Resource7Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_7
elif $digit >= 0.8 && $digit < 0.9 
	Resource\RabbitFX\Glowmap = ref Resource8Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_8
elif $digit >= 0.9 && $digit < 1.0 
	Resource\RabbitFX\Glowmap = ref Resource9Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_9
endif
```

Which will load each digit in sequence for 1 second:

https://github.com/user-attachments/assets/50c86381-06db-44fe-b573-ad9b48ec110b

Next, we deal with the left digit. At first, you might think that the simplest way is to just create another set of 10 textures but there is an easier way - we can use the exact same set but give them all a `movex1` offset to put them in the correct place. We can actually re-use the set code from the right digit if we move it into a command list too:

```
$\RabbitFX\Brightness = 5.0
$\RabbitFX\movex1 = 0.35
$digit = (time/100)%1
run = CommandListDisplayDigit
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
```

Note that we are actually drawing the mesh twice - once for the right digit, and once for the left. You may need to set some values again like `$\RabbitFX\Brightness` between calls (and you only need to call `Cleanup` once at the very end).

This will create a timer that counts between `0` and `99` which is close to what we want but not quite - we want it to cycle between `0` and `60`. Your first thought might be to change `/100` to `/60` to swap it to a 60 second cycle, but that won't work since each slice will be 6 seconds and not 10 seconds. The actual solution is to use

`$digit = (time/100)%0.6`

iInstead, which keeps the slices at 10 seconds but constrains the output to `[0,0.6]` instead of `[0,1.0]` (ie only the first 6 digits).

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack

$digit = (time/10)%1
run = CommandListDisplayDigit
$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = 0
$\RabbitFX\Radius1 = 0.2
$\RabbitFX\movex1 = 0.05
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0

$\RabbitFX\Brightness = 5.0
$\RabbitFX\movex1 = 0.35
$digit = (time/100)%0.6
run = CommandListDisplayDigit
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup


[CommandListDisplayDigit]
if $digit >= 0 && $digit < 0.1 
	Resource\RabbitFX\Glowmap = ref Resource0Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_0
elif $digit >= 0.1 && $digit < 0.2 
	Resource\RabbitFX\Glowmap = ref Resource1Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_1
elif $digit >= 0.2 && $digit < 0.3 
	Resource\RabbitFX\Glowmap = ref Resource2Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_2
elif $digit >= 0.3 && $digit < 0.4 
	Resource\RabbitFX\Glowmap = ref Resource3Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_3
elif $digit >= 0.4 && $digit < 0.5 
	Resource\RabbitFX\Glowmap = ref Resource4Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_4
elif $digit >= 0.5 && $digit < 0.6 
	Resource\RabbitFX\Glowmap = ref Resource5Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_5
elif $digit >= 0.6 && $digit < 0.7 
	Resource\RabbitFX\Glowmap = ref Resource6Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_6
elif $digit >= 0.7 && $digit < 0.8 
	Resource\RabbitFX\Glowmap = ref Resource7Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_7
elif $digit >= 0.8 && $digit < 0.9 
	Resource\RabbitFX\Glowmap = ref Resource8Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_8
elif $digit >= 0.9 && $digit < 1.0 
	Resource\RabbitFX\Glowmap = ref Resource9Right
	Resource\RabbitFX\FXMap = ref ResourceIntermediateExample5_9
endif
```

### 6) DVD Logo

Next, we explore other types of movement beside scrolling - more complex movement is possible instead of just looping around the screen. We use this to animate a DVD logo in various ways

https://github.com/user-attachments/assets/e13c3dce-5e28-4705-841d-685f13a43468

First, let's start with something basic - instead of having the DVD logo loop, we are going to have it hover up and down in place.

The key here is instead of passing something like `(time/5)%1`, we are going to cause it to reverse directions when it reaches a certain point. We already saw an example in the Sucrose example, and we examine it more here. Basically, we want to swap to using `1-(time/N)%1` when we reach the half-way point, where `N` is the cycle length - that will cause the direction to reverse, until it reaches the lowest point again creating a "bobbing" motion

So let's say we want the dvd logo to go up and down by a total of `0.15` (ie we want it to travel between `-0.15` and `+0.15`) over the course of five seconds. We set the lower bound to `-0.15` and the upper bound to `+0.45` (*not* `+0.15`, since we want to travel back upon reaching `+0.15` which means we need an extra `0.3` of space to return to `-0.15`)

Using the equation from the basic section, that gives us `0.6*((time/5)%1) - 0.15`. Next, we do an if statement to check if we are above `+0.15` and if so reverse direction:

```
if 0.6*((time/5)%1) - 0.15 > 0.15
	$\RabbitFX\movey1 = 0.6*(1 - (time/5)%1) - 0.15
else
	$\RabbitFX\movey1 = 0.6*((time/5)%1) - 0.15
endif
```

https://github.com/user-attachments/assets/eb3c1289-7f61-422b-8754-26565066157e

This works, but the movement is a bit stiff - if our goal is to create a "bobbing" motion (like being on the waves), then it should spend more time at the edges and less time in the center. This is more complicated, however, and is something we will cover in the advanced section (see the Halo example specifically) - for now, this motion is good enough for our purposes.

Now that we know the basics of how to move an object back and forth, let's implement the bouncing DVD logo from the original video. To move diagonally, we set movement in X and Y to be equal. Assuming the dvd logo starts in the center, the edges of X and Y are located at -0.5 and 0.5. So in other words, we want to apply the concepts from the previous code block but to both directions and with the range `[-0.5, +0.5]` (while remembering that the logo itself has a thickness of about ~0.15, so the actual range is `[-0.35, 0.35]`):

```
if 1.35*((time/5)%1) - 0.35 > 0.35
	$\RabbitFX\movex1 = 1.35*(1 - (time/5)%1) - 0.35
	$\RabbitFX\movey1 = 1.35*(1 - (time/5)%1) - 0.35
else
	$\RabbitFX\movex1 = 1.35*((time/5)%1) - 0.35
	$\RabbitFX\movey1 = 1.35*((time/5)%1) - 0.35
endif
```

This works, but the movement is sort of boring:

https://github.com/user-attachments/assets/27cb0935-2f73-4c17-bbf5-fd2edf63e3ea

Since the DVD logo starts in the center, it will just bounce between corners. For more interesting movement, we can add an initial offset to one of the directions (by shifting one of the time variables by 1 second relative to the other):

```
if 1.35*(((time+1)/5)%1) - 0.35 > 0.35
	$\RabbitFX\movex1 = 1.35*(1 - ((time+1)/5)%1) - 0.35
else
	$\RabbitFX\movex1 = 1.35*(((time+1)/5)%1) - 0.35
endif
if 1.35*((time/5)%1) - 0.35 > 0.35
	$\RabbitFX\movey1 = 1.35*(1 - (time/5)%1) - 0.35
else
	$\RabbitFX\movey1 = 1.35*((time/5)%1) - 0.35
endif
```

This creates the motion we saw in the original video where the DVD logo bounces around the sides.

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceDVD
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample6

$\RabbitFX\Brightness = 5.0
$\RabbitFX\Time1 = (time/2)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\AnimationMode1 = 1

;$\RabbitFX\movex1 = -(time/5)%1

if 1.35*(((time+1)/5)%1) - 0.35 > 0.35
	$\RabbitFX\movex1 = 1.35*(1 - ((time+1)/5)%1) - 0.35
else
	$\RabbitFX\movex1 = 1.35*(((time+1)/5)%1) - 0.35
endif
if 1.35*((time/5)%1) - 0.35 > 0.35
	$\RabbitFX\movey1 = 1.35*(1 - (time/5)%1) - 0.35
else
	$\RabbitFX\movey1 = 1.35*((time/5)%1) - 0.35
endif

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```



### 7) Lightning Clouds

In this example, we show how it is possible to layer the two glowmaps to create certain effects such as scrolling clouds with lightning. This is a more complicated version of intermediate example 2; we add movement to the gradient effects and demonstrates how multiple effects can be layered:

https://github.com/user-attachments/assets/f4b22fc8-219c-484b-b9ab-8e566bae355b

This effect consists of two layers: the first is the scrolling clouds, and the second is the lightning effects. The FX textures look like:

<p align="center"> 
<img width="300" alt="IntermediateExample7_1" src="https://github.com/user-attachments/assets/9552ed2c-6fde-4541-9b95-4ba6ba23a021" />
<img width="300" alt="IntermediateExample7_2" src="https://github.com/user-attachments/assets/8016a618-7b87-46c4-b002-1ef42ffc88b1" />
</p>

Combined:

<p align="center"> 
<img width="300" alt="IntermediateExample7_3" src="https://github.com/user-attachments/assets/d5f021dd-09a7-4ae2-9225-b94f529038d3" />
</p>

Trying this out, we see that it has an issue - since glowmap2 takes priority over glowmap1, the lightning will appear even outside the clouds:

https://github.com/user-attachments/assets/343554c4-168e-4cb7-80f3-8a35fbd8f703

If the background was a static color, we could do something like draw glowmap1 -> draw glowmap2 -> draw background, but since it is a cutout that won't work (once we draw glowmap2, we can't "erase" it anymore; we can only draw more things on top). To get around this, we use a value for `cuout2` we haven't seen so far: `cutout2 = 2`. This causes glowmap2 to *only* be active whenever glowmap1 is also active, and results in the lightning only appearing when over the clouds.

The final code is:

```
[CommandListIntermediate7]
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceCloud
Resource\RabbitFX\Glowmap2 = ref ResourceLightning
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample7_1

$\RabbitFX\Brightness = 1.0
$\RabbitFX\Time1 = (time/5)%1
$\RabbitFX\Radius1 = 0.25
$\RabbitFX\Cutout1 = 1
$\RabbitFX\movex1 = -(time/8)%1

$\RabbitFX\Time2 = (time/4)%1
$\RabbitFX\Radius2 = 0.05
$\RabbitFX\Cutout2 = 2
$\RabbitFX\AnimationMode2 = 10

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```


### 8) Moving Clothing Glow

We combine several of the previous intermediate examples to create an animated tattoo on the character's skin and clothing. This is the first example where we apply the concepts we have been learning to a more complicated mesh.

https://github.com/user-attachments/assets/0efb5ec0-9e9c-4fa8-b63a-acfac1afbf0f

There are two new concepts introduced here - first, we are applying the gradient glow from intermediate examples 2 and 7 (circuit and clouds) on to a non-flat mesh, and second we need to understand how to handle cases where the location on the UV map no longer correlates directly to location in space (ie a point high up on the UV map might no longer be high up on the model).

The first concept is fairly straightforward - we have already seen an example of a non-flat mesh in example 3 (rotating emoji sphere), and while a character mesh has more complicated geometry and UVs it's still fundamentally the same. For example, Iris's cape corresponds to this part of the texture:

<p align="center"> 
<img width="300" alt="IntermediateExample8_1" src="https://github.com/user-attachments/assets/2b6445ce-50c2-4497-8ad6-ad14cafaa83c" />
</p>

So we can make it glow using the same concepts we have been using so far:

<p align="center"> 
<img width="300" alt="IntermediateExample8_2" src="https://github.com/user-attachments/assets/de6050d5-b5cd-4833-a209-424829478c0f" />
<img width="300" height="1012" alt="IntermediateExample8_3" src="https://github.com/user-attachments/assets/9ea6c3d2-c7d1-4f60-86f2-ed079df5bc14" />
</p>

The second concept is a little trickier. Say we want the glow to travel from top-to-bottom of the model. Before, we could just directly color the texture with a gradient, but now the location on the UV map no longer corresponds to the "height" on the character model. For example, you can see that the pattern for Iris's boots is actually above the pattern for her stockings:

<p align="center"> 
<img width="300" alt="IntermediateExample8_4" src="https://github.com/user-attachments/assets/1f710de3-f6d3-40cb-8b39-d061a0c2ef01" />
</p>

The simplest way to handle this is the following:

1) Load up the model in blender
2) Press numpad `1` to focus select and get a front view
3) Create a copy of the mesh, and merge it together (select all body parts with the same material and ctrl+j)
4) Create a new empty texture
5) Create a new material and assign that texture to the model
6) Enter texture edit mode
7) Set the brush to be between black (~15) and white (~240) (remember it is usually better to avoid edges if possible, so don't go all the way to 0/255)
8) Use fill mode with the gradient option and drag from top to bottom (or vice-versa, depending if you want black or white at the top)

This will create a texture that represents the gradient from top-to-bottom for the character:

<p align="center"> 
<img width="300" alt="IntermediateExample8_5" src="https://github.com/user-attachments/assets/ac92c65e-3ead-4ad4-bf37-d088db467816" />
</p>

And we can separate out the red channel and overlay it with the parts we want to glow to get for our effect:

<p align="center"> 
<img width="300" alt="IntermediateExample8_6" src="https://github.com/user-attachments/assets/0250c316-fe34-4979-8c28-cbeafe551a7e" />
<img width="300" alt="IntermediateExample8_7" src="https://github.com/user-attachments/assets/f58ca03f-84d6-4dad-a925-d56c001dca27" />
</p>

Resulting in the effect:

https://github.com/user-attachments/assets/4cafde99-3df6-4896-96cb-7e2751032f32

The final code is: 

```
[CommandListIntermediate8]
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap

Resource\RabbitFX\Glowmap = ref ResourceIrisGlowMap1
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample8_2

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/7)%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 0

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 19104, 3828, 0
run = CommandList\RabbitFX\Cleanup


[CommandListIntermediate8Dress]
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap

Resource\RabbitFX\Glowmap = ref ResourceIrisGlowMap1
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample8_2

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/7)%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 0

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 2844, 0, 0
run = CommandList\RabbitFX\Cleanup
```

Note that we had to do a separate draw for the dress, since it is on a different part that the rest of her body (we could have also moved the dress to the same part as her body if it didn't change the outlines).


## Advanced Applications

The final section will use the knowledge we have gained in the previous two sections to implement some complex animations/effects. Make sure you have a solid grasp of how the examples in the first two sections work. These examples will mostly be applied to complex meshes such as characters, though some planes will still be used to illustrate more complicated concepts.


### 1) Rainbow Gradient

A modified version of the final example from the intermediate section, to demonstrate additional things we can do to the effect.

https://github.com/user-attachments/assets/d028c460-9f11-491c-8072-b63c222cb16b

First, let's start with something basic as a warm-up for the advanced section - we want to have the effect from intermediate8, but have it display the default colors instead of purple when the glow is inactive

We can do this via the technique from the intermediate2 circuit example: we draw the diffuse first, then draw the glow on top while cutting out the non-glowing parts:

```
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 19104, 3828, 0

Resource\RabbitFX\Glowmap = ref ResourceIrisGlowMap1
Resource\RabbitFX\FXMap   = ref ResourceIntermediateExample8_2

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/7)%1
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 19104, 3828, 0
run = CommandList\RabbitFX\Cleanup
```
https://github.com/user-attachments/assets/812ccb09-2e84-40a5-b81f-cd32664153cf


This is a powerful technique, and one that is good to remember - we will use it several times in the advanced examples. It's actually possible to do even more with it too; right now, we are simply overlapping the textures, but we can blend them instead to create transparency effects or merge colors as well.


Next, let's make it so the we cycle the colors. We can do this via changing the `$\rabbitfx\h` value. It goes from 0 to 360, so we should multiply the output of the `time` values we have been using by 360:

https://github.com/user-attachments/assets/09a77e2a-b44a-4340-ae9e-0c5f4285a371

This is a neat effect, but it's not quite the one we wanted in the original video - we want multiple colors to appear at once instead of having the entire mesh cycle between a single color.

There are a couple of ways to do this. I'll go over two: the first is to add a blue channel gradient to the fx map and add `AnimationMode1` to the ini:

<p align="center"> 
<img width="300" height="862" alt="AdvancedExample1_1" src="https://github.com/user-attachments/assets/b31b121c-b352-4413-a475-0b88acf4ed9f" />
</p>

This causes the hue to shift as glow reaches maximum for that region, creating a travelling rainbow effect:

https://github.com/user-attachments/assets/c0bc913e-4666-4576-ade3-786bc2b2e4a6

An alternate way is to bake the rainbow color into the glowmap itself and use `$\rabbitfx\h` to cycle the colors instead of `time1`. In this case, we assign colors based on "height" on the model - a point that is high up is purple while one near the bottom is red. A simple way to do this is with python's `colorsys` library, specifically `colorsys.hsv_to_rgb(hue, 1.0, 1.0)` - you treat the value at each point as a hue shift, and generate a texture:

Example python script:

```
from PIL import Image
import colorsys

def alpha_to_rainbow_color(red):
    """Convert red channel (0-255) to an HSV rainbow color (RGB)."""
    hue = red / 255.0  # hue from 0 to 1
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)  # full saturation and value
    return int(r * 255), int(g * 255), int(b * 255)

def convert_white_transparent_to_rainbow(input_path):
    output_path = input_path.replace("Gradient", "Rainbow")
    img = Image.open(input_path).convert('RGBA')
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 0:
                new_r, new_g, new_b = alpha_to_rainbow_color(r)
                pixels[x, y] = (new_r, new_g, new_b, 255)  # make it fully opaque

    img.save(output_path)
    print(f"Saved rainbow image to {output_path}")

convert_white_transparent_to_rainbow('IrisGradient.png')
```

Example output:

<p align="center"> 
<img width="300" alt="AdvancedExample1_2" src="https://github.com/user-attachments/assets/78ff158b-4613-4075-990d-37bf75710594" />
</p>

Result:

https://github.com/user-attachments/assets/d028c460-9f11-491c-8072-b63c222cb16b

The final code is:

```
[CommandListAdvanced1]
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap

Resource\RabbitFX\Glowmap = ref ResourceIrisGlowMap2
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample1_1

$\rabbitfx\h = -360*((time/4)%1)
$\RabbitFX\Brightness = 3.0
$\RabbitFX\Radius1 = 0.1
$\RabbitFX\Cutout1 = 0
$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 19104, 3828, 0
run = CommandList\RabbitFX\Cleanup


[CommandListAdvanced1Dress]
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap

Resource\RabbitFX\Glowmap = ref ResourceIrisGlowMap2
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample1_1

$\rabbitfx\h = -360*((time/4)%1)
$\RabbitFX\Brightness = 3.0
$\RabbitFX\Radius1 = 0.3
$\RabbitFX\Cutout1 = 0
$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 2844, 0, 0
run = CommandList\RabbitFX\Cleanup
```

Note how we managed to create an animated effect without using `Time1` at all by using hue shifting to mimic the movement instead.


### 2) Rotating Halo

A combination of the rotating emoji and DVD logo examples to create a halo above the character

https://github.com/user-attachments/assets/67ec15ff-3dac-4ec0-bf08-f13f6621fd07

For this, we will use a cylindrical object that is connected to Iris's head vertex groups. You can either use a torus or a cylinder - it depends on the shape you want (I used a cylinder for simplicity and because I didn't want it to curve towards the top/bottom):

<p align="center"> 
<img width="400" alt="AdvancedExample2_1" src="https://github.com/user-attachments/assets/61a64bb5-3acf-4130-ba30-c285a2f4a5db" />
</p>

Next, we rotate it by scrolling in the X direction the same way we did for the emoji:

`$\RabbitFX\movex1 = -(time/15)%1`

https://github.com/user-attachments/assets/6f481dd4-ec08-43e4-b79b-39f0ffb6a034

That is part 1 complete. Next, we want it to bob up and down slightly. We can re-use the code from the DVD logo section to make it move up and down slightly:

```
if 0.3*((time/5)%1) - 0.1 > 0.05
	$\RabbitFX\movey1 = 0.3*(1 - (time/5)%1) - 0.1
else
	$\RabbitFX\movey1 = 0.3*((time/5)%1) - 0.1
endif
```

https://github.com/user-attachments/assets/ec2459c0-7f86-4819-a394-fa2bd7338e6d

ASIDE:

I was going to use this section to explain the difference between linear (ramp) motion and parabolic motion, but the vertical movement of the halo is subtle enough that it would be hard to tell the difference and I don't want to redo the UV maps on it. Basically, it's just that the halo/object spends the same amount of time in each position, when sometimes it might look nicer if it spent longer at the edges; to do this, you can use a `sin` or `cos` function on time instead to get a smoother motion:

<p align="center"> 
<img width="350" alt="AdvancedExample2_2" src="https://github.com/user-attachments/assets/aef1ab4c-8e07-4adc-a422-519bd6605024" />
</p>

You can also emulate this effect by having it "stall" at the top and bottom for a bit, which might be simpler to code since 3dmigoto ini don't come with `sin` and `cos` functions so you will have to approximate them by using something like a taylor series.

The final step is to add a few more glow effects - let's have the center lines slowly hue shift. We separate them out on to another glowmap, and draw the halo in two parts (another example of layering effects):

<p align="center"> 
<img width="350" alt="AdvancedExample2_3" src="https://github.com/user-attachments/assets/3eb3e994-f081-4057-b80e-471eb25bbeee" />
</p>

Note that a few of the colors in the center are showing up as white - this is because of the purple aura from the surroundings overlapping with the color it emits. This can be reduced either by decreasing glow, or adjusting the colors used so they don't overlap.

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceHalo
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample2_2

$\RabbitFX\Brightness = 3.5
$\RabbitFX\Cutout1 = -1

$\RabbitFX\movex1 = -(time/15)%1
if 0.3*((time/5)%1) - 0.1 > 0.05
	$\RabbitFX\movey1 = 0.3*(1 - (time/5)%1) - 0.1
else
	$\RabbitFX\movey1 = 0.3*((time/5)%1) - 0.1
endif

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 372, 0, 0

Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceHalo
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample2_3

$\RabbitFX\Brightness = 2.0
$\rabbitfx\h = 360*((time/4)%1)
$\RabbitFX\Cutout1 = -1

$\RabbitFX\movex1 = -(time/15)%1
if 0.3*((time/5)%1) - 0.1 > 0.05
	$\RabbitFX\movey1 = 0.3*(1 - (time/5)%1) - 0.1
else
	$\RabbitFX\movey1 = 0.3*((time/5)%1) - 0.1
endif

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 372, 0, 0
run = CommandList\RabbitFX\Cleanup
```




### 3) Rotating Magic Circle

A more advanced rotation example showing how to rotate on a flat plane.

https://github.com/user-attachments/assets/3b085b41-f993-4f77-af56-6235ef665636

"We have already seen two examples of rotating objects before Silent, why is this one any different?". Well, the previous examples had something in common - the mesh they were displayed on was already curved (sphere, cylinder) and we scrolled along that curved surface to create the rotation. But what if we want to rotate something on a flat surface? As it turns out, this is actually more complicated than expected - we can move things easily in X and Y directions, but how do we move things along a circle?

The answer is math. Until recently, we have been representing the locations and movements on the texture using cartesian coordinates (e.g. move this amount in the X direction, or move this amount in Y), but now we want to represent the movement of an object in polar coordinates instead (e.g. as a radius away from the center, and a certain angle relative to the X axis):

<p align="center"> 
<img width="500" alt="AdvancedExample3_1" src="https://github.com/user-attachments/assets/dddfe936-93e1-4758-9eb8-4154fc3f16dd" />
</p>

We can specify `$\RabbitFX\mover1` and `$\RabbitFX\moveangle1` to control radius and angle respectively. Let's say we want to create a magic circle - we can use the r value to increase/decrease the size of the circle and the angle value to rotate it. Rotations are defined in radians (so between 0 and 2pi (6.28) - if you have degrees, you can multiply by pi/180 to convert), and the radius default is 1 (larger increases size, smaller decreases it).

<p align="center"> 
<img width="400" alt="AdvancedExample3_3" src="https://github.com/user-attachments/assets/ea812d79-458b-49ad-bbe6-bd3f63de8ccc" />
</p>

```
if (time/10)%0.2 + 0.9 > 1.0
	$\RabbitFX\mover1 = 1.1-(time/10)%0.2
else
	$\RabbitFX\mover1 = (time/10)%0.2 + 0.9
endif
$\RabbitFX\moveangle1 = (time/2)%6.28
```

https://github.com/user-attachments/assets/0ae19f94-a7ed-4dcc-8832-ac655c6d7b8f

Also, I just want to say that if you are still here and reading this tutorial I really appreciate it. I suspect that less than a dozen people will ever read this line (just like several of my other in-depth tutorials on effects lol), so I'm happy that at least someone cares enough to get this far.

For rotation, note that wrapping will be turned off - if you shift the object in the x or y direction off-screen (or if it rotates off-screen), it won't appear on the other side. This is for a few reasons, the main one being that implementing proper wrapping for rotation is just really painful and I don't feel like doing it.

The last part is just placing the plane/circle at the character's feet - there are still some issues like the plane not remaining aligned with the ground (it follows whatever you weighted it to), but fixing those issues are beyond the scope of this tutorial.

The final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceIrisBodyDiffuse
Resource\RabbitFX\LightMap = ref ResourceIrisBodyLightMap
Resource\RabbitFX\SpecularMap = ref ResourceIrisBodySpecularMap
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 19104, 3828, 0

Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceMagicCircle
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample3

$\RabbitFX\Brightness = 10.0
$\RabbitFX\Time1 = (time/8)%1
$\RabbitFX\Radius1 = 0.50

if (time/10)%0.2 + 0.9 > 1.0
	$\RabbitFX\mover1 = 1.1-(time/10)%0.2
else
	$\RabbitFX\mover1 = (time/10)%0.2 + 0.9
endif
$\RabbitFX\moveangle1 = (time/2)%6.28

$\RabbitFX\AnimationMode1 = 1

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22938, 0
run =  CommandList\RabbitFX\Cleanup
```

### 4) Analog Clock

An alternate application of the rotating circle example above, combined with the clock example from intermediate examples. We are going to create an analog clock that "ticks" each second and slowly counts out minutes:

https://github.com/user-attachments/assets/27fd7a78-676c-492a-8acd-0fd11e803318

First, let's do the seconds hand. It has a cycle of 60 seconds, but we need to slightly adjust the formula we were using. A full rotation in radians is 2pi (6.28) - that means, if we use `time` directly it will take 6.28 seconds to complete a rotation (or 6.28 s / 1 cycle). We want a rotation to take 60 seconds instead so we multiply by `6.28/60 = 0.104` (we want 1/60th of a rotation to be 6.28 seconds). So the equation is 

`$\RabbitFX\moveangle1 = (time* 0.104)%6.28`

This will work, but it creates a smooth motion of the clock - we want the clock to "tick" each second instead. We can do this via chopping `time` into 60 discrete intervals instead of having it continuous. We can do that using `//` which does integer division: `(time*X)//X`, where X is the step size. For example, if X is 0.5 the this will go 0.5, 1.0, 1.5, 2.0 instead of smoothly counting from 0.5 to 2.0. We can then use this value in place of `time` to create the ticking motion:

```
local $interval = (time*0.104)//0.104
$\RabbitFX\moveangle1 = -($interval*0.104)%6.28
```

This will rotate the hand by `1/60th` of the clock every second.

For the minute hand, we use smooth motion but the period is different - it does a full rotation in 3600 seconds so the value is `6.28/3600 = *0.00174`:

`$\RabbitFX\moveangle2 = -(time*0.00174)%6.28`

The fx texture is (each had is on a seperate glowmap, and has no special effects applied):

<p align="center"> 
<img width="350" alt="AdvancedExample4_1" src="https://github.com/user-attachments/assets/4fb64719-96d5-445c-b971-95f31e1dc2a0" />
</p>

And the final code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceClock
Resource\RabbitFX\FXMap = ref ResourceAdvancedExample4_1

$\RabbitFX\Brightness = 1.0

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0

Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourceSecondHand
Resource\RabbitFX\Glowmap2 = ref ResourceMinuteHand
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample4_2

$\RabbitFX\Brightness = 1.0
$\RabbitFX\Cutout1 = -1

local $interval = (time*0.104)//0.104
$\RabbitFX\moveangle1 = -($interval*0.104)%6.28
$\RabbitFX\moveangle2 = -(time*0.00174)%6.28

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run =  CommandList\RabbitFX\Cleanup
```


### 5) Animation Atlas

In this example, we illustrate how to use this library to create longer sequences of animation.

https://github.com/user-attachments/assets/16456057-504c-4e21-80d3-b2843f114806

(Yes, it has the entire animation. I just cut it at 10 seconds to keep the file size small enough to upload here lol)

With this library, we have another way to implement simple frame-by-frame videos compared to the older method of loading each frame individually - we can line up the frames in a large atlas, and scroll across it:

<p align="center"> 
<img width="500" alt="AdvancedExample5_1" src="https://github.com/user-attachments/assets/bd52e066-def1-48fe-bc09-e7bced0615b1" />
</p>

This has the benefit of having a much smaller number of files and code to deal with - this animation has over 3000 frames in total, meaning that to animate the frames we would need around 12000 lines of code (around 6k in definitions for each of the frames, and around 6k for the if/else statements that loaded them all). But by putting them into a series of 10 x 10 atlases, we can reduce the number of textures required to 30, the number of lines of code to ~100, and the total size to around 10 mb.

There are different ways to create the atlas - I believe photoshop has a plugin for it, or you could write a script to split up an mp4 or gif. I did the later and included the script in the tutorial zip files.

Once the atlas has been created, we need to find a way to display a specific frame. First, we need to shrink what is displayed to only a single square instead of the entire 10x10 grid. We can do that via:

`$\RabbitFX\mover1 = 10`

(Why is r 10 and not 0.1? Well, our goal is to display just a single square so we are actually massively increasing the size of the texture so only a single square is visible).

<p align="center"> 
<img width="350" alt="AdvancedExample5_2" src="https://github.com/user-attachments/assets/88c559da-dc9a-4ca9-9097-ec6bc05bde24" />
</p>

This sort of works, but you can see that we are actually between frames - our center point isn't aligned properly with the start/end points of the images. Since our current location is 0.5, 0.5 and a single image has a width and height of of 0.1 (1/10th of the image), we can subtract `-0.45` from our X and Y positions to reach the first frame (puts us at `(0.05, 0.05)` and we can see between `(0,0)` and `(0.1,0.1)`):

<p align="center"> 
<img width="350" alt="AdvancedExample5_3" src="https://github.com/user-attachments/assets/8a2f58ae-c07f-4396-9c7c-b66e86da98c8" />
</p>

Now, to move frames we can "jump" by 0.1 in each direction. We already saw in the previous clock example how to make discrete movements - we want to scroll horizontally at whatever framerate we set, and vertically at 1/10th that speed:

```
local $framerate = 15
local $intervalX = ((time*$framerate)//1)%$atlaswidth
local $intervalY = ((time*$framerate/10)//1)%$atlasheight
$\RabbitFX\movex1 = -0.45 + 0.1*$intervalX
$\RabbitFX\movey1 = -0.45 + 0.1*$intervalY
```

Here, $framerate defines how many frames we want to see per second. `15` means 15 fps. Note that this is *independent* of the fps the game is running at - this animation will always run at 15 fps regardless if the game itself is running at 30, 60 or 120 fps. The `$atlaswidth` and `$atlasheight` are both 10. This will result in:

https://github.com/user-attachments/assets/8d722ac8-47b1-41d3-afaa-63a5f31337a9

So we now have a single atlas correct. The next step is to implement multiple ones for the full animation (since putting 3k frames on a single texture is very inefficient). The concept is very similar to what we have done so far - we want to move to the next atlas after `$atlaswidth*$atlasheight` frames pass at whatever framerate we are using, only allowing integer values and looping when we reach the max atlas count: 

`local $atlasnumber = ((time*$framerate/($atlaswidth*$atlasheight))//1)%$atlascount `

This will start at 0, then after (width*height)/fps time passes (in this case 100 frames /15 s -> 6.5 seconds) it will increase to 1. Then after another 6.5 seconds, it will increase to 2, until it reaches `$atlascount` (which is 30 in this case) and the animation loops back to 0.

The final step is to load the correct atlas depending on the value of `$atlasnumber`. Unfortunately, since we lack loops or string manipulation, the only way to do it is to just list it out in a big if/else statement:

```
if $atlasnumber == 0
	Resource\RabbitFX\Glowmap = ref ResourceAtlas0
elif $atlasnumber == 1
	Resource\RabbitFX\Glowmap = ref ResourceAtlas1
elif $atlasnumber == 2
	Resource\RabbitFX\Glowmap = ref ResourceAtlas2
...
endif
```

The final code is (I trimmed the atlas set, it goes to 30):

```
local $framerate = 15
local $atlaswidth = 10
local $atlasheight = 10
local $atlascount = 30

Resource\RabbitFX\Diffuse = ref ResourceBlack

local $atlasnumber = ((time*$framerate/($atlaswidth*$atlasheight))//1)%$atlascount 

if $atlasnumber == 0
	Resource\RabbitFX\Glowmap = ref ResourceAtlas0
elif $atlasnumber == 1
	Resource\RabbitFX\Glowmap = ref ResourceAtlas1
elif $atlasnumber == 2
	Resource\RabbitFX\Glowmap = ref ResourceAtlas2
elif $atlasnumber == 3
	Resource\RabbitFX\Glowmap = ref ResourceAtlas3
elif $atlasnumber == 4
	Resource\RabbitFX\Glowmap = ref ResourceAtlas4
; ... trimmed, continue this until 30
endif

Resource\RabbitFX\FXMap = ref ResourceBlack
$\RabbitFX\Brightness = 1.0

local $intervalX = ((time*$framerate)//1)%$atlaswidth
local $intervalY = ((time*$framerate/10)//1)%$atlasheight
$\RabbitFX\movex1 = -0.45 + 0.1*$intervalX
$\RabbitFX\movey1 = -0.45 + 0.1*$intervalY

$\RabbitFX\mover1 = 10.2

$\RabbitFX\removeshadow = 1
$\RabbitFX\removebackgroundshadow = 1
run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
```


### 6) Paimon Cape

Now we start to get to the really cool looking effects. We are going to be emulating paimon's cape effect from Genshin:

https://github.com/user-attachments/assets/80dfa4f2-a23b-4c93-8098-afd9f3945343

This effect has multiple layers, and is the first time we are going to see more advanced blending techniques. We will not be able to fully replicate the effect since we don't have access to the camera's location to do parallax, but we can approximate the effect.

Now, to briefly explain how paimon's cape effect works. It has 5 layers: the background color (a gradient from dark to light blue), a cloud effect, a series of constellations, stars (two sets that move independently) and a color palette that is applied over the clouds and stars.

<p align="center"> 
<img width="1000" alt="AdvancedExample6_1" src="https://github.com/user-attachments/assets/0e884bc4-704c-4546-a3f5-f24f719f0967" />
</p>

We will implement them one-by-one. First is the easiest, the background:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeBackground
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_1

$\RabbitFX\Brightness = 1.0

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
drawindexed = 6, 22932, 0
run = CommandList\RabbitFX\Cleanup
```

<p align="center"> 
<img width="350" alt="AdvancedExample6_2" src="https://github.com/user-attachments/assets/9b7ff683-b326-4f95-8b6b-a927dbbb5cf1" />
</p>

Not much to say here. If you've reached this point, this shouldn't be complicated. The FX map is just a red square, since we want it to be always visible.

Next, we add the clouds. We add a slight horizontal movement to shift them back and forth, and have a radius of 1.3 to avoid issues with edges:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeClouds
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_1

$\RabbitFX\Brightness = 1.0

if 0.2*((time/20)%1) - 0.1 > 0
	$\RabbitFX\movex1 = 0.2*(1 - (time/20)%1) - 0.1
else
	$\RabbitFX\movex1 = 0.2*((time/20)%1) - 0.1
endif

$\RabbitFX\mover1 = 1.3

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
run = CustomShaderBlendClouds
run = CommandList\RabbitFX\Cleanup

[CustomShaderBlendClouds]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = .1
blend_factor[1] = .1
blend_factor[2] = .1
blend_factor[3] = 1
drawindexed = 6, 22932, 0
```

https://github.com/user-attachments/assets/4660ee57-de10-43b2-b6fe-0e3c5952192a

Most of this should be familiar, with one exception - instead of directly overlapping the clouds, I'm using a custom shader to `blend` them together with the background sky. The `0.1` represents the amount of blending performed - at any given point, `0.9` of the color comes from the sky and `0.1` from the clouds (we use a very light blend so the clouds are only slightly visible, since they aren't the focus of the effect).

Next, the constellations. We split this into two since we want to have different glow/blend for different parts:

<p align="center"> 
<img width="350" alt="AdvancedExample6_3" src="https://github.com/user-attachments/assets/a0ccbd74-0bd2-4716-8bab-42afc34c9086" />
<img width="350" alt="AdvancedExample6_4" src="https://github.com/user-attachments/assets/9d40ddb8-9ff0-4ac2-ae9d-131eb8e686e0" />
</p>

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeConstellations
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_2

$\RabbitFX\Brightness = 3.0

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
run = CustomShaderBlendConstellation
run = CommandList\RabbitFX\Cleanup

Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeConstellations
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_3

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
run = CustomShaderBlendConstellation2
run = CommandList\RabbitFX\Cleanup

[CustomShaderBlendConstellation]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = .75
blend_factor[1] = .75
blend_factor[2] = .75
blend_factor[3] = 1
drawindexed = 6, 22932, 0

[CustomShaderBlendConstellation2]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = .3
blend_factor[1] = .3
blend_factor[2] = .3
blend_factor[3] = 1
drawindexed = 6, 22932, 0
```

Note that I blend the glowing parts more strongly than the lines that connect them, to closer mimic how paimon's cape works.

<p align="center"> 
<img width="400" alt="AdvancedExample6_5" src="https://github.com/user-attachments/assets/155e48f5-92d9-4750-933c-a92f836d68b9" />
</p>


Next, let's add the stars. We split it into two again like before, and give each different movement:

<p align="center"> 
<img width="512" height="512" alt="AdvancedExample6_6" src="https://github.com/user-attachments/assets/b5c5619a-1616-4790-a896-469cb0626d6e" />
<img width="512" height="512" alt="AdvancedExample6_7" src="https://github.com/user-attachments/assets/3c4d0acb-6e43-40b5-977e-bdf92d1eaae3" />
</p>

This time, we want the motion to be smooth and not do a hard rebound like we saw on the DVD logo example. We can do this by using a sin/cos wave instead of linear movement. Unfortunately, 3dmigoto doesn't have a function for `sin` or `cos`, so we need to approximate it (this approximation comes from SinsOfSeven's 3dmigoto math library https://github.com/SinsOfSeven/3dmigoto_math_lib):

```
[Constants]
global $in
global $out

[CommandListCos]
local $pi = 3.14159265
if $in == inf || $in == -inf || $in == NaN || $in == null
    $out = NaN
else
    local $x = ($in+$pi/2)%$pi-$pi/2
    local $xx = $x*$x
    local $f0 = -($xx/2)
    local $f1 = (($xx*$xx)/24)
    local $f2 = -(($xx*$xx*$xx)/720)
    local $f3 = (($xx*$xx*$xx*$xx)/40320)
    local $f4 = -(($xx*$xx*$xx*$xx*$xx)/3628800)
    $out = -((($in+$pi/2)/$pi)%2//1*2-1) * (1+$f0+$f1+$f2+$f3+$f4)
endif
$in = 0
```

We can pass in a value `x` in radians, and get the corresponding value of `sin(x)`. The math on how to create outputs is very similar to the rotation examples we've seen before - if we want to create a back-and-forth movement with a cycle of 10 seconds that goes between -0.1 and 0.1, the code is:

```
$\RabbitFX\Brightness = 2.0
$in = time*(6.28/10)
run = CommandListCos
$\RabbitFX\movex1 = 0.1*$out
```

`6.28/10` means performing a full rotation (`2pi`) every 10 seconds, and we scale the output (which is normally in the range `[-1,1]`) to `[-0.1,0.1]` by multiplying by `0.1`.

So the code is:

```
Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeStars
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_4

$\RabbitFX\Brightness = 2.0
$in = time*(6.28/10)
run = CommandListCos
$\RabbitFX\movex1 = 0.1*$out

$in = time*(6.28/6)
run = CommandListCos
$\RabbitFX\movey1 = 0.07*$out

$in = time*(6.28/30)
run = CommandListCos
$\RabbitFX\mover1 = 1 + 0.1*$out

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
run = CustomShaderBlendStars
run = CommandList\RabbitFX\Cleanup


Resource\RabbitFX\Diffuse = ref ResourceBlack
Resource\RabbitFX\Glowmap = ref ResourcePaimonCapeStars
Resource\RabbitFX\FXMap   = ref ResourceAdvancedExample6_5

$in = time*(6.28/10)
run = CommandListCos
$\RabbitFX\movex1 = 0.1*$out

$in = time*(6.28/5)
run = CommandListCos
$\RabbitFX\movey1 = 0.07*$out

$in = time*(6.28/35)
run = CommandListCos
$\RabbitFX\mover1 = 1 + 0.1*$out

run = CommandList\RabbitFX\SetTextures
run = CommandList\RabbitFX\Run
run = CustomShaderBlendStars
run = CommandList\RabbitFX\Cleanup

[CustomShaderBlendStars]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = .75
blend_factor[1] = .75
blend_factor[2] = .75
blend_factor[3] = 1
drawindexed = 6, 22932, 0
```

https://github.com/user-attachments/assets/dff85be0-a9cd-4a88-ae83-46641d9a3b16

We are almost at the full effect. The last part is applying the color palette. The simplest way in this case is to just apply it directly to the textures:

<p align="center"> 
<img width="512" height="512" alt="AdvancedExample6_9" src="https://github.com/user-attachments/assets/8b54a240-7ab7-4708-9c10-512de4ec1468" />
<img width="512" height="512" alt="AdvancedExample6_8" src="https://github.com/user-attachments/assets/19bf78b4-7b11-4a5d-9c6b-5f6c48df563f" />
</p>

And the effect is complete!

https://github.com/user-attachments/assets/c82e2663-d56f-444a-8371-c90b068770f2

The code is quite long in this case (and I've already shown the entire thing as we've gone along), so I'll refrain from posting it this time - you can look in the example ini to see it.

The final step would be applying this effect to clothing, but getting this functional already took me like 8 hours and I'm tired lol. Putting it on clothing is left as an excercise for the reader.


### 7) Matrix Digital Rain

A combination of multiple effects we have seen so far to create a matrix-style movie effect.

https://github.com/user-attachments/assets/209cc8dd-5a5e-4c56-94ff-330721a14fc1

There are many ways we can implement this sort of effect - the simplest is to have a string of letters/characters and just scroll the UV over them. But I want to show something a bit fancier - I want to demonstrate how we can make the symbols constantly flip between different values as they drop.

This isn't as easy as it sounds (if it sounds easy to you lol). While we can use thresholds to make glow flip between on/off states, a single portion of the glowmap can have at most 3 regions (off/on/off). Even with glowmap 2, that increases to at most ~5 so we are going to have to layer multiple calls on top of each other.

The simplest way to do this will be to use a font atlas, and use randomization to select which portion of it to load at any given time. First, we need the font:

<p align="center"> 
<img width="400" alt="AdvancedExample7_1" src="https://github.com/user-attachments/assets/31caa577-3305-4fb2-86be-7754c44ecf33" />
</p>

Now, we need a way to "select" a specific character for any given draw. We could do this by just giving each letter its own image, but that would require us to create and load around 150 images. Instead, we can leverage some of the library's functions to create a function that can select a single character from the grid:

<p align="center"> 
<img width="400" alt="AdvancedExample7_2" src="https://github.com/user-attachments/assets/90d010a4-3c03-456c-9a4e-41fc319cc878" />
</p>

This has a gradient from 0 to 255 on the red channel going left to right, and a gradient of 0 to 255 on the green channel going up to down. So by using specific values for `time1`, `radius1`, `time2` and `radius`, it lets us select a specific point in a 2D grid. The `time` values represent the X and Y coordinates, and the `radius` represent the thickness of a single character.

```
local $atlaswidth = 14
local $atlasheight = 14
$\RabbitFX\time1 = $matrix_row/($atlaswidth)
$\RabbitFX\radius1 = 1/(2*$atlaswidth)

$\RabbitFX\time2 = $matrix_col/($atlasheight)
$\RabbitFX\radius2 = 1/(2*$atlasheight)

$\RabbitFX\cutout1 = 2
$\RabbitFX\cutout2 = 2
```

This will display a single image corresponding to `$matrix_row` and `$matrix_col`. Setting both `cutout` to `2` uses glowmap1 as a mask for glowmap2 (this avoids drawing the whole glowmap1 column).

Next, we can draw that symbol at any position we want via:

```
$\RabbitFX\movex1 = ($matrix_row-1)/($atlaswidth-1) - ($col - 1)/($atlaswidth-1)
$\RabbitFX\movex2 = ($matrix_row-1)/($atlaswidth-1) - ($col - 1)/($atlaswidth-1)

$\RabbitFX\movey1 = ($matrix_col-1)/($atlasheight-1) - ($row - 1)/($atlasheight-1)
$\RabbitFX\movey2 = ($matrix_col-1)/($atlasheight-1) - ($row - 1)/($atlasheight-1)
```

This first moves the symbol to the point `(1,1)` by subtracting off its `matrix_col` and `matrix_col`, the moves it to a specific `row` and `col` that we want to draw it at.

We now have the ability to select and draw arbitrary symbols, but we are a long way from the full effect. Next, let's focus on a single column and creating the "dropping" effect.

The first thing we need is the ability to store if each row on the column is active, and what intensity/how visible the symbol is (from 0 being not active to 4 being the most active). While we could simply create 13 variables, one for each row, that will require us to have over 150 variables in total for the entire grid and is a bit painful.

We can instead use some basic bit-packing to store multiple values in a single number:

```
[CommandListGetIntensity]
$intensity = ($target_col // (10)**($row-1)) % 10

[CommandListSetIntensity]
$target_col = $target_col - $intensity * (10**($row-1)) + $new_intensity * (10**($row-1))
```

This lets us use a number such as `00432` to store the the state of each row - 2 represents the value of the first row, 3 of the second, 4 of the third, and both the fourth and fifth are 0.

Unfortunately, this still isn't enough - 3dmigoto uses 32 bit floats to store numbers, which means that it can only support up to around 10 digits or so (and in practice, we will start running into problems around ~8 digits due to float precision). So we need to store it across two values:

```
[CommandListGetIntensity]
if $row < 8
	$intensity = ($target_col // (10)**($row-1)) % 10
elif $row < 14
	$intensity = ($target_col_2 // (10)**($row-8)) % 10
endif


[CommandListSetIntensity]
if $row < 8
	$target_col = $target_col - $intensity * (10**($row-1)) + $new_intensity * (10**($row-1))
elif $row < 14
	$target_col_2 = $target_col_2 - $intensity * (10**($row-8)) + $new_intensity * (10**($row-8))
endif
```

This is functionally the same thing, except we now use two sets of numbers to store all 13 rows.

We now have the ability to store and retrieve the state of any row - the next step is to update the state. There are two different types of state we are interested in; the first is what symbols are being displayed and the second is the location of the symbols.

For the symbols, we use the randomization function from the Sins' math library mentioned before:

```
[CommandListRandom]
local $m = 65537
local $a = 75
local $c = 74
local $first_call
if $seed < 0
	$seed = time
endif
$seed = ($seed * $a + $c) % $m
$out = $seed
```

Calling this before any draw will let us randomize what character is displayed. Furthermore, as long as we use the same seed each frame we will get the same set of characters - thus, starting from a different seed will let us generate a new set to display.

Randomly selecting a char:

```
run = CommandListRandom
$matrix_row = ($out)%13 + 1
run = CommandListRandom
$matrix_col = ($out)%10 + 1
```

Updating the seed every `$symbol_update_interval`:

```
if time - $last_symbol_update > $symbol_update_interval
	$last_symbol_update = time
	$stored_seed = $out
endif
$seed = $stored_seed

```

This handles randomly swapping characters, but not the movement downwards. For that, we can do the following:

```
if time - $last_location_update > $location_update_interval
	$last_location_update = time
	run = CommandListUpdateGrid
endif

[CommandListUpdateGrid]
$target_col = $col1_1
$target_col_2 = $col1_2
run = CommandListUpdateColumn
$col1_1 = $target_col
$col1_2 = $target_col_2

$target_col = $col2_1
$target_col_2 = $col2_2
run = CommandListUpdateColumn
$col2_1 = $target_col
$col2_2 = $target_col_2

; continue for all 13 cols

[CommandListUpdateColumn]
$row = 13
run = CommandListUpdateSymbol
$row = 12
run = CommandListUpdateSymbol
; continue for all 13 rows

[CommandListUpdateSymbol]
run = CommandListGetIntensity
if $intensity > 0
	$new_intensity = $intensity - 1
	run = CommandListSetIntensity
endif
if $intensity == 4
	$intensity = 0
	$new_intensity = 4
	$row = $row + 1
	run = CommandListSetIntensity
	$row = $row - 1
endif
```

While this is a big chunk, all it is saying is "every `location_update_interval` go through each row and column. If the intensity at any point is greater than 0, subtract 1. If it is 4, make the one below 4 as well". The only thing to note is that we travel from bottom-to-top so we don't have to handle conflicts as the strings of symbols travel downwards.

This is most of the logic handled - all we have left is the fade out effect and the start condition. For the fade, we can use the blending technique we covered last time and use the intensity to blend different amounts:

```
run = CommandListGetIntensity
if $intensity == 1
	run = CustomShaderBlendSymbol1
elif $intensity == 2
	run = CustomShaderBlendSymbol2
elif $intensity == 3
	run = CustomShaderBlendSymbol3
elif $intensity == 4
	drawindexed = 6, 22932, 0
endif

[CustomShaderBlendSymbol1]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = 0.1
blend_factor[1] = 0.1
blend_factor[2] = 0.1
blend_factor[3] = 1
drawindexed = 6, 22932, 0

[CustomShaderBlendSymbol2]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = 0.3
blend_factor[1] = 0.3
blend_factor[2] = 0.3
blend_factor[3] = 1
drawindexed = 6, 22932, 0

[CustomShaderBlendSymbol3]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = 0.6
blend_factor[1] = 0.6
blend_factor[2] = 0.6
blend_factor[3] = 1
drawindexed = 6, 22932, 0
```

The final part is the start condition. For each column, every tme we update locations we generate a random value and if it is within a certain range we set `4` at the top of that column:

```
run = CommandListRandomLoc
if $OutSymbolLoc%100 < 7
	$row = 1
	$intensity = 0
	$new_intensity = 4
	run = CommandListSetIntensity
endif
```

In this case I chose 7 for a 7% chance for any column to have the rain begin (chosen by trying different values - 5% was a bit too infrequent, and 10% triggered too often). Note that we have to use a different seed/randomize here so it doesn't interfere with the one for randomizing symbols.

The final code is in the example ini - it's quite long, so will refrain from posting it here to avoid bloating the tutorial.


### 8) Tetris

For the final example, let's implement tetris! You heard me.

WIP




## Addendum

### Colorspaces:

The FX texture expects a linear colorspace, while the glow textures expect SRGB colorspace. If you are using a tool like paint.net, make sure to select the correct export type.

While paint.net is a good tool, it has some issues with DDS compression; if you are noticing odd artifacting on your textures, there are a couple of alternatives:

1) Save as png and convert via magick: `magick.exe .\Dots.png -colorspace sRGB .\DotsTest.png` . Most tools save png as SRGB by default, and that command converts it to linear (*even though* it says sRGB colorspace in the command, it's linear. I don't know why. Some tools like photoshop also support choosing colorspace) . Smallest size and no compression issues, but may have compatibility issues on some systems/OS
2) Use nvidia texture tools (exports as linear by default, can change in export transfer function. Don't export mip maps, rest is default)
3) Photoshop with either intel texture works or nvidia texture tools
4) texconv tools (may result in crunchiness, texconv sometimes won't use the correct color space)

Do NOT use blender dds export or photoshop default dds export, they don't work properly as of the time of writing this guide

Also note that behaviour may be odd around the edges - I recommend leaving a small gap (~`0.01`) around the edges and avoiding numbers that are very close to `0` or `1.0`


### Setting textures using RabbitFX

For stella sora and star rail, RabbitFX supports setting diffuse, lightmap via calls:
```
Resource\RabbitFX\Diffuse = ref ResourceDiffuse
Resource\RabbitFX\LightMap = ref ResourceLightmap
```

Stella sora specifically also has a specular map
`Resource\RabbitFX\SpecularMap = ref ResourceSpecularmap`

Along with the ability to set custom outlines via
`Resource\RabbitFX\OutlineMap = ref ResourceOutlinemap`

For more details, please refer to the rabbitfx page of your game

### Texture Visibility

Since it can be confusing to remember, here is a quick overview of what will happen depending on the values of Glowmap1, Glowmap2 and FX map (Remember: setting Glowmap2 without Glowmap1 first is undefined behaviour):

#### Glowmap1 set, Glowmap2 not set:

```
FXmap alpha == 0:
	Mesh will always be invisible, regardless of other values

Glowmap alpha == 0, FXmap alpha > 0, FXmap red channel == 0:
	cutout = 0 : uses original diffuse
	cutout = +1 or -1 : mesh will not be visible

Glowmap alpha == 0, FXmap alpha > 0, FXmap red channel > 0:
	cutout = 0 or -1 : uses original diffuse (no animation, entire segment will always be visible)
	cutout = 1 : uses original diffuse (animation - when active, original diffuse will be visible and when inactive will be invisible. Will not glow)

Glowmap alpha > 0, FXmap alpha > 0, FXmap red channel == 0:
	cutout = 0 : uses glowmap color
	cutout = 1 or -1 : mesh will not be visible

Glowmap alpha > 0, FXmap alpha > 0, FXmap red channel > 0:
	cutout = 0 or -1: uses glowmap color (will glow when active using glowmap color, and use non-glowing glowmap color when inactive)
	cutout = 1: uses glowmap color (will glow when active using glowmap color, and be invisible when inactive)

Glowmap alpha > 0, FXmap alpha > 0, FXmap red channel == 1:
	Uses glowmap color and will always glow (no animation)

Special:
	cutout = 2 : Mesh always invisible, regardless of fxmap values (glowmap1 intended to be used as a mask for glowmap2)

```

The inverse table is:
```
Mesh is invisible when:
	FXmap alpha == 0
	Glowmap alpha >= 0, FXmap alpha > 0, FXmap red channel == 0, cutout = +1 or -1
	Glowmap alpha >= 0, FXmap alpha > 0, FXmap red channel > 0,  cutout = 1, section is inactive

Diffuse is visible when:
	Glowmap alpha == 0, FXmap alpha > 0, FXmap red channel == 0, cutout = 0
	Glowmap alpha == 0, FXmap alpha > 0, FXmap red channel > 0,  cutout = 0 or -1
	Glowmap alpha == 0, FXmap alpha > 0, FXmap red channel > 0,  cutout = 1, section is active

Glowmap is visible when:
	Glowmap alpha > 0,  FXmap alpha > 0, FXmap red channel == 0, cutout = 0
	Glowmap alpha > 0,  FXmap alpha > 0, FXmap red channel > 0,  cutout = 0 or -1
	Glowmap alpha > 0,  FXmap alpha > 0, FXmap red channel > 0,  cutout = 1, section is active

Texture glows when:
	Glowmap alpha > 0, FXmap alpha > 0, FXmap red channel > 0,  section is active
	Glowmap alpha > 0, FXmap alpha > 0, FXmap red channel == 1, at all times

```

TLDR: If FX map alpha is 0, the mesh will always be invisible regardless of other values. If glowmap1 alpha is 0, you will either see the original diffuse or it will be invisible depending on `cutout1`. If both fxmap and glowmap have alpha > 0, then it will either display glowmap1 or be invisible depending on the value of `cutout` and the FX map red channel.

Note that the one situation that is difficult to handle is when you want the original diffuse to be visible on a part of the texture which also supports glow, where the original diffuse color is different than the glow color (such as having a blue part glow red, or having a gray part light up). See Intermediate example #2 for a situation where this occurs and some solutions (usually the simplest solution is to just draw the mesh twice and overlap it while using cutouts- once for the default color, and once for the glow)


#### Glowmap1 set, Glowmap2 set:

When active, Glowmap2 takes priority over Glowmap1. Otherwise, the behaviour of Glowmap2 is very similar to Glowmap1 with a few key differences. The most important one is that instead of directly cutting out the mesh or displaying the diffuse, it will defer the decision to glowmap1 *most of the time* (they are layered Glowmap2 > Glowmap1 > Diffuse; even if Glowmap2 isn't active, we don't know what the final output will be until we check Glowmap1). 

The second point is that values of the FX map with alpha > 0 and green channel == 0 (such as black) behave slightly differently. For Glowmap1, it will display the Glowmap1 value as long as cutout is 0 but for Glowmap2, it will still defer to Glowmap1 instead of using 2. This is for technical reasons, to prevent issues where Glowmap2 is not set; as a result, if you want constant non-glowing parts, it's better to put them on Diffuse or Glowmap1 instead of Glowmap2 (you can still have parts that don't have glow on Glowmap2, by adjusting the glow output so they have a glow of 1.0).

The third point is that `cutout2` can be set to `2` (in addition to the regular values of `0`, `1` and `-1`). This is a special case that causes only parts of glowmap2 that overlap glowmap1 to be visible (see intermediate example 7 for a case where we use it to make the glowing lightning effects only appear over the clouds)

```
FXmap alpha == 0:
	Mesh will always be invisible, regardless of other values

Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel == 0:
	Defer to Glowmap1

(This one is tricky and somewhat non-standard. Honestly, I'd avoid this set if possible, unless you really need to cut directly to the diffuse)
Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel > 0:
	cutout2 = 0  : Uses original diffuse
	cutout2 = +1 or -1 : Uses original diffuse when when active, defers to glowmap1 when inactive

Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel == 0:
	Defer to Glowmap1

Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel > 0:
	cutout2 = 0 or -1 : uses Glowmap2 color (will glow when active using glowmap2 color, and use non-glowing glowmap2 color when inactive)
	cutout2 = 1  : will glow when active using glowmap2 color, and defer to glowmap1 when inactive

Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel == 1:
	Uses glowmap2 color and will always glow (no animation)

Special:
	cutout2 = 2 : Behaves the same as cutout2 = 0, but with the restriction that glowmap1 must also be active

```

The inverse table is:

```
Mesh is invisible when:
	FXmap alpha == 0

Diffuse is visible when:
	Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel > 0, cutout2 = 0
	Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel > 0, cutout2 = +1 or -1 when active

Defer to Glowmap1 to decide what to display:
	Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel == 0
	Glowmap2 alpha == 0, FXmap alpha > 0, FXmap green channel > 0, cutout2 = +1 or -1 when inactive
	Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel == 0
	Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel > 0 , cutout2 = 1 when inactive

Glowmap2 is visible when:
	Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel > 0

Texture glows with Glowmap2 colors when:
	Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel > 0, section is active
	Glowmap2 alpha > 0, FXmap alpha > 0, FXmap green channel == 1
```

TLDR: If FX map alpha is 0, the mesh will always be invisible regardless of other values. If Glowmap2 alpha is 0, it will either display diffuse or defer to glowmap1 depending on the value of `cutout2` and the FX map green channel. If both fxmap and glowmap2 have alpha > 0, then it will either display glowmap2 or defer to glowmap1 depending on the value of `cutout2` and the FX map green channel.


#### Glowmap1 not set, Glowmap2 set:

Undefined. It *should* behave the same as if Glowmap1 had all values == 0 (ie it is a full black texture) and thus should will either show diffuse or be invisible depending on the values of the `cutout`, but hasn't been tested.
