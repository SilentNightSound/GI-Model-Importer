# Animated Texture Tutorial

Hello everyone. Recently, I wrote a library to add animated texture/glow support to games supported by 3dmigoto. It currently only works for Stella Sora (extending the RabbitFX library by CaveRabbit), with no current plans to extend to other games at this time.

See download section for example code. You can use left and right arrow keys when the mod is visible to move through examples covered in this guide, and up and down to move through the sections (Basic/Intermediate/Advanced)


## Overview of textures and commands 

High-level overview of all the commands. Each of these will be explained in more detail in the tutorial section. See addendum for additional notes on texture colorspaces

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
`$\RabbitFX\cutout1`  

; Same as above, but for glowmap2. Not required if not setting glowmap2  
; If both glowmap1 and glowmap2 are active, these take priority. If not specified, they are all set to `0`  
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

The following examples will go through the basic usage of the library. I will demonstrate them on a flat plane for simplicity, but the concepts will work on a mesh of any shape.

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

For this example, we change the FX map and give it a blue channel of `63` (`0.25`). The blue channel controls how much hue shift is applied when it is active - `0.25` means that it applies a maxmimum shift of `25%` or 90 degrees.

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

Next, we demonstrate how we can use use two glow maps simultaneously. We will add a second dot that is flashing twice as fast as the first one.

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

The reason we need to use a second glowmap here is becase we want the two dots to flash at different speeds. If they were the same speed, we could just add the dot to the first glowmap. Note that the library is currently limited to a max of two independent glowmaps - while adding a third dot that blinks with a different speed to the first two isn't impossible, it's not as simple since there is no Glowmap3 and would require some very creative coding. I recommend trying to limit any animations to at most two independent glowmaps/speeds.

In situations where the effects from glowmap1 and glowmap2 overlap, glowmap2 will take priority. For cutout, think of the textures being layered like glowmap2 > glowmap1 > diffuse - if cutout2 is set, when glowmap2 is inactive you will essentially be able to see through it to the layer "below". So if glowmap1 is active or has cutout1 not set, you will see glowmap1 below. If glowmap1 is inactive and has cutout1 set, you will either see the original diffuse texture (if alpha > 0 on glowmap1) or the mesh will be cut out and not visible (alpha = 0)


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

[IMAGE]

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

`(upperbound-lowerbound)*(time/cyclelength)%1 + lowerbound` 

for creating a cycle between lowerbound and upperbound with length cyclelength. 

Just be aware that since we are changing the size of the range, you may need to adjust the cyclelength timing (even though this cycle still takes `3` seconds, it spends `1.5` seconds out of bounds and `1.5` seconds in-bounds - if you wanted `3` seconds in-bounds, you would need a cyclelength of `6` instead). Also be careful with setting lowerbound and upperbound too far away from the original 0 and 1 boundaries. You can see that with `0.5`, the animation will already spend more than half the time inactive - something like `-0.1` and `1.1` is probably better in this case to minimize that effect:

`$\RabbitFX\Time1 = 1.2*(time/3)%1 - 0.1`

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

There are two values associated with movement: `moveX1` and `moveY1` (+the corresponding ones for glowmap2, moveX2 and moveY2). These represent the amount to shift the UV maps of the texture in the X and Y direction - a positive value represents movement to the right and up, while negative is left and down. You can pass in any number, but note that the range is `[-1.0, 1.0]` - anything with an absolute value larger than `1.0` will just be shifted back into this range (so `1.6` will be treated as `0.6`, `-5.3` is `-0.3`, etc. Think of `1.6` as meaning "move 1 full cycle then 0.6 of a cycle" which results in a movement of 0.6)

By setting moveX1 and moveY1 to static values, we can give a constant offset; by setting them to dynamic ones, we can create movement. The simplest dynamic value to use is time:

`$\RabbitFX\movex1 = (time/5)%1`

This will cause the dot to move to the right, taking 5 seconds to return to where it started. Meanwhile:

`$\RabbitFX\movey1 = 1-(time/20)%1`

This will cause the dot to slowly move down, taking 20 seconds to complete a full cycle.

