## 3DMigoto GIMI 纹理修改教程

本教程将经历修改原神的纹理的过程。

如果你想改变UI元素或横幅（因为许多图标都是使用相同的vb/ib绘制的，这意味着GIMI插件不能用于创建mods），或者只是想改变纹理而不做完整的mod（例如想改变物体或武器的颜色但不想改变形状），这是非常有用的。

本教程将经历纹理修改的两个例子:修改一个祈愿横幅和修改一个风之翼。修改纹理比修改基本的网格稍微难一些，但比导入自定义模型容易得多。

## 前提条件

安装3dmigoto GIMI 开发版本，并设置paint.net或photoshop以打开dds文件（详见[莫娜帽子移除](Guides/CN_MonaWalkthrough.md)）。

我还强烈建议不要在mods中使用mod，也不要在ShaderFixes中使用着色器，因为有时这样会扰乱整个过程。

## 重要提示

默认情况下，当你按下F8时，3dmigoto的开发版本会转储所有的纹理和缓冲，这是由d3dx.ini中的这一行引起的: 

![image](https://user-images.githubusercontent.com/107697535/208988377-e4708ee9-ffed-4d33-a077-698332afae3f.png)


这通常会导致大量（5-10 GB+）的帧转储-我强烈建议这样注释这一行: 

![image](https://user-images.githubusercontent.com/107697535/208988409-3af15c43-b33c-475e-95b4-ae4577320c73.png)

取而代之的是使用[ShaderOverride]部分来指定你在做帧转储时所寻找的内容。 然而，如果空间和时间不是一个问题，或者你无法找到与你正在寻找的对象对应的着色器，取消注释并做一个完整的转储仍然可以工作
## 祈愿横幅

1.  修改纹理的第一步是在游戏中寻找纹理和它的哈希。确保你使用的是开发版本，并在顶部和底部有绿色文本，然后进入祈愿界面:
<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988430-bd1f834b-1aa4-442e-8887-d455308fb6e6.png" width="600"/>
</p>

2.  我们在小键盘上按1和2来循环PS（像素着色器）-我们正在寻找导致横幅纹理消失的着色器。找到它们后，按小键盘上的3来复制哈希

在本例中，我们正在寻找的哈希是:` 000d2ce199e12697 `（它绘制了横幅上的字符，横幅背景，顶部的图标，滚动条和一些文本）
<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988464-cd5d8ebf-bc97-4dbe-a3e4-7cc346b285a1.png" width="600"/>
</p>

以及 ` dcf5ad8be031c5fc `（绘制卡片背景，图标和其余文本）
<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988482-9318495e-d89e-4f88-81b4-44977e44ec98.png" width="600"/>
</p>

这些是原神3.2版本的哈希值——虽然很少见，但有时候着色器哈希值会在不同版本之间发生变化。

3.  一旦我们有了这些哈希，在Mods文件夹的某个地方创建一个Banner.ini文件（可以是任何名称，只要扩展名为.ini），并带有以下文本:

```
[ShaderOverrideBanner1]
hash = 000d2ce199e12697
analyse_options = dump_rt dump_tex dump_cb dump_vb dump_ib buf txt dds

[ShaderOverrideBanner2]
hash = dcf5ad8be031c5fc
analyse_options = dump_rt dump_tex dump_cb dump_vb dump_ib buf txt dds
```

4.  在游戏中按F10重新加载更改。我们刚刚创建的.ini文件将告诉3dmigoto在帧分析期间转储什么文件-如果你无法找到着色器哈希值（例如，因为纹理只在屏幕上显示一秒钟），通过取消d3dx.ini中的行注释来进行完整的转储是一种替代方法。

5.  现在，当仍停留在祈愿界面上时，按F8——这将执行一个帧分析转储，将所有缓冲和纹理转储到3dmigoto文件夹，这个文件夹被命名为FrameAnalysis-YYYY-MM-DD-HHMMSS

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988606-6416661b-8ae6-4e46-9c1c-1a331a7c985e.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988677-94251b3d-8b18-4ca1-8ab3-9618c6f8487e.png" width="600"/>
</p>

如果文件夹是空的，或者只包含log.txt和shaderuse.txt，请确保您已经在正确的位置创建并保存了.ini文件，按下F10重新加载，并在屏幕上显示您正在寻找的纹理。

6.  一旦我们有了文件夹，我们可以通过它寻找我们需要的纹理。你可以在主文件夹中查看按绘制ID排序的文件（文件名开头的6位数字字符串，代表纹理绘制的顺序），或者在包含所有文件但已删除重复的deduped文件夹中查看。

提示:将你的dds编辑软件设置为打开.dds文件的默认应用程序会很有帮助，因为它可以让你在Windows资源管理器中看到预览。

7.  经过一些搜索，我们可以找到我们正在寻找的纹理: 

卡片背景（文件名为 `000059-ps-t0=93073271-vs=8236b1752acd9b01-ps=dcf5ad8be031c5fc.dds` 在主文件夹里以及 `93073271-BC7_UNORM. dds` 在 deduped 里 —— 绘制ID可能与您不同）:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988828-9933ff3b-4137-4dc7-afb3-5e8821790be3.png" width="600"/>
</p>

纳西妲（`000067-ps-t0=70a940c8-vs=28a248a16fa16289-ps=000d2ce199e12697.dds`, `70a940c8-BC7_UNORM.dds`）:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208988902-3456044f-243c-43fc-a70d-307189a8cd42.png" width="600"/>
</p>

侧面人物（`000069-ps-t0=ad520043-vs=28a248a16fa16289-ps=000d2ce199e12697.dds`, `ad520043-BC7_UNORM.dds`）

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989027-5ac89c6b-e786-4e30-9f62-9d1962477a4c.png" width="300"/>
</p>

提示:o0文件显示了正在绘制的ID，因此您可以使用它们来缩小搜索范围 

还有一些其他相关的纹理，但现在我们将专注于这三个。还要注意，使用3dmigoto更改文本非常困难，除非该文本是图标（在本例中并非如此）。

8.  现在我们有了纹理，我们可以从它们的文件名中得到它们的哈希值。 

9.	对于主文件夹中的文件，结构为绘制ID-缓冲类型-哈希-着色器类型-着色器哈希。扩展名-例如，卡片是`000059-ps-t0=93073271-vs=8236b1752acd9b01-ps=dcf5ad8be031c5fc.dds`这意味着它有一个绘制ID`000059`，一个`ps-t0` 缓冲,还有个哈希`93073271`，以及被顶点着色器使用的`8236b1752acd9b01`和像素着色器使用的`dcf5ad8be031c5fc`

对于deduped文件，结构为哈希-文件类型。该卡的名称是`93073271-BC7_UNORM.dds`，它的哈希是`93073271`类型是`BC7_UNORM`.

最重要的信息是哈希和类型，因为这是我们将使用的——所以在本例中，卡片是`93073271`和`BC7_UNORM`，纳西妲是`70a940c8`和`BC7_UNORM`以及四星人物是`ad520043`和`BC7_UNORM`。

10.  在Banner.ini中添加以下代码行: 

```
[TextureOverrideDendroBannerCard]
hash = 93073271
this = ResourceDendroBannerCard

[TextureOverrideBannerNahidaBanner]
hash = 70a940c8
this = ResourceNahidaBanner

[TextureOverrideNahida4StarBanner]
hash = ad520043
this = ResourceNahida4StarBanner

[ResourceDendroBannerCard]
filename = DendroBannerCard.dds

[ResourceNahidaBanner]
filename = NahidaBanner.dds

[ResourceNahida4StarBanner]
filename = Nahida4StarBanner.dds
```

这些行告诉程序要做的是，当它在游戏中看到纹理的哈希时，它会用一个新的纹理替换它（`DendroBannerCard.dds`，`NahidaBanner.dds`，`Nahida4StarBanner.dds`各自替换对应的哈希）。

11.  现在让我们创建这些纹理并将它们添加到Banner.ini所在的文件夹中。注意这3个纹理的类型都是`BC7_UNORM`，对应的是`BC7 Linear`

对于横幅，我将给它重新着色，并将其保存为`DendroBannerCard.dds`（关于如何打开和保存dds文件的详细信息，请参见[莫娜帽子移除](Guides/CN_MonaWalkthrough.md)教程）

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989556-0a5b60a1-1396-4b38-94a9-35eec74bdeea.png" width="600"/>
</p>

对于纳西妲，我将用玉眼猫替换纹理——为了获得正确的大小，我确保与原始的比较（大小为2048x1024，原始的存储是颠倒的）:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989714-21590248-c57b-4ad6-b96d-486c9b9a7e28.png" width="600"/>
</p>

最后，对于四星人物，我将添加信仰（注意这个纹理有一个奇怪的560x512大小）:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989791-4e88703f-df9c-4613-af78-c616c636d5b4.png" width="300"/>
</p>

12.  将这3个文件放入.ini文件夹中，在游戏中按F10，结果如下: 

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989860-3d563399-708c-4976-9f18-cf16cf952904.png" width="600"/>
</p>

成功!第一个纹理mod完成。

（如果按F10后什么都没有发生，确保你把文本放在.ini文件中，新的dds图像与.ini文件在同一个文件夹中，并且屏幕上没有弹出错误消息）

（另一种可能是游戏没有检查特定着色器上的纹理，无论出于什么原因——尝试清空ShaderFixes文件夹，并添加行`checktextureoverride = ps-tx`其中`ps-tx`是纹理的原始缓冲（在例中是`ps-t0`）到ShaderOverride部分强制3dmigoto检查该着色器上的纹理）

## 风之翼

在另一个演示中，让我们替换风之翼的纹理。与UI元素不同，风之翼实际上有一个模型（尽管它看起来像一个平整的矩形），所以我们可以使用GIMI工具来制作mod，但每个风之翼都共享相同的网格。如果我们只想修改一个风之翼，我们需要更精确地确定我们到底要替换什么。

1.  与前面类似，找到绘制翅膀的PS哈希。 我们可以在空中滑行时暂停，然后像之前一样在小键盘上循环1/2

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208989996-ee0dc0bc-dde2-473d-b1da-ea09f5c7e026.png" width="600"/>
</p>

在这种情况下，哈希值是`f8143fa00dc241fe`（注意，还有其他着色器会导致翅膀与环境块一起消失，但我们想要寻找对翅膀最独特的着色器）:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208990044-a43aa6e3-6f96-4fbc-b2b8-b3df0a08d9bc.png" width="600"/>
</p>

2.  我们在Mod文件夹中放入一个ini文件（例如wings.ini）: 

```
[ShaderOverrideGlider]
hash = f8143fa00dc241fe
analyse_options = dump_rt dump_tex dump_cb dump_vb dump_ib buf txt dds
```

3.  然后按F10重新加载，再按F8进行帧转储。

4.  在文件中搜索，我们可以找到翅膀（`000081-ps-t0=d27db883-vs=7494a6d4010b8dec-ps=f8143fa00dc241fe.dd`或`d27db883-BC7_UNORM_SRGB.dds`）。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208990131-64b4dcc4-f29e-4664-a1a3-22259950bd12.png" width="400"/>
</p>

5.  并将它们替换为其他内容（注意:我们可以从文件名中看到，类型现在是`BC7_UNORM_SRGB`，这意味着这些存储为BC7 SRGB，而不是线性）。 

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208990242-7ebdb294-3ba2-43bd-b1a3-3c4a0c8f0882.png" width="400"/>
</p>

6.  我们像这样在.ini文件中创建纹理和覆盖资源: 

```
[ShaderOverrideGlider]
hash = f8143fa00dc241fe
analyse_options = dump_rt dump_tex dump_cb dump_vb dump_ib buf txt dds

[TextureOverrideFirstFlight]
hash = d27db883
this = ResourceFirstFlight

[ResourceFirstFlight]
filename = WingsOfFirstFlight.dds
```

7.  在游戏中按F10重新加载:

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208990331-8ee8125d-0dcb-4a46-87eb-fd3b9c4acfaa.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/208990373-9c143e72-06c6-4592-93f6-13322a6df22e.png" width="600"/>
</p>
