# Shader Effect Modding Techniques

In this tutorial, we will learn some useful techniques which can be applied for making shader mods.

As a prerequisite, make sure to go over [this tutorial](https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Guides/EffectModdingTutorial.md) made by SilentNightSound. Make sure you understand how to dump shaders, how to edit the text file using a convenient text editor, and how to make INI files to control the shaders.

I will demonstrate using different characters, but these apply to almost all effects.

## Before you get started
The process involves lot of pausing and also repeatedly using the skill/burst in order to identify the shader hashes.
For spamming skills and burst, cooldowns and energy can be a hindrance. You can use a private server to get around this issue, although its not necessary if you have the patience to do it on official server.
For pausing, you could use the in-game pause menu, however it is quite scuffed. A better method is to use the Kamera gadget along with the [Remove UI](https://gamebanana.com/mods/424034) mod. Just snap the Kamera at the moment you want to pause and toggle the UI.
For elemental bursts which cannot be paused, you can stand next to a wall/tree etc facing it, that will prevent the burst cam and you will be able to pause.
Also preferably go to some dark place, it will be easier to see the effects.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/dilucburst.png)

This screenshot shows the game paused in middle of Diluc's burst and with a side view, using the methods discussed above.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/kazuhaburst.png)

Similarly Kazuha's burst.
NOTE: In this tutorial I am using game version 3.5. Shader hashes *can* change between different game patches, so do not expect to find the same hashes shown here in your game.

## Directly setting output channel values
The most simple method, and it was also explained in Silent's tutorial. You can directly set the values of the different channels to constant values. This will make the whole effect as a uniform color, which means it will lose some finer details.
I would not recommend using this method unless necessary, because it looks flat and featureless.
Consider Beidou's skill shown below.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/beidouE.png)

I can find the hash for the outer spiky electric effect and change it to constant orange using the below code lines.
```
o0.x = 1;
o0.y = 0.5;
o0.z = 0;
```

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/beidouEorange.png)


## Basic math operations for output channels
Lets try some basic math on the channel outputs.
```
o0.x = o0.x * 0.1;
```
This will suppress the red color within the purple effect, leaving the blue channel dominant.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/beidouEblue.png)

The green component in purple color is quite low. Lets try bumping it to 5 times the original.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/beidouEwhite.png)

Here is a bonus image showing what it looks like on perfect counter.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/beidouEcounter.png)

This method is limited in its potential when used alone, but it is very useful when combined with the upcoming methods.

## Channel Swapping and Assigning
This is where we start to cook. Colors are made of three components, RGB. At any given point on the effect, these channels can have different values.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/dilucE.png)

In the above screenshot, the part circled in pink would have all channels at high values. While the part circled in green would have mostly red at high values and other channels very low.
How do we change the overall color, while keeping the bright parts as white, and giving it a more "natural" look. An easy method here is to swap the channels around.
Let us start by swapping the red and the blue channels, on the semicircular attack trail and the fiery cloud shaders.
```
o0.xz = o0.zx;
```

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/dilucEblue.png)

The idea is that orange color contains a lot of red and a little bit of green and blue. By giving the high red value to blue channel, and the low blue value to red channel, we achieve this result without any loss of details.
This is useful when the source and the target colors are easy to achieve by swapping. But sometimes the target color needs more.
Lets try making pink. Rather than assigning the low value to red channel, we leave it as it is, but we copy the value to blue channel.
```
o0.z = o0.x;
```

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/dilucEpink.png)

Lets try inverting colors. This also affects brightness, meaning the bright areas will turn dark and vice-versa.
```
o0.xyz = float3(1,1,1) - o0.xyz;
```
Applying this to six different shaders in Kazuha's elemental skill gives us the following.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/kazuhaEred.png)

Note that this will not be very effective alone. You will need to combine it with the other methods to achieve a good result.
Here is the same method applied to five different shaders in Xiangling's pyronado.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/xianglingQdark.png)

## Restricting effects
As mentioned in Silent's tutorial, you can restrict these mods to only apply when the specific character is on-field. However, there are some characters that disappear momentarily during some of their animations. For example, Raiden's 4th basic attack sequence.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/raiden4na.png)

For such cases, we should use the hash of the elemental skill icon since it is always present when character is present on screen. At the times when skill icon is not visible, such as gliding or plunging attack, we can use the character VB hash. We can apply the effect when either of these conditions are met.
To find the skill icon hash, refer to the texture modding tutorial. Then you can make the INI file as shown
```
[Constants]
global $active
global $icon

[Present]
post $active = 0
post $icon = 0
run = CommandListCharacterControl

[TextureOverrideCharacterPosition]
hash = put_character_vb_hash_here
match_priority = 1
$active = 1

[TextureOverrideSkillE]
hash = put_character_skill_icon_hash_here
$icon = 1

; CommandList -------------------------

[CommandListCharacterControl]
if $active == 1 || $icon == 1
    x160 = 1
else if $active == 0 && $effect == 0
    x160 = 0
endif
```
That is how to prevent effects from spilling over to other characters (you can skip this part if you *want* your edits to apply to other characters too).
It is a bit more tricky to prevent unintended changes on the same character. There is no fixed way to do this, you will have to figure out how to distinguish one part of the shader from other.
Let us look at an example. Consider Keqing's infused basic attacks, which are purple in color.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/keqing3na.png)