It's possible to use this in tandom with the previous effects and a second glowmap to create fairly complex movement - we will explore some more advanced applications in the intermediate and advanced sections

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

The following examples will show some more complex use cases that use multiple features at the same time. I would recommend at least skimming the basic examples in the first section to learn the syntax before trying these.


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

[VIDEO]



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

[VIDEO]

Here, we demonstrate how to create basic animated tattoos.

For Glowmap1, we use a static image of sucrose. For Glowmap2, we use the glowing eyes overlay. We want sucrose to always be visible (of course), so the FX map will all black on any section that overlaps with her. For the eyes, we want gradually increase in intensity from the inside outwards, then fade back the same way - we can use the same idea as example 2, by using a gradiant on the FX map:

[IMAGE]
[VIDEO]

This will half work, but the problem is that it will fade from the inside out, which is the opposite of what we want (we want it to appear inside-out, then fade outside-in). We will go over how to do this in more detail in example 6, but for now the basic idea is that once we reach the maximum glow, we want the time variable to start travelling backwards instead of continuing forward. That will ensure the center remains in the range, while the edges gradually fade

`time`

Also note that we still have an entire glowmap to play around with - we can add some light gradient glow effect on sucrose herself by adjusting the FX map:

[IMAGE]
[VIDEO]


A practical application would be something like a dragon tattoo:

[VIDEO]


### 5) Digital Clock

We create a simple digital clock that counts seconds between 0 and 9





### 6) Bobbing Movement

Next, we explore other types of movement beside scrolling - it is possible to cause an object to move up and down instead of looping around the screen. We use this to animate a ship bobbing on the waves

[VIDEO]




### 7) Falling rain/teardrops

[VIDEO]

8) Travelling dragon

An example of a dragon travelling to the right

[VIDEO]

X) Moving glow on clothing

The first example that actually uses the original mesh, 

[VIDEO]




## Advanced Applications

The final section will use the knowledge we have gained in the previous two sections to implement some complex animations/effects. Make sure you have a solid grasp of how the examples in the first two sections work


1) Traveling Rainbow Circuit

A modified version of the final example from the intermediate section, to demonstrate ways we can control the color of the effect

X) Matrix-style numbers

A combination of the rain and number example from intermediate to create a matrix-style falling effect


X) River of stars/sky

X) Flames/Smoke/Lightning

X) Radial lightning/lines

X) Rotating halo

X) Rotating magic circle

X) Analog Clock

X) Shorekeeper-style effect (or paimon cape)

X) Flappy Bird


## Addendum

### Colorspaces:

The FX texture expects a linear colorspace, while the glow textures expect srgb colorspace. If you are using a tool like paint.net, make sure to select the correct export type.

While paint.net is a good tool, it has some issues with DDS compression; if you are noticing odd artifacting on your textures, there are a couple of alternatives:

1) Save as png and convert via magick: magick.exe .\Dots.png -colorspace sRGB .\DotsTest.png . Smallest size and no compression issues, but may have compatibility issues on some systems/OS
2) Use nvidia texture tools (exports as linear by default, can change in export transfer function. Don't export mip maps, rest is default)
3) Photoshop with either intel texture works or nvidia texture tools
4) texconv tools (may result in crunchiness, texconv sometimes won't use the correct color space)

Do NOT use blender dds export or photoshop default dds export, they don't work properly as of the time of writing this guide

Also note that behaviour may be odd around the edges - I recommend leaving a small gap (~0.01) around the edges and avoiding numbers that are very close to 0 or 1.0


### Setting textures using RabbitFX

For stella sora and star rail, RabbitFX supports setting diffuse, lightmap via calls:

Resource\RabbitFX\Diffuse = ref ResourceDiffuse
Resource\RabbitFX\LightMap = ref ResourceLightmap

Stella sora specifically also has a specular map
Resource\RabbitFX\SpecularMap = ref ResourceSpecularmap

Along with the ability to set custom outlines via
Resource\RabbitFX\OutlineMap = ref ResourceOutlinemap

For more details, please refer to the rabbitfx page of your game
