## 3DMigoto GIMI 效果与着色器教程

本教程将介绍改变原神的效果的过程，如技能效果，灯光效果，以及任何未通过纹理或缓冲区控制的游戏内对象。学习着色器如何工作将显著增加你能够mod的范围。

这个效果修改教程比我之前的基本网格编辑/导入和纹理编辑更难，但阅读这些并不是理解本教程的先决条件。

我粗略地按照难度增加的顺序安排了本教程，所以即使阅读第一节也足以进行简单的编辑。后面的章节将需要基本的编程知识。

我将列举三个逐渐复杂的例子： 

-	改变角色的攻击/技能颜色(请参见 https://gamebanana.com/mods/409181 关于甘雨的冰攻击重新着色的例子)
-	创建一个随着时间的推移在多种颜色之间切换的效果(请参见 https://gamebanana.com/mods/418434 关于圣诞树改变灯光的颜色的例子)
-	演示如何创建基本效果动画(请参见 https://gamebanana.com/mods/420434 关于Cyber Bodysuit Raiden的动画线条的例子)

## 前提条件

安装3dmigoto GIMI Dev版本(绿色文本需要可见)。

## 重要说明

默认情况下，我禁用了GIMI转储着色器的能力，因为它们可以干扰mods。您可以通过确保d3dx.ini的`marking_actions`行在列表中包含`hlsl`和`asm`来重新启用它们。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211983955-7a13e1a0-542e-435f-ab67-aa5e78031bd7.PNG" width="600"/>
</p>

另外，如果你在尝试本教程中的内容后遇到mods问题，请尝试清空ShaderFixes文件夹-有时转储的着色器会导致某些mods出现故障。

让我们开始吧！

## 改变角色攻击颜色(迪卢克的火焰)

对于第一节，我将演示如何重新着色迪卢克的火焰。这章节是基本/中级难度，不需要任何先前的编码/着色器知识。

1.	首先，我建议你去一个屏幕上的物体尽可能少，但你想要的效果仍然会显示的地方。你很快就会看到原因，但屏幕上的对象越多，我们寻找着色器的时间就越长。起始海滩区域总是一个不错的选择

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211985874-1e3a43e6-bb5e-48e1-9b8c-c99a199595a0.png" width="600"/>
</p>

2.一旦你找到了一个好的位置，触发你想要的效果并进入暂停菜单。在这种情况下，我们对迪卢克技能的火焰效果感兴趣，所以我们按下e然后暂停（注意：对于只有在游戏未暂停时才显示的效果，仍然有可能获得稍微困难一点的效果——我稍后会解释）

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

5.	在数字键盘上按' 3 '将PS哈希值复制到剪贴板，并将着色器保存到ShaderFixes文件夹中。上面两个着色器的哈希值是' e75b3ffb93a1d268 '和' dd0757868249aaa5 '(注意:如果你需要快速回到起点，你可以按数字键盘上的 ' + '将缓冲区重置为0)。注意，着色器哈希值可以在不同版本之间改变，所以你的哈希值可能不相同

6.	着色器现在应该显示在ShaderFixes中，名称类似' hash-ps_replace.txt '。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986246-48a6ccdb-e779-4e13-8b1e-ce02bcb1b044.png" width="400"/>
</p>

如果它们在numpad上按下“3”后没有显示，请确保您将“hlsl”和“asm”放在“marking_actions”中，正如顶部的重要说明中提到的那样，并使用“F10”刷新。

还要注意的是，少数着色器不会正确地反编译为' hlsl '(高级着色器语言)，而是会恢复为' asm '(汇编)。这些着色器仍然可以工作，但编辑起来会更加笨拙。我不会在本教程中介绍asm，但概念是相同的-着色器的语法只是更难阅读。

7.	用你选择的文本编辑器(Notepad/ notepad++ /Sublime text /随便什么)打开它们。这个文件一开始看起来很吓人，但是不要担心——您不需要了解细节就可以进行基本的更改(我将在后面的章节中详细介绍这个文件的工作方式)。
	
<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986377-e2fd3418-f673-4cf8-9ff1-938faf945c76.png" width="400"/>
</p>

8.	现在，我们最感兴趣的是处理输入和输出。这些都列在main下面——这个文件有9个输入(编号为' v0 '， ' v1 '， ' v2 '，…' v8 ')，有一个输出(' o0 ')。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986455-0a5ca895-c3a7-4066-a59f-be71fe2634e6.png" width="300"/>
</p>

9.	通常从输出开始是最简单的。它有一个' float4 '类型，这意味着它有一个' x '， ' y '， ' z '和' w '组件，并接受一个浮点数(即十进制)作为输入。我们可以通过在代码末尾放一行来强制将值设置为常量，来看看它是怎么做的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986560-b25728ae-e24a-4fe1-929e-0d49bf02dadf.png" width="300"/>
</p>

（`//`和`/**/`表示代码中的注释，并被程序忽略。3dmigoto还将`asm`代码导出到`hlsl`代码下面——当我说“end”时，我的意思是“return”之前，而不是之后。该点之后的所有内容都被注释掉，默认情况下不会运行。如果您看到像`div`、`mul`和`mov`这样的内容，您跑得太远了）

基本上，我们所做的就是覆盖游戏计算的值，并将其替换为我们自己的值

10.	保存文件，然后在游戏中按“F10”重新加载(确保也按“+”重置缓冲区!)3dmigoto会自动从ShaderFixes文件夹中加载着色器。这就是所发生的:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986773-ee66b8c6-2d80-44fc-b1cf-fa8e41f4f9db.png" width="600"/>
</p>

中线变成了黑色，火花变成了绿色。如果你熟悉颜色是如何储存的，你可能会猜到' o0.X '表示，但我们可以继续检查以确保:

将' x '和' z '组件设置为0，' y '设置为1:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986865-67fb5c91-3c25-4df7-8821-c5b11c3531fa.png" width="300"/>
</p>

设置所有内容为绿色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986940-01ebfc18-ef72-4c60-b7e2-91985bf9c2b1.png" width="600"/>
</p>

同时将“x”和“y”设置为0，“z”设置为1

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211986994-c3070f3f-9eb5-480a-b8ed-13ab90076c80.png" width="300"/>
</p>

设置颜色为蓝色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987033-f9a1b299-9676-4687-9ae9-808db2b84b3d.png" width="600"/>
</p>

或者换句话说' o0.xyz '对应效果的RGB颜色。并不总是“o0”是颜色——一些着色器有多个输出，所以颜色可能是“o1”或“o2”等;值得庆幸的是，这个着色器相当简单，只有一个输出“o0”。

(如果你想知道“w”代表什么，它似乎与效果的宽度/放射有关:)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987161-edd09e67-99e8-42ff-9653-9aafadda4531.png" width="600"/>
</p>


11.	现在我们知道了这些值对应的是什么，我们可以对颜色进行基本的更改。例如，设置三个' o0.xyz '到0会导致迪卢克的火焰变成黑色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987214-bc9c7a29-1bf0-483d-bb9d-7cba39afd1da.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987253-b4480e4e-b3f3-4726-b66d-cb8e5c698815.png" width="600"/>
</p>

或者我们可以把它们变成紫色，把' r '和' b '设为1，把' g '设为0:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987317-f0237be8-da62-43d1-8d0f-7f6447872f09.png" width="600"/>
</p>

注意，我们也不局限于设置常量-我们也可以改变颜色的色调。这减少了攻击中的红色数量，同时增加了更多的绿色和蓝色，以创造一个鲑鱼粉色的颜色:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987374-be4661b0-46aa-4829-82c0-2274175a8b6e.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987415-bf5057ee-1c20-4e19-8195-0c3ace4fd26f.png" width="600"/>
</p>

注意，与我们强制设置恒定值的情况不同，火焰纹理在这里仍然可见。

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

`7690cf4aa6647c6c` 是元素爆发期间的剑辉：

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

然而，对于只在过场动画中出现或难以重现的效果，最快的方法是进行帧转储。关于如何执行帧转储的更多细节，请参阅纹理修改教程，但本质上，当效果在屏幕上显示时，您按“F8”来执行转储，同时效果是可见的。

不幸的是，由于我们不知道着色器哈希，它将需要一个完整的转储，所以确保你有5-10GB的空闲空间和屏幕上尽可能少的对象。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211987810-78fc6d7f-1f98-4474-8e59-86d155378fda.png" width="300"/>
</p>

当你有了按下“F8”后创建的框架分析文件夹时，你可以通过它来查看效果何时绘制。“o0”和“o1”文件显示了每个ID所绘制的内容，对于隔离在屏幕上绘制效果的确切ID非常有用。

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

14.	现在我们有了剩下的哈希值，我们需要转储它们。按numpad ' + '重置缓冲区，施放ult，然后开始使用numpad ' 1 ' / ' 2 '循环，而效果在屏幕上。即使在我们到达哈希时，效果已经离开了屏幕，只要我们在效果出现在屏幕上时开始循环，它就会显示在列表中，并且可以转储:

PS ' 4d4da8a4cbe1149a '即使ult没有激活显示的例子:

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

16.	我们想要一种方法来限制效果，只有当迪卢克在场上时才会出现。我们有几种方法可以做到这一点，但它们都遵循相同的基本原则-我们确定了当Diluc在场上时引起的某些条件，然后仅在该条件为真时应用这些效果。

这是一个更高级的主题，在你玩了更多的着色器和阅读后面的部分后会更有意义-如果你有理解这个问题，试着阅读下面的部分，然后再回来。

首先，我们需要确定迪卢克唯一的哈希值。为了简单起见，我将使用迪卢克的`VB` 哈希 `56159d74` (' VB '可以与numpad ' / '和' * '循环，并使用numpad ' - '复制):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211988418-a6af34f5-b9dc-4446-aa84-44ddf93a435c.png" width="600"/>
</p>

17.	接下来，我们构建一个' .ini '，我们将使用它来选择性地应用效果。我们定义了一个名为“$ActiveCharacter”的变量，并在每一帧开始时将其设置为0 (' [Present] '在每一帧开始时运行一次)。当迪卢克在场上时时，我们只将值设置为1，由匹配的VB散列表示:

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
这里的`match_priority`只是为了确保这个效果不会干扰任何加载的迪卢克mod -如果你将这个效果作为一个mod的一部分而不是单独添加，你不需要包括它。

18.	现在，我们有两种方法来隔离着色器。两种方法中比较简单的是简单地定义一个自定义着色器并执行替换，然后创建一个`shaderoverride`，并且只在迪卢克是活动角色时运行自定义着色器:

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

这通常会工作，但3dmigoto有时不能正确编译' hlsl '如果这样做会导致错误。同样，它也不会对' asm '起作用。但优点是，着色器可以捆绑在mod文件夹与mod的其余部分，它不会影响如果另一个mod试图修改相同的着色器。

另一种方法是传递一个自定义变量给着色器，只有当变量匹配时才执行效果。下一节将更详细地讨论这一点，但本质上你想为每个着色器创建一个这样的部分:

```
[ShaderOverrideDilucFlame]
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

在本节中，我将演示如何从“.ini”文件加载自定义值到着色器，以及如何使用它来制作多种颜色之间循环的效果。我还将演示如何找到着色器中控制放射的部分，这比仅仅是效果颜色更具挑战性。

本节属于中等难度，我假设你已经阅读了前一节的大部分内容，并且至少对“.ini”文件和着色器有一些基本的熟悉(例如，知道如何打开它们，至少模糊地理解不同的部分)。有基本的编程知识。

1. 像以前一样，我们从收集着色器哈希开始，这次是中立的柱子:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990319-6809dcff-aa24-46de-8d50-56e21511f384.png" width="600"/>
</p>

与Diluc不同，这个散列不会导致整个柱子消失——只会导致纹理消失。这是因为它是使用多个着色器绘制的，所以即使我们跳过对象的一部分，仍然会绘制(在这种情况下，柱子的轮廓仍然保留)。

本例中的哈希值是 `4c99fec14dca7797` – 按' 3 '将着色器转储到ShaderFixes。

我们的最终目标是改变黄色裂隙效果的颜色，而其他部分保持不变。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990446-34c57fcf-fb0a-495a-adf0-4c3834236f0f.png" width="200"/>
</p>

2. 打开着色器，我们可以看到它比以前的9个输入和6个输出更复杂。这是因为着色器负责做很多事情，比如绘制纹理，处理放射，计算阴影等。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990505-a83e9b5d-e53f-4d81-8bf1-4b88224c4b3f.png" width="300"/>
</p>

我们首先尝试与前面相同的方法——将每个输出设置为常量，以了解它们控制的内容。

3.' o0 '似乎与轮廓有关，使它们变得更厚和更薄(有点难以看到，但可以使用' F9 '在修改模式和无修改模式之间来回切换):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211990621-0a6ae9bb-00d8-4da2-b533-bc49e373b2d4.png" width="200"/>
</p>

`o1.xyz` 似乎和之前一样对应颜色RGB，而' w '似乎控制亮度

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

但是，您可能已经注意到一个问题——所有这些选项都会改变整个柱子的颜色，而不仅仅是黄色地理线!我们必须再深入挖掘一下，以找出这是如何处理的。

4. 在我们继续之前，让我更详细地解释着色器中最重要的符号:

- `v0`,`v1`,`v2`..etc. 是vb文件中加载的输入数据，也就是说，与顶点位置、顶点颜色(与纹理颜色不同!)、uv贴图、混合权重等相关的数据。
- `o0`, `o1`, `o2`… 是输出目标，是实际绘制到屏幕上的东西(或者在顶点着色器' VS '的情况下，传递给像素着色器' PS '的东西)
- `t0`, `t1`, `t2`… 是纹理-典型的像DDS纹理，尽管它们在某些情况下也可以是缓冲区。当你在.ini文件中看到' ps-t0 '， ' vs-t0 '， ' ps-t1 '， ' vs-t1 '等时，这就是它们对应的
- `r0`, `r1`, `r2`… 寄存器——这些是着色器用来存储计算结果的临时变量
- `cb0`, `cb1`, `cb2`… 常量缓冲区-这些是游戏传递给着色器的值，代表当前游戏状态的值，如对象的全局位置或自游戏开始以来传递的时间

考虑到这一点，我们可以专注于我们感兴趣的代码部分，而不是试图理解所有200多行代码。

我们感兴趣的是中立柱子的光芒。查看柱子的纹理，我们可以看到diffuse纹理包含alpha层之上的发光部分，并加载在插槽0(第一个哈希来自柱子的哈希.json)。或者通过查看创建的mod，看到diffuse加载为' ps-t0 '):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991323-68087da3-c621-4238-a994-50e3859837a5.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991357-5a0c0cee-eb64-410c-875f-db1576e107b9.png" width="300"/>
</p>

因此，我们感兴趣的是代码中涉及到变量' t0 '的任何部分，这对应于diffuse纹理。具体来说，我们最感兴趣的是任何涉及w分量的东西，因为它代表发光部分。

5. ' t0 '在着色器中被加载了两次:一次是在第100行左右的变量' r2 '中:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991507-ed958308-a38f-40dc-a056-5d663f389052.png" width="400"/>
</p>

还有一次在第235行左右，输入变量' r0 ':

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991578-04bb9823-8bb5-4523-a0f5-2b81e4f32502.png" width="400"/>
</p>

有很多方法可以通过阅读代码来判断哪个是正确的，但尝试每种方法也可以:

设置“r2.X '作为第一个块中的常数:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211991690-68c079f5-5111-4b09-90ae-e7120338b791.png" width="300"/>
</p>

将柱子变成绿色，但保持正常的裂隙效果:

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

https://user-images.githubusercontent.com/107697535/212007147-b94b5eda-ca1d-40ee-938e-25d5e7b1f913.mp4

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


## Animated Effects

In this final section, I will demonstrate how we can use the principles from the previous two sections to create simple animated effects – I will be going through the process of creating the animated lines in cyber bodysuit raiden (https://gamebanana.com/mods/420434). This section is advanced – I will be assuming you understand the previous two sections, know how to make mods, as well as have some basic programming knowledge.

1. To start, we find the shader that controls drawing the textures on Raiden Shogun:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994076-18855a3d-7400-4315-9c86-34320c9c1393.png" width="600"/>
</p>

Raiden actually uses at least two – one for the body object and one for the dress object – but we are interested in the body object since that is the one that has the emission effect we need (found through trial and error previously)

The hash is `7d2763cf91813333`, and we dump it to ShaderFixes.

2. Now, we look for the part of the shader responsible for emission. The emission is above the alpha layer on the diffuse texture which is in slot 0, so we are looking for things related to `t0.w`. There is only one relevant line in the shader:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994193-4a061233-20e7-4817-871d-499d04b209be.png" width="400"/>
</p>

And testing it, we find it is responsible for the glow:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994259-272abaad-7bb2-452a-ab81-b28a3c97c8ed.png" width="200"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994318-7846346e-6614-4dfc-a793-32ac6af1d173.png" width="600"/>
</p>

And we can modify the glowing portions of her texture only by adding a conditional that only triggers on pixels that have an alpha value greater than some arbitrary number:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994369-a97f22ad-3d00-4aa0-846a-a69596874609.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994415-6582a59d-8ac1-464a-a245-b55ea3c4c28b.png" width="600"/>
</p>

3. Now, I am going to demonstrate the process of adding lines to my cyber bodysuit raiden mod:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994483-bf30fc5b-248a-44ea-84b4-6d3bb867b502.png" width="600"/>
</p>

First, I draw the lines:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994549-4268e3f1-0f26-462f-a8c9-598f5295aa3a.png" width="500"/>
</p>

I did this through the Blender texture painting tab, but you could also paint directly on to the texture using paint.net\/photoshop. Note that the final output has to be `BC7 SRGB` `dds` for the diffuse texture. Also, don’t be like me – paint these on a separate layer so you can easily separate them out later ;-;.

4. The final texture looks like this after moving the lines above the alpha layer (note: it is wide because I merged a few models together and put their textures side-by-side):

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994700-5f1401f1-a7cb-4f7a-82bf-057638c2e6d3.png" width="700"/>
</p>

Which gives us glowing lines in-game

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994819-843f583b-91d2-4de3-b4ef-153c6199f540.png" width="600"/>
</p>

5. Now, time to implement some basic animations. I separate out the lines from the diffuse texture into another empty texture which I am going to call the “control” texture:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211994886-0ead61d0-d16d-4029-8e43-376599f51806.png" width="700"/>
</p>

This texture will essentially be what we are going to use to tell the shader which parts of the texture will have animated effects (since all four channels of the diffuse/lightmap are already in-use). The type for this texture should be `BC7 Linear`, since we want the color values to be evenly spaced. 

I have also recolored it to black for simplicity – we won’t be using specific colors in this example to keep things simpler, so we set all the color channels equal; if you wanted, you could use each color channel to control different things. Make sure the color is greater than 0 though, since we want to be able to differentiate it from the background without relying on the alpha channel.

Note that I have removed the lines from the original diffuse texture now, so we are back to vanilla bodysuit:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995020-f2d1f4ce-e7ba-4391-a2c1-6ad4f8f2a7f4.png" width="400"/>
</p>

6. Next, we add a section into the `BodyOverride` in the `.ini` of the mod to pass the new texture to the shader:

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

I chose to load it into slot 26 arbitrarily – I don’t recommend going lower than 20, since I’ve seen a few cases where they go up that high (vast majority of things use <10, and it’s rare that anything above 5 is important).

7. We also need to add the variable in to the shader near the top:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995132-b3a2b48c-e562-4ae8-af43-157ccc0e87b6.png" width="400"/>
</p>

We can now load this texture in a similar way to how we load the other textures:

`r2.xyzw = t26.SampleBias(s0_s, v2.xy, r0.x).xyzw;`

(If you are wondering how we got this line, it was from looking at how the `t0` and `t1` textures are loaded in and mimicking the format. I chose `r2` since I know it will be replaced by whatever we load in from the diffuse, so it won’t end up breaking any other lines of code – another option would be to create an additional register variable).

8. Now, we can add a conditional that only triggers on pixels of the control texture that have a red channel value greater than 0. When we see that, we set the pixel color to green; otherwise, we simply load the pixel value from the original diffuse texture:

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
(Note: I’m being a bit lazy setting the values here since they should be normalized but it won’t make too much of a difference).

Which leads us back to our original starting point:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995286-4e89fdea-a027-4c25-bdcb-15807d890ee5.png" width="600"/>
</p>

However, there is now one key difference – the line colors and locations are being fully controlled through the control texture and shader calculations, and not being read from the original texture.

This lets us easily change the color just by changing the value of `r2.xyz = float3(R,G,B)`;

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995384-8e650f7b-697f-495f-b058-186d67083141.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995416-ee01bbe2-ded5-4aaa-9f85-8fe2d87a1846.png" width="600"/>
</p>

Or even set them in the `.ini` like we did in the previous section. We can even make them cycle between colors using this as well!

9. Now that the lines are being controlled through the shader and control texture, we have a lot more flexibility in what we can do. Let’s start by animating them. Instead of using a constant black across all the control texture lines, I am going to use a gradient from black to white:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211995487-2705e187-b9c7-4d7a-8885-e09c690db396.png" width="400"/>
</p>

Now, the value of `r2.x` will linearly increase from 0 to 1 as you travel down the lines (this is why we saved as `BC7 linear` – otherwise, the values would be skewed leading to issues). We can then pass the time variable from the `.ini` into the shader:

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

Define a new variable in the shader:

`#define TIME IniParams[180].x`

Now, we can compare the value of `r2.x` to `TIME` to figure out what part of the model we want to draw. `r2.x` is in the range 0 to 1, so we need to shift the `TIME` into this range as well – we can divide `TIME` into repeating buckets using the modulo operator, then divide by the max value to put into the range 0 to 1. So the equation would be `TIME%2/2` to have it cycle between 0 and 1 every two seconds.

```
if (r2.x > TIME%2/2){
    r2.xyz = float3(0,1,0);
    r2.w = 0.6;
  }
  else{
    r2.xyzw = t0.SampleBias(s0_s, v2.xy, r0.x).xyzw;
  }
```

Result:

https://user-images.githubusercontent.com/107697535/212007218-4d9aea37-e98a-4a6c-8098-f5e9bcb2bada.mp4

Alternatively, to change the direction we can use `1- TIME%2/2` instead:

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

10. The result of this isn’t bad, but it isn’t quite what I was looking for – I don’t like how the lines gradually appear/disappear, and I was hoping for a more “matrix-like” effect where the line travels along the body.

Instead of using a single condition, we can define a range where the lines will appear. This will only allow values that are at most 0.2 away of `TIME%2/2`:

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

Much better, but it moves a bit fast. Also, the lines still appear all at once at the start of the cycle, making the starting and stopping points obvious. The final equation I settled on was:

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

This loops every 3 seconds, and we actually put the time into the range 0 to 1.2 instead of 0 to 1 by dividing by 2.5 instead of 3 – the extra 0.2 side lets the lines gradually appear and disappear at the end of the cycle.

11. Now, lets add some more cool effects. We are just using a constant color green, but we don’t have to – we can use math to make the colors cycle. Explaining how this works is beyond the scope of this tutorial, but basically we are using out of sync sine waves to travel around the color wheel. For more details, look here: https://krazydad.com/tutorials/makecolors.php

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

12. At this point, I have mostly finished explaining how to create the effect. The actual cyber Raiden mod also has some additional toggles to turn the effects on and off, to limit them to while Raiden is on-screen and to let the user choose custom colors but all of those have already been covered in previous sections.

The only additional thing I would note is that you aren’t just limited to using colors with this technique – instead of setting `r2` to be a constant color, you could instead use this to pick and choose between different textures. You can also use the separate channels on the control texture for different effects, or use different variables for toggles – the possibilities are limitless! (not really, but you can still do a lot!)

13. While we are mostly done, I will point out some issues:

- The lines don’t appear for ~1-2 seconds after character swap. This is because characters actually use a different shader when they are loading into the game for a few seconds – you can hunt down this shader and replace it as well to remove this issue
- Reflections don’t have the lines. This is also because the reflections use a different shader, and can be fixed by also hunting down and replacing the shader.

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996519-bbb1ce32-70dd-4e53-8708-646f50ecc7cf.png" width="200"/>
</p>

- The transparency filter is applied. While this isn’t an error, it means that someone using the remove transparency filter mod will have that one overwritten for Raiden. If you want to fix this, do a dif on the shader file with the one from remove transparency filter to see what the differences are and apply them to your file

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996611-a550eddc-a7e1-44a0-8e9f-9246a8fa8411.png" width="600"/>
</p>

- Some characters break while Raiden is on screen for a moment when using the party menu. I don’t actually know why this happens – the part that breaks doesn’t even use the same shader and I couldn’t seem to isolate the issue. If anyone knows, please send me a message

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/211996685-a4c68680-57b7-40c7-8036-ffc0fc5a27e4.png" width="600"/>
</p>

- The rainbow color effect is cool but isn’t 100% mathematically sound – the diffuse texture uses an `SRGB` color space not a `linear` one, which means you would need an additional step to convert the colors (you can see that the lines don’t ever turn fully red/green/blue as you would expect). See something like https://lettier.github.io/3d-game-shaders-for-beginners/gamma-correction.html for details

- Shaders can change hashes between versions, and tend to do so more commonly than character hashes so you may need to update effect mods more often than character ones.

If you have reached this point, congratulations! You know the majority of the basics of how shaders can be used to change effects or even make custom ones. Thank you for reading, and I look forward to seeing what you create!

https://user-images.githubusercontent.com/107697535/212008927-9afe13ef-28ff-49b6-804e-847aa039daff.mp4