We will convert that purple color to green using the methods dicussed before.
```
o0.xyz = o0.yzx;
```

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/keqing3nagreen.png)

However, the shader for the infused and non-infused attacks is the same. So when the infusion runs out, the shader is still affected by the edit, turning the pale yellow attack effects into a light pink.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/keqing3napink.png)

To prevent this, we want to only apply the edit when the original color is purple and not yellow. We can use the fact that in yellow color, the blue channel will be less than the green channel, and the opposite will be true for purple. So we can use the below code to isolate purple color.
```
if (o0.z > o0.y) {
  o0.xyz = o0.yzx;
}
```
With this, the infused attacks will turn green, while the non-infused will stay as it is.
Note that this kind of trick will work in many places, but in other places you will have to figure out something else.

## Dynamic color effects
So far we have learned how to modify effects in a static way, which means it just changes the colors but the new color remains same.
Now let us look at some ways to make it dynamic with time.
The first thing to know here is that shaders by themselves do not have a concept of time, and thus we must pass the time-like value into the shader via an INI file.
```
[Constants]
global $step

[Present]
post $step = $step + 1
run = CommandListShaderControl

[CommandListShaderControl]
x160 = $step
```
Here is an example of such an INI. The `step` variable gets incremented at each frame, and we can then use this in our shader.
```
#define STEP IniParams[160].x
```
For practicality reasons, I have not included full video recordings of these effects in this tutorial, but if you have followed the previous sections then you will know how to test these in-game.
Firstly let us make a simple pulsating effect. To do this we need a mathematical function that goes up and down periodically. Conveniently we have the sine function available to us. Lets use an online tool called [Desmos](https://www.desmos.com/calculator) to visualize this function.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/sine.png)

Notice however that the vertical range of this is from -1 to 1, but in terms of colors, we can only use values from 0 to 1. So we need to do some adjustment. We add 1 to this which will make the range from 0 to 2.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/sineadjusted.png)

Now we can multiply this with our color output to scale the values.
```
o0.xyz = o0.xyz * (sin(STEP)+1)*0.5;
```
You may notice that this blinks too fast. In order to make it slower, we slow down the value that goes into the sine function, like so
```
o0.xyz = o0.xyz * (sin(STEP*0.1)+1)*0.5;
```
This will make it 0.1 times it original speed, which is 10 times slower.
Let us now look at how we can make some rainbow-like effects. The key concept here is to make the different channels "pulsate" at different rates, which will result in various colors.
First we extract the grayscale value, in order to preserve the details in the effect. This can be found by the following formula.
```
float gs = 0.30*o0.x + 0.59*o0.y + 0.11*o0.z;
```
(The weird multipliers are taken from standard conversion for RGB to grayscale, which takes into account the sensitivity of human eyes toward different colors)
Once we have this, we can now make the individual channels like shown
```
o0.x = gs * (sin(STEP*0.1)+1)*0.5;
o0.y = gs * (sin(STEP*0.1*2)+1)*0.5;
o0.z = gs * (sin(STEP*0.1*4)+1)*0.5;
```
Notice the 2 and 4 written in above lines, that is how we make the function pulsate at different rates. You can try experimenting with different values to get somewhat different results, although it may not be very noticeable.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/sinemixed.png)

I understand that this may be confusing for those of us who are not familiar with the math involved, but it is what it is. Math is a useful tool, and this is just one of its applications. You can use the sample code provided here to build your mods if that helps.

It is worth noting at this point that colors are made of three components. So far we have been using RGB which is convenient for calculations. There is another system of representing color, the HSV system, which we will look into soon. But this is also a 3-component system. However time itself has only one component, so any values derived using time as a basis, will not be able to cover the full range of possible color values because it has 3 components. The TLDR is, you cannot expect to cover all possible color values in this kind of time-varying color effect.

Now let us look at a different method of varying colors, but we want to keep them as vibrant as possible, giving us the classic "gamer RGB lights" look.
This is where the HSV color model comes in. HSV means hue-saturation-value. For our purpose, we want to cycle through all possible hues while maintaining saturation and value(brightness) at maximum. Then we will convert this into RGB so that we can apply it to our effects.
Below is the formula for conversion of HSV to RGB (from [Wikipedia](https://en.wikipedia.org/wiki/HSL_and_HSV#HSV_to_RGB))

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/hsv2rgb.png)

We derive the H from our time-step variable, by using modulus function. This gives us the remainder when left after dividing by 360, which cycles over all the values from 0 to 360. Basically it gives us all the colors on the boundary of the color wheel as shown below.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/colorwheel.png)

Now we can implement the formula into code. We will define a function `getColor()` which we can use as needed. You can also implement it directly where the shader output is calculated, but I prefer keeping it separate. We put it just above the line which says `void main`.

