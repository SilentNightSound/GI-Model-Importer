## 3DMigoto GIMI 效果与着色器教程

本教程将介绍改变原神的效果的过程，如技能效果，灯光效果，以及任何未通过纹理或缓冲区控制的游戏内对象。学习着色器如何工作将显著增加你能够mod的范围。

这个效果修改教程比我之前的基本网格编辑/导入和纹理编辑更难，但阅读这些并不是理解本教程的先决条件。

我粗略地按照难度增加的顺序安排了本教程，所以即使阅读第一节也足以进行简单的编辑。后面的章节将需要基本的编程知识。

我将列举三个逐渐复杂的例子: 

-	改变角色的攻击/技能颜色(请参见 https://gamebanana.com/mods/409181 关于甘雨的冰攻击重新着色的例子)
-	创建一个随着时间的推移在多种颜色之间切换的效果(请参见 https://gamebanana.com/mods/418434 关于圣诞树改变灯光的颜色的例子)
-	演示如何创建基本效果动画(请参见 https://gamebanana.com/mods/420434 关于Cyber Bodysuit Raiden的动画线条的例子)

## 前提条件

安装3dmigoto GIMI Dev版本(绿色文本需要可见)。

## 重要说明

默认情况下，我禁用了GIMI转储着色器的能力，因为它们可以干扰mods。你可以通过确保d3dx.ini的`marking_actions`行在列表中包含`hlsl`和`asm`来重新启用它们。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211983955-7a13e1a0-542e-435f-ab67-aa5e78031bd7.PNG" width="600"/>
</p>

另外，如果你在尝试本教程中的内容后遇到mods问题，请尝试清空ShaderFixes文件夹-有时转储的着色器会导致某些mods出现故障。

让我们开始吧！

## 改变角色攻击颜色(迪卢克的火焰)

对于第一节，我将演示如何重新着色迪卢克的火焰。这章节是基本/中级难度，不需要任何先前的编程/着色器知识。

1.	首先，我建议你去一个屏幕上的物体尽可能少，但你想要的效果仍然会显示的地方。你很快就会看到原因，但屏幕上的对象越多，我们寻找着色器的时间就越长。起始海滩区域总是一个不错的选择

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211985874-1e3a43e6-bb5e-48e1-9b8c-c99a199595a0.png" width="600"/>
</p>

2.一旦你找到了一个好的位置，触发你想要的效果并进入暂停菜单。在这种情况下，我们对迪卢克技能的火焰效果感兴趣，所以我们按下e然后暂停（注意:对于只有在游戏未暂停时才显示的效果，仍然有可能获得稍微困难一点的效果——我稍后会解释）

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986006-20e3e92b-29c4-4f3e-8808-bf151fb72e97.png" width="600"/>
</p>

3.	现在，我们要在数字键盘上按`1`和`2`来循环像素着色器(`PS`)。有两种类型的着色器-顶点着色器(`VS`)，它控制物体在屏幕上绘制的位置，以及像素着色器(`PS`)，它决定它们的外观和绘制纹理/颜色。因为我们对颜色感兴趣，所以我们想要PS

4.	当你找到正确的`PS`时，这种效果就会在游戏中消失。例如，下面是控制挥动中心火焰的着色器:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986075-16734f42-e46b-46ab-a46f-b2a8ac8c0821.png" width="600"/>
</p>

这个控制着周围的火焰云:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986124-523e0fe5-f134-4fcd-b8ad-588bcf158f06.png" width="600"/>
</p>

我们从这两个开始。

5.	在数字键盘上按` 3 `将PS哈希值复制到剪贴板，并将着色器保存到ShaderFixes文件夹中。上面两个着色器的哈希值是` e75b3ffb93a1d268 `和` dd0757868249aaa5 `(注意:如果你需要快速回到起点，你可以按数字键盘上的 ` + `将缓冲区重置为0)。注意，着色器哈希值可以在不同版本之间改变，所以你的哈希值可能不相同

6.	着色器现在应该显示在ShaderFixes中，名称类似` hash-ps_replace.txt `。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986246-48a6ccdb-e779-4e13-8b1e-ce02bcb1b044.png" width="400"/>
</p>

如果它们在数字键盘上按下`3`后没有显示，请确保你将`hlsl`和`asm`放在`marking_actions`中，正如顶部的重要说明中提到的那样，并使用`F10`刷新。

还要注意的是，少数着色器不会正确地反编译为` hlsl `(高级着色器语言)，而是会恢复为` asm `(汇编)。这些着色器仍然可以工作，但编辑起来会更加笨拙。我不会在本教程中介绍asm，但概念是相同的-着色器的语法只是更难阅读。

7.	用你选择的文本编辑器(Notepad/ notepad++ /Sublime text /随便什么)打开它们。这个文件一开始看起来很吓人，但是不要担心——你不需要了解细节就可以进行基本的更改(我将在后面的章节中详细介绍这个文件的工作方式)。
	
<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986377-e2fd3418-f673-4cf8-9ff1-938faf945c76.png" width="400"/>
</p>

8.	现在，我们最感兴趣的是处理输入和输出。这些都列在main下面——这个文件有9个输入(编号为` v0 `， ` v1 `， ` v2 `，…` v8 `)，有一个输出(` o0 `)。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986455-0a5ca895-c3a7-4066-a59f-be71fe2634e6.png" width="300"/>
</p>

9.	通常从输出开始是最简单的。它有一个` float4 `类型，这意味着它有一个` x `， ` y `， ` z `和` w `组件，并接受一个浮点数(即十进制)作为输入。我们可以通过在代码末尾放一行来强制将值设置为常量，来看看它是怎么做的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986560-b25728ae-e24a-4fe1-929e-0d49bf02dadf.png" width="300"/>
</p>

（`//`和`/**/`表示代码中的注释，并被程序忽略。3dmigoto还将`asm`代码导出到`hlsl`代码下面——当我说`end`时，我的意思是`return`之前，而不是之后。该点之后的所有内容都被注释掉，默认情况下不会运行。如果你看到像`div`、`mul`和`mov`这样的内容，你跑得太远了）

基本上，我们所做的就是覆盖游戏计算的值，并将其替换为我们自己的值

10.	保存文件，然后在游戏中按`F10`重新加载(确保也按`+`重置缓冲区!)3dmigoto会自动从ShaderFixes文件夹中加载着色器。这就是所发生的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986773-ee66b8c6-2d80-44fc-b1cf-fa8e41f4f9db.png" width="600"/>
</p>

中线变成了黑色，火花变成了绿色。如果你熟悉颜色是如何存储的，你可能会猜到` o0.X `表示，但我们可以继续检查以确保:

将` x `和` z `组件设置为0，` y `设置为1:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986865-67fb5c91-3c25-4df7-8821-c5b11c3531fa.png" width="300"/>
</p>

设置所有内容为绿色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986940-01ebfc18-ef72-4c60-b7e2-91985bf9c2b1.png" width="600"/>
</p>

同时将`x`和`y`设置为0，`z`设置为1

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986994-c3070f3f-9eb5-480a-b8ed-13ab90076c80.png" width="300"/>
</p>

设置颜色为蓝色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987033-f9a1b299-9676-4687-9ae9-808db2b84b3d.png" width="600"/>
</p>

或者换句话说` o0.xyz `对应效果的RGB颜色。并不总是`o0`是颜色——一些着色器有多个输出，所以颜色可能是`o1`或`o2`等;值得庆幸的是，这个着色器相当简单，只有一个输出`o0`。

(如果你想知道`w`代表什么，它似乎与效果的宽度/发射有关:)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987161-edd09e67-99e8-42ff-9653-9aafadda4531.png" width="600"/>
</p>


11.	现在我们知道了这些值对应的是什么，我们可以对颜色进行基本的更改。例如，设置三个` o0.xyz `到0会导致迪卢克的火焰变成黑色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987214-bc9c7a29-1bf0-483d-bb9d-7cba39afd1da.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987253-b4480e4e-b3f3-4726-b66d-cb8e5c698815.png" width="600"/>
</p>

或者我们可以把它们变成紫色，把` r `和` b `设为1，把` g `设为0:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987317-f0237be8-da62-43d1-8d0f-7f6447872f09.png" width="600"/>
</p>

注意，我们也不局限于设置常量-我们也可以改变颜色的色调。这减少了攻击中的红色数量，同时增加了更多的绿色和蓝色，以创造一个鲑鱼粉的颜色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987374-be4661b0-46aa-4829-82c0-2274175a8b6e.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987415-bf5057ee-1c20-4e19-8195-0c3ace4fd26f.png" width="600"/>
</p>

注意，与我们强制设置常量的情况不同，火焰纹理在这里仍然可见。

我们甚至可以做一些更花哨的事情，比如将值设置为数学表达式，但我将在最后一节中讨论这个问题。

除了改变输出，我们还可以使用类似的方法通过改变输入来改变效果(将这些行放在它们正常加载之后，并覆盖游戏的值)，尽管你需要尝试去推断哪个变量改变了什么。

12.	这是改变效果颜色的基本过程——找到哈希，转储它，然后修改输入或输出。然而，如果你一直在跟进，你可能已经注意到并不是所有的火焰纹理都被替换了-还有更多的我们需要转储:

`0fa220b5adced192` 是火花:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987510-3d411b42-0e3a-4d69-8081-e8b2ebf8707f.png" width="600"/>
</p>

`bf7eb60b256538c7` 是剑边的火焰:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987559-c100eec0-4a7f-4039-8873-bfb3b2d9308e.png" width="600"/>
</p>

`439c03865c4ce77e` 是鸟:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987610-6a3362cf-bcb9-4d9f-b1a7-a47feb245bc4.png" width="600"/>
</p>

`7690cf4aa6647c6c` 是元素爆发期间的剑辉:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987673-309f0467-ba0f-40ae-94cc-256912c056c0.png" width="600"/>
</p>

收集所有不同的着色器是在编辑效果时所花费的大部分时间。

13.	即使把上述所有的都变成黑色，你可能已经注意到在我们不能暂停游戏的元素爆发期间仍然会出现火焰效果:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987723-01d3c4ba-f86d-4139-a0d2-468af27e8229.png" width="600"/>
</p>

获取这些着色器比较麻烦，但并非不可能。第一种方法是在grasscutter身上启用无限爆发能量，并在能量满溢时反复施放元素爆发。这将花费一些时间，但应该适用于任何可重复的事情。

(更新:我收到了另外两种你可以从爆发中获得着色器信息的方法的建议:一种是站在浅水区或背对着墙来禁用爆发相机。这将让你在爆发时正常暂停，给你时间循环哈希:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/212235277-b8d9de11-78d7-4f97-8c09-dc220be72980.png" width="600"/>
</p>

第二种是使用像Akebi这样的作弊软件将游戏速度降低到1以下，这样你就可以用慢动作观看效果。请注意，如果在官方服务器上使用作弊软件，可能会导致封禁，所以如果你决定使用这种方法，我建议只使用私人服务器。

非常感谢ComplexSignal31#5778和NK#1321的推荐!)

然而，对于只在过场动画中出现或难以重现的效果，最快的方法是进行帧转储。关于如何执行帧转储的更多细节，请参阅纹理修改教程，但本质上，当效果在屏幕上显示时，你按`F8`来执行转储，同时效果是可见的。

不幸的是，由于我们不知道着色器哈希，它将需要一个完整的转储，所以确保你有5-10GB的空闲空间和屏幕上尽可能少的对象。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987810-78fc6d7f-1f98-4474-8e59-86d155378fda.png" width="300"/>
</p>

当你有了按下`F8`后创建的帧分析文件夹时，你可以通过它来查看效果何时绘制。`o0`和`o1`文件显示了每个ID所绘制的内容，对于分离在屏幕上绘制效果的确切ID非常有用。

例子: `000351-o0=3315d2b5-vs=eb65cb4eba57132b-ps=7690cf4aa6647c6c.dds` 看起来像在我的帧转储这样:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987902-faaa47f5-db4e-42b6-96c4-ea3629da0480.png" width="600"/>
</p>

而 `000352-o0=3315d2b5-vs=f6a1f24f9c9b28c2-ps=a69e25f25a6c8e04.dds` 看起来是这样的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987954-5e042475-bddd-4168-a834-0cfb55578c49.png" width="600"/>
</p>

所以我们知道，在这一帧中，绘制调用 `000352` 负责地面上的发光效果。我们还可以从文件名 `ps=a69e25f25a6c8e04` 中获得哈希值。

使用这个方法，我们可以找到剩下的哈希值:

`000353-o0=3315d2b5-vs=f50ce30bb0caf55c-ps=4d4da8a4cbe1149a.dds`

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988024-d44e4331-8232-43d7-b536-9784b0fb6ee4.png" width="600"/>
</p>

和 `000365-o0=3315d2b5-vs=72ce1e39ede0982f-ps=622a52d3edcf0363.dds`

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988083-9efb97a2-9d6d-48fc-8faa-878dc85f48c7.png" width="600"/>
</p>

14.	现在我们有了剩下的哈希值，我们需要转储它们。按数字键盘 ` + `重置缓冲区，施放元素爆发，然后开始使用数字键盘 ` 1 ` / ` 2 `循环，而效果在屏幕上。即使在我们到达哈希时，效果已经离开了屏幕，只要我们在效果出现在屏幕上时开始循环，它就会显示在列表中，并且可以转储:

PS ` 4d4da8a4cbe1149a `即使元素爆发没有激活显示的例子:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988198-9a6ddd0e-e55b-4783-8602-d21bca4d61c0.png" width="600"/>
</p>

使用这个技术，我们可以转储剩下的着色器 `a69e25f25a6c8e04`， `4d4da8a4cbe1149a` 和 `622a52d3edcf0363`:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988253-5f67709e-62b5-4a17-ad21-3dd99de90bd3.png" width="600"/>
</p>

15.	修改完成了!或者……也许不是。如果你切换到另一个火系角色，比如胡桃，你可能会注意到一个问题:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988307-de6a26dd-a26a-45ea-a760-4c694ed82dca.png" width="600"/>
</p>

我们已经把所有的火焰都设置为黑色，不只是迪卢克的。此外，如果其他人创建了一个mod，改变了其他角色的火焰，如胡桃或可莉的，它也会与迪卢克的重叠。

16.	我们想要一种方法来限制效果，只有当迪卢克在场上时才会出现。我们有几种方法可以做到这一点，但它们都遵循相同的基本原则-我们确定了当迪卢克在场上时引起的某些条件，然后仅在该条件为真时应用这些效果。

这是一个更高级的主题，在你玩了更多的着色器和阅读后面的部分后会更有意义-如果你有理解这个问题，试着阅读下面的部分，然后再回来。

首先，我们需要确定迪卢克唯一的哈希值。为了简单起见，我将使用迪卢克的`VB` 哈希 `56159d74` (` VB `可以与数字键盘 ` / `和` * `循环，并使用数字键盘 ` - `复制):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988418-a6af34f5-b9dc-4446-aa84-44ddf93a435c.png" width="600"/>
</p>

17.	接下来，我们构建一个` .ini `，我们将使用它来选择性地应用效果。我们定义了一个名为`$ActiveCharacter`的变量，并在每一帧开始时将其设置为0 (` [Present] `在每一帧开始时运行一次)。当迪卢克在场上时时，我们只将值设置为1，由匹配的VBhash表示:

```
[Constants]
global $ActiveCharacter

[Present]
post $ActiveCharacter = 0

[TextureOverride迪卢克VB]
hash = 56159d74
match_priority = 1
$ActiveCharacter = 1
```
这里的`match_priority`只是为了确保这个效果不会干扰任何加载的迪卢克mod -如果你将这个效果作为一个mod的一部分而不是单独添加，你不需要包括它。

18.	现在，我们有两种方法来分离着色器。两种方法中比较简单的是简单地定义一个自定义着色器并执行替换，然后创建一个`shaderoverride`，并且只在迪卢克是活动角色时运行自定义着色器:

```
[ShaderOverride迪卢克Flame]
hash = 4d4da8a4cbe1149a
if $ActiveCharacter == 1
	run = CustomShader迪卢克Flame
endif

[CustomShader迪卢克Flame]
ps = 4d4da8a4cbe1149a-ps_replace.txt
handling = skip
drawindexed = auto
```

这通常会工作，但3dmigoto有时不能正确编译` hlsl `如果这样做会导致错误。同样，它也不会对` asm `起作用。但优点是，着色器可以捆绑在mod文件夹与mod的其余部分，它不会影响如果另一个mod试图修改相同的着色器。

另一种方法是传递一个自定义变量给着色器，只有当变量匹配时才执行效果。下一节将更详细地讨论这一点，但本质上你想为每个着色器创建一个这样的部分:

```
[ShaderOverride迪卢克Flame]
hash = 0fa220b5adced192
x160 = $ActiveCharacter
```

然后在着色器中定义一个新的常量:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988660-d2ffb89b-67bc-4583-afc3-3b5bd6270230.png" width="400"/>
</p>

并且只在常量等于1时才执行效果(例如角色在屏幕上):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988744-da6a9f46-aa2c-4dc9-8050-7d225adb241e.png" width="400"/>
</p>

这样一来，迪卢克就保持了这样的效果:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988793-72e1a43c-25e5-4b4a-b024-2a2aae0d99ee.png" width="600"/>
</p>

而胡桃的则是正常的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988856-0cb0690a-b65f-4db7-96e3-75e0f04dfde5.png" width="600"/>
</p>

在运动中(我留下了一些红色效果作为对比):

https://user-images.githubusercontent.com/107697535/212006132-08528c9c-2069-451c-9d78-bd1737768bb4.mp4


## 将自定义值传递到着色器(循环颜色)

在本节中，我将演示如何从`.ini`文件加载自定义值到着色器，以及如何使用它来制作多种颜色之间循环的效果。我还将演示如何找到着色器中控制发射的部分，这比仅仅是效果颜色更具挑战性。

本节属于中等难度，我假设你已经阅读了前一节的大部分内容，并且至少对`.ini`文件和着色器有一些基本的熟悉(例如，知道如何打开它们，至少模糊地理解不同的部分)。有基本的编程知识。

1. 像以前一样，我们从收集着色器哈希开始，这次是钟离的柱子:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990319-6809dcff-aa24-46de-8d50-56e21511f384.png" width="600"/>
</p>

与迪卢克不同，这个hash不会导致整个柱子消失——只会导致纹理消失。这是因为它是使用多个着色器绘制的，所以即使我们跳过对象的一部分，仍然会绘制(在这种情况下，柱子的轮廓仍然保留)。

本例中的哈希值是 `4c99fec14dca7797` – 按` 3 `将着色器转储到ShaderFixes。

我们的最终目标是改变黄色裂隙效果的颜色，而其他部分保持不变。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990446-34c57fcf-fb0a-495a-adf0-4c3834236f0f.png" width="200"/>
</p>

2. 打开着色器，我们可以看到它比以前的9个输入和6个输出更复杂。这是因为着色器负责做很多事情，比如绘制纹理，处理发射，计算阴影等。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990505-a83e9b5d-e53f-4d81-8bf1-4b88224c4b3f.png" width="300"/>
</p>

我们首先尝试与前面相同的方法——将每个输出设置为常量，以了解它们控制的内容。

3.` o0 `似乎与轮廓有关，使它们变得更厚和更薄(有点难以看到，但可以使用` F9 `在修改模式和无修改模式之间来回切换):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990621-0a6ae9bb-00d8-4da2-b533-bc49e373b2d4.png" width="200"/>
</p>

`o1.xyz` 似乎和之前一样对应颜色RGB，而` w `似乎控制亮度

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990706-ae3443bf-e591-49a0-a071-6725d806bb0e.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990739-c4ebdbbe-de56-4f48-a223-6f3dba5c59ce.png" width="600"/>
</p>

`o2` 似乎还能控制颜色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990811-c07390a1-2d01-4d98-b220-8914a03b2b34.png" width="600"/>
</p>

`o3`-`o5` 不清楚，但似乎影响线粗细。

但是，你可能已经注意到一个问题——所有这些选项都会改变整个柱子的颜色，而不仅仅是黄色地理线!我们必须再深入挖掘一下，以找出这是如何处理的。

4. 在我们继续之前，让我更详细地解释着色器中最重要的符号:

- `v0`,`v1`,`v2`..etc. 是vb文件中加载的输入数据，也就是说，与顶点位置、顶点颜色(与纹理颜色不同!)、uv贴图、混合权重等相关的数据。
- `o0`, `o1`, `o2`… 是输出目标，是实际绘制到屏幕上的东西(或者在顶点着色器` VS `的情况下，传递给像素着色器` PS `的东西)
- `t0`, `t1`, `t2`… 是纹理-典型的像DDS纹理，尽管它们在某些情况下也可以是缓冲区。当你在.ini文件中看到` ps-t0 `， ` vs-t0 `， ` ps-t1 `， ` vs-t1 `等时，这就是它们对应的
- `r0`, `r1`, `r2`… 寄存器——这些是着色器用来存储计算结果的临时变量
- `cb0`, `cb1`, `cb2`… 常量缓冲区-这些是游戏传递给着色器的值，代表当前游戏状态的值，如对象的全局位置或自游戏开始以来传递的时间

考虑到这一点，我们可以专注于我们感兴趣的代码部分，而不是试图理解所有200多行代码。

我们感兴趣的是钟离柱子的光芒。查看柱子的纹理，我们可以看到diffuse纹理包含alpha层之上的发光部分，并加载在插槽0(第一个哈希来自柱子的hash.json)。或者通过查看创建的mod，看到diffuse加载为` ps-t0 `):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991323-68087da3-c621-4238-a994-50e3859837a5.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991357-5a0c0cee-eb64-410c-875f-db1576e107b9.png" width="300"/>
</p>

因此，我们感兴趣的是代码中涉及到变量` t0 `的任何部分，这对应于diffuse纹理。具体来说，我们最感兴趣的是任何涉及w组件的东西，因为它代表发光部分。

5. ` t0 `在着色器中被加载了两次:一次是在第100行左右的变量` r2 `中:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991507-ed958308-a38f-40dc-a056-5d663f389052.png" width="400"/>
</p>

还有一次在第235行左右，输入变量` r0 `:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991578-04bb9823-8bb5-4523-a0f5-2b81e4f32502.png" width="400"/>
</p>

有很多方法可以通过阅读代码来判断哪个是正确的，但尝试每种方法也可以:

设置`r2.X `作为第一个代码块中的常数:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991690-68c079f5-5111-4b09-90ae-e7120338b791.png" width="300"/>
</p>

将柱子变成绿色，但保持正常的裂隙效果:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991731-c2bbb878-2a7b-401d-8d79-0020e46e92e5.png" width="600"/>
</p>

所以我们应该去第二个代码块附近看看。颜色很可能是由一个有3个组件的变量表示的(每个颜色通道一个组件)，最接近该块的是`r1`，它显示在3行以下:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991835-9983b92e-4ee2-4541-b546-2a5a9a560ed8.png" width="300"/>
</p>

如果我们设 `r1.x` 为1:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991910-4e13e1e6-ac7c-4b7d-879e-305903c5632a.png" width="300"/>
</p>

我们得到:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991957-54261de6-263f-491b-bfa9-e1cdd4bf7ffd.png" width="600"/>
</p>

成功!这个`r1`值是控制柱子辉光的RGB(我们将红色组件设置为0)。

(注意:这并不意味着` r1 `总是负责代码中所有地方的柱状辉光颜色，只是它保留了这个特定时间点的柱状辉光。寄存器值在执行计算时被着色器重用，因此每一个所代表的`含义`可以从一行到一行地改变，不像输入和输出)。

同样的基本原理也可以用在其他情况下，找到着色器的哪个部分控制输出-从你知道的某个组件开始，它与你正在寻找的任何东西(比如纹理，或特定的vb值)，然后搜索周围的着色器代码，并尝试找到它。

6. 然而，只有一种颜色是无趣的-如果我们可以设置任何我们想要的颜色呢?实际上，可以将自定义值从` .ini `文件传递给着色器。

首先，在3dmigoto声明的文件顶部定义你想要使用的变量(180是任意选择的，但理想情况下你应该选择超过100的数字，这样它们就不会意外地干扰游戏使用的变量)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992100-bce019e7-bf54-442e-a4b3-52f856352fb4.png" width="400"/>
</p>

接下来，我们将R、G和B设置在上一部分中找到的t0行以下

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992193-e24ab261-b997-4cb7-9a9c-59e02a9bff5f.png" width="300"/>
</p>

(注意:` r1 `有一个` x `， ` z `和` w `组件，而不是` x `， ` y `和` z `组件。它们仍然对应RGB，只是字母不同)

最后，在.ini文件中，当我们看到柱子的` IB `时，我们将设置三个值:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992258-b40caa68-9a4e-4d16-bfd6-63b60ad8e7b5.png" width="200"/>
</p>

(你可以通过使用数字键盘 ` 7 ` / ` 8 `循环找到柱子` IB `，直到你找到令柱子消失的IB，或者通过查找hash.json):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992424-ddbab70d-4fdd-42e8-996b-4c8cde2337f3.png" width="600"/>
</p>

成功!我们将线条设置为红色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992488-bc79ec9e-2155-4142-8b00-89cd264c6308.png" width="600"/>
</p>

我们可以通过改变.ini值将它们设置为其他颜色;这将把它们设置为紫色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992526-3ad6084c-60b6-402d-b265-d59e9aa09757.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992599-f58f70da-1ebb-41c5-8f1f-bf0f690a1c5d.png" width="600"/>
</p>

但是，请注意这并不完美——我们已经失去了一些动画效果，以换取自定义颜色。我将在本教程的最后一节中介绍实现动画的方法。

7. 我们还可以做更多的事情。一种颜色很棒，但如果我们能在它们之间自动循环呢?3dmigoto有一个叫做`time`的特殊变量，它表示游戏开始后经过的秒数。我们可以使用它在颜色之间自动循环:

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

它所做的是将当前时间放入3个桶中的1个，然后根据当前时间将柱子设置为红色、绿色或蓝色(每3秒循环一次)。通过改变数字，你可以设置它的周期更快或更慢，或添加/删除颜色，等等。

https://user-images.githubusercontent.com/107697535/212007147-b94b5eda-ca1d-40ee-938e-25d5e7b1f913.mp4

8. 最后，类似于之前，我们可以在` .ini `中加载着色器，而不是将它放在shaderfixes中:

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

这在大多数情况下是可行的，但是这里的编译中有一个小故障，会导致柱子消失后留下大约1秒的残留:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211992799-823cb1d7-cb97-469a-b1d0-6d80affed8a8.png" width="600"/>
</p>

也可以限制这个着色器，特别是当钟离在场上时，尽管在这种情况下，我不知道有任何其他对象共享这个着色器，所以它不像迪卢克的火焰那么重要。


## 动画效果

在这最后一节中，我将演示我们如何使用前两节的原理来创建简单的动画效果-我将通过在 cyber bodysuit raiden (https://gamebanana.com/mods/420434) 中创建动画线条的过程。本节是高级的-我将假设你理解前两节，知道如何制作mod，以及有一些基本的编程知识。

1. 首先，我们找到在雷电将军上控制绘制纹理的着色器:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994076-18855a3d-7400-4315-9c86-34320c9c1393.png" width="600"/>
</p>

雷电实际上使用至少两个——一个为身体对象和一个为服装对象——但我们对身体对象感兴趣，因为它具有我们需要的发射效果（之前通过反复试验发现的）

哈希值是 `7d2763cf91813333`, 我们将它转储到ShaderFixes。

2.现在，我们寻找着色器中负责发射的部分。发射位于diffuse纹理（位于槽0中）的alpha层之上，因此我们正在查找与`t0.w`相关的内容。着色器中只有一条相关的行:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994193-4a061233-20e7-4817-871d-499d04b209be.png" width="400"/>
</p>

经过测试，我们发现它是发光的原因:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994259-272abaad-7bb2-452a-ab81-b28a3c97c8ed.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994318-7846346e-6614-4dfc-a793-32ac6af1d173.png" width="600"/>
</p>

我们只能通过添加一个条件来修改她的纹理的发光部分，该条件仅在alpha值大于某个任意数字的像素上触发:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994369-a97f22ad-3d00-4aa0-846a-a69596874609.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994415-6582a59d-8ac1-464a-a245-b55ea3c4c28b.png" width="600"/>
</p>

3.现在，我将演示添加线条到我的cyber bodysuit raiden mod的过程:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994483-bf30fc5b-248a-44ea-84b4-6d3bb867b502.png" width="600"/>
</p>

首先，我绘制了线:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994549-4268e3f1-0f26-462f-a8c9-598f5295aa3a.png" width="500"/>
</p>

我是通过Blender纹理绘制选项卡完成的，但你也可以使用paint.net\/photoshop直接在纹理上绘制。注意，对于diffuse纹理，最终输出必须是 `BC7 SRGB` `dds` 。另外，不要像我一样——在一个单独的图层上画这些，这样你以后就可以很容易地把它们分开;-;。

4. 在alpha图层上移动线条后，最终的纹理看起来是这样的(注意:它很宽，因为我把几个模型合并在一起，并把它们的纹理并排放在一起):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994700-5f1401f1-a7cb-4f7a-82bf-057638c2e6d3.png" width="700"/>
</p>

这让我们在游戏中看到了发光的线条

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994819-843f583b-91d2-4de3-b4ef-153c6199f540.png" width="600"/>
</p>

5. 现在，是时候执行一些基本的动画了。我将线条从diffuse纹理中分离出来，放入另一个空白纹理中，我将其称为`control`纹理:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994886-0ead61d0-d16d-4029-8e43-376599f51806.png" width="700"/>
</p>

这个纹理本质上是我们要用来告诉着色器纹理的哪些部分会有动画效果的(因为diffuse/光贴图的所有四个通道都已经在使用中)。这个纹理的类型应该是` BC7 Linear `，因为我们希望颜色值是均匀分布的。

为了简单起见，我也将它重新上色为黑色-为了保持事情简单我们不会在这个例子中使用特别的颜色，所以我们设置所有的颜色通道相等;如果你愿意，你可以使用每个颜色通道来控制不同的东西。但是要确保颜色大于0，因为我们希望能够在不依赖alpha通道的情况下将其与背景区分开来。

注意，我现在已经从原来的diffuse纹理中删除了线条，所以我们回到了普通的紧身衣:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995020-f2d1f4ce-e7ba-4391-a2c1-6ad4f8f2a7f4.png" width="400"/>
</p>

6. 接下来，我们在mod的` .ini `中的` BodyOverride `中添加了一个部分，将新纹理传递给着色器:

```
[TextureOverrideRaidenShogunBody]
hash = 428c56cd
match_first_index = 17769
ib = ResourceRaidenShogunBodyIBZipped
ps-t0 = ResourceRaidenShogunBodyDiffuseRed
ps-t1 = ResourceRaidenShogunBodyLightMap
ps-t26 = ResourceRaidenShogunBodyControl

[ResourceRaidenShogunBodyControl]
filename = RaidenShogunBodyControl.dds
```

我选择将它加载到插槽26 -我不建议低于20，因为我见过一些情况下，它们会达到这么高(绝大多数的东西使用<10，很少有高于5的东西是重要的)。

7. 我们还需要在着色器顶部附近添加变量:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995132-b3a2b48c-e562-4ae8-af43-157ccc0e87b6.png" width="400"/>
</p>

现在我们可以用类似于加载其他纹理的方式加载这个纹理:

`r2.xyzw = t26.SampleBias(s0_s, v2.xy, r0.x).xyzw;`

(如果你想知道我们是如何得到这一行的，它是通过观察` t0 `和` t1 `纹理是如何加载的，并模仿格式。我选择了` r2 `，因为我知道它将被我们从diffuse加载的任何东西所取代，所以它最终不会破坏任何其他代码行-另一种选择是创建一个额外的寄存器变量)。

8. 现在，我们可以添加一个条件，只触发控件纹理中红色通道值大于0的像素。当我们看到这个时，我们将像素颜色设置为绿色;否则，我们只是从原始的diffuse纹理中加载像素值:

```
  r2.xyzw = t26.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  if (r2.x > 0){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```
(注意:我有点懒于在这里设置值，因为它们应该是标准化的，但这不会有太大的区别)。

这让我们回到了最初的起点:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995286-4e89fdea-a027-4c25-bdcb-15807d890ee5.png" width="600"/>
</p>

但是，现在有一个关键的区别-线的颜色和位置是完全控制通过控制纹理和着色器计算，而不是从原始纹理读取。

这让我们可以通过改变 `r2.xyz = float3(R,G,B)` 的值来轻松地改变颜色。;

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995384-8e650f7b-697f-495f-b058-186d67083141.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995416-ee01bbe2-ded5-4aaa-9f85-8fe2d87a1846.png" width="600"/>
</p>

或者甚至像我们在上一节中所做的那样，将它们设置在`.ini`中。我们甚至可以用这个让它们在颜色之间循环！

9. 现在，线条是通过着色器和控制纹理控制的，我们有更多的灵活性，我们可以做什么。让我们从动画开始。我将使用从黑到白的渐变，而不是在所有的控制纹理线上使用常量黑色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995487-2705e187-b9c7-4d7a-8885-e09c690db396.png" width="400"/>
</p>

现在，`r2.x`的值将从0线性增加到1（这就是为什么我们将其保存为`BC7 线性`的原因，否则，值会出现偏差，从而导致问题）。然后，我们可以将时间变量从`.ini`传递到着色器中:

```
[TextureOverrideRaidenShogunBody]
hash = 428c56cd
match_first_index = 17769
ib = ResourceRaidenShogunBodyIBZipped
ps-t0 = ResourceRaidenShogunBodyDiffuseRed
ps-t1 = ResourceRaidenShogunBodyLightMap
ps-t26 = ResourceRaidenShogunBodyControl
x180 = time
```

在着色器中定义一个新变量:

`#define TIME IniParams[180].x`

现在，我们可以将`r2.x`的值与`TIME`进行比较，以确定我们要绘制模型的哪个部分`r2.x`在0到1的范围内，因此我们需要将`TIME`也移到这个范围内–我们可以使用模运算符将`TIME`划分为重复的桶，然后除以最大值，将其置于0到1范围内。因此，方程式将为`TIME%2/2`，使其每两秒在0和1之间循环。

```
if (r2.x > TIME%2/2){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

结果:

https://user-images.githubusercontent.com/107697535/212007218-4d9aea37-e98a-4a6c-8098-f5e9bcb2bada.mp4

或者，我们可以用 `1- TIME%2/2` 来改变方向:

```
  if (r2.x > 1-TIME%2/2){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

https://user-images.githubusercontent.com/107697535/212006027-a20bf56e-7b36-43f9-bfd3-91e0e286e863.mp4

10. 这样做的结果还不错，但这不是我想要的——我不喜欢线条逐渐出现/消失的方式，我希望线条在身体上移动的时候有一个更`矩阵`的效果。

我们可以定义线条出现的范围，而不是使用单个条件。这将只允许与 `TIME%2/2`最多相差0.2的值:

```
  r2.xyzw = t26.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  if (r2.x > TIME%2/2 && r2.x < TIME%2/2+0.2){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

https://user-images.githubusercontent.com/107697535/212007252-4550a581-3ef7-48ed-865c-f3c516361224.mp4

好多了，但是速度有点快。此外，线条仍然在循环开始时同时出现，使得开始点和停止点很明显。我最终确定的方程是:

```
  if (r2.x > 0 && (TIME % 3)/2.5 > r2.x && (TIME % 3)/2.5-0.2 < r2.x){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

https://user-images.githubusercontent.com/107697535/212007300-9ef429fc-14ae-4057-8c35-90ebc53476e8.mp4

这个循环每3秒一次，我们实际上把时间放在0到1.2的范围内，而不是0到1，除以2.5而不是3——额外的0.2边让线条在循环结束时逐渐出现和消失。

11. 现在，让我们添加一些更酷的效果。我们只是使用一个不变的颜色绿色，但我们不需要-我们可以用数学让颜色循环。解释这是如何工作的超出了本教程的范围，但基本上我们是使用不同步的正弦波在色轮周围传播。更多详情，请看这里:https://krazydad.com/tutorials/makecolors.php

```
if (r2.x > 0 && (TIME % 3)/2.5 > r2.x && (TIME % 3)/2.5-0.2 < r2.x){
    r2.xyz = float3((sin(TIME)+1)/2, (sin(TIME+2)+1)/2, (sin(TIME+4)+1)/2);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

https://user-images.githubusercontent.com/107697535/212008474-dd57332e-6b00-4fef-9d95-b9b585dd37e5.mp4

12. 在这一点上，我已经基本完成了如何创建效果的解释。实际上 cyber bodysuit raiden mod 也有一些额外的切换，以打开和关闭的效果，以限制它们，而雷电是在屏幕上，让用户选择自定义的颜色，但所有这些已经在前面的章节涵盖。

我要提示的唯一一点是，你不仅限于使用这种技术的颜色——你可以使用这种方法在不同的纹理之间进行选择，而不是将`r2`设置为恒定的颜色。你也可以使用控制纹理上的单独通道来获得不同的效果，或者使用不同的变量来切换–可能性是无限的！（不是真的，但你仍然可以做很多！）

13. 虽然我们已经基本完成了，但我将指出一些问题:

- 角色切换后，这些线条不会出现1-2秒。这是因为角色在加载到游戏中几秒钟时实际上使用了不同的着色器-你可以找到这个着色器并替换它来消除这个问题
- 倒影没有线条。这也是因为反射使用了不同的着色器，并且可以通过查找和替换着色器来修复。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996519-bbb1ce32-70dd-4e53-8708-646f50ecc7cf.png" width="200"/>
</p>

- 应用了透明滤镜。虽然这不是一个错误，这意味着有人使用移除透明滤镜mod将有一个覆盖雷电的着色器。如果你想修复这个问题，在shader文件上做一个dif，用一个从删除透明滤镜，看看有什么不同，并将它们应用到你的文件

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996611-a550eddc-a7e1-44a0-8e9f-9246a8fa8411.png" width="600"/>
</p>

- 在使用队伍配置时，有些角色会在雷电出现在屏幕上时破坏。我实际上不知道为什么会发生这种情况-损坏的部分甚至没有使用相同的着色器，我似乎无法孤立这个问题。如果有人知道，请给我留言

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996685-a4c68680-57b7-40c7-8036-ffc0fc5a27e4.png" width="600"/>
</p>

- 彩虹色效果很酷，但在数学上不是100%合理-diffuse纹理使用`SRGB`颜色空间而不是`线性`，这意味着你需要一个额外的步骤来转换颜色(你可以看到线条不会像你期望的那样完全变成红色/绿色/蓝色)。详细信息请参见类似于 https://lettier.github.io/3d-game-shaders-for-beginners/gamma-correction.html 的东西

- 着色器可以在不同版本之间更改哈希值，而且比角色哈希值更常见，所以你可能需要更频繁地更新效果mod而不是角色mod。

如果你已经做到了这一点，恭喜你!你知道如何使用着色器来更改效果甚至生成自定义效果的大部分基本知识。感谢你的阅读，我期待着看到你的创作！

https://user-images.githubusercontent.com/107697535/212008927-9afe13ef-28ff-49b6-804e-847aa039daff.mp4