```
float3 getColor() {
  float h = STEP % 360;
  float h1 = h/60;
  float x = 1 - abs(h1 % 2 - 1);
  float3 col1 = float3(0,0,0);
  if (h1 < 1) {
	col1 = float3(1, x, 0);}
  else if (h1 < 2) {
	col1 = float3(x, 1, 0);}
  else if (h1 < 3) {
	col1 = float3(0, 1, x);}
  else if (h1 < 4) {
	col1 = float3(0, x, 1);}
  else if (h1 < 5) {
	col1 = float3(x, 0, 1);}
  else {
	col1 = float3(1, 0, x);}
  return col1;
}

// void main....
```

Now we get the tint using this function, and multiply it with the grayscale value we had calculated in the previous section.
```
float gs = 0.30*o0.x + 0.59*o0.y + 0.11*o0.z;
float3 tint = getColor();
o0.xyz = tint * gs;
```

This will give us the gamer RGB lighting.

These are just some of the techniques you can use in your shader mods. The possibilities are endless, so explore and experiment, maybe you discover something that looks cool.

## Shader edits for model textures
So far we have looked at ways to apply shader edits to visual effects. However, everything that you see on your game is drawn by shaders. And as such they can be edited. These shaders might not be as simple as the ones we have seen so far, and I myself dont fully understand them. Nevertheless, even with this limited knowledge, it is possible to do some cool stuff as we will see now.

First let us learn how to identify the shader for the model parts over which we want to apply the edit. Character models are usually made up of multiple components, and each of these components may have different hashes.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/luminebody.png)
![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/luminedress.png)

For example, Lumine model is made of 3 components: head, body and dress. Above images show what to look for when hunting the hash for these parts.
Note that different parts of the models have different shaders, thus they can have different behaviours. Some might have a pulsating glow, some might be constant, and some might have a fixed color for glow. You have to determine this by observation.
Now, as an example, lets see how we can edit the brightness for the glowing parts.
The first thing to notice is that the glowing bits are contained in the body component. So we will dump the shader for that. In that we can see that there are a bunch of outputs.
```
...
o1.xyz = r2.xyz;
o2.xyw = r0.xyw;
o3.x = 0.0156862754;
o4.x = r0.w;
o5.x = 0;
return;
```
These are responsible for various aspects of the appearance, such as lighting and shadows etc. But for most of the purposes, we will be dealing with `o1`. First we ensure that `o1`
is indeed the one we want to edit. We do this by setting it to zero and checking the result in game.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/outputzero.png)

Now lets look at the outputs once again. By experimenting, we can isolate the output that affects only the glow part.
```
o1.xyz = o4.xxx;
```
This will make the glowing parts appear as white while other parts will be black. So now we can put a condition to increase the glow on those parts. Glow is determined in this case by `o1.w`. We can multiply it by 1.6, basically increasing the value by 60%.
```
if(o4.x>0.1) {
  o1.w = o1.w * 1.6;
}
```
One property of Lumine body component is that it takes on the color of the traveler's element. This can be changed via shader too as we will see shortly. But there is another way, which is to utilize the dress component. While it does not have any glowing parts by default, it does support a glow, which is independent of the element and energy. So we can just move the parts which need this behaviour, from body to dress. But it has more to do with model and texture editing so I won't go into much depth here. This technique has been used in [this mod](https://gamebanana.com/mods/420074). Therefore to make a similar edit in that, we need to use shader for the dress component, and apply similar code edit there.
Below are some example codes and their corresponding results. The usage depends on the result you want to achieve, and there may be different ways to get similar results. These are just here as some examples.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/tlcompare.png)

This method will work on most characters. But now let us look at one behaviour which is unique to traveler. It is how the glowing parts on body gets tinted with the element color. The information about the element color is passed into the shader by the game, and we can find this value in `cb0`. The exact index of this value may change over game versions, but basically we are looking for a line that looks like this:
```
r1.xzw = cb0[37].xyz * r2.xyz;
```
You can check that `cb0[37]` indeed contains the element color by adding the below line just before the `return` statement.
```
o1.xyz = cb0[37].xyz;
```
Now that we have identified how the element color gets applied, we can change it. Suppose we want to apply magenta color as the element tint, we replace `cb0[37]` in the line which we found earlier.
```
float3 tint = float3(1,0,1);
r1.xzw = tint * r2.xyz;
```
I dont know what `r1` and `r2` do exactly, but they are intermediate variables that eventually form the output. And for our use, we don't need to know what they do.

![alt text](https://raw.githubusercontent.com/complex31/3DMTutorial/main/shader_tech.md_files/magenta.png)

Above image demonstrates the result using [this mod](https://gamebanana.com/mods/414698). I am using it because it is easier to see than the default model.
You can also prevent the tint from getting applied by simply removing `cb0[37]` from the original line, and it will give you the same color which is there in the texture. It can be useful if you are trying to make glowing parts for the traveler and you don't want the tint.

As an exercise, I would suggest you to try applying the gamer RGB technique to the traveler element tint. It will be a cool effect.
Other than traveler, most characters take the colors directly from the texture and do not add any tint. However there are some weapons which have a fixed tint on glowing parts, such as Jade Cutter or Black Sword. This method can also be useful when modding those kind of weapons.


