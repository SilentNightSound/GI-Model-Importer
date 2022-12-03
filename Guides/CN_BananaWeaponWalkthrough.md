## 自定义武器修改指南

这是一个将自定义武器模型导入原神的操作指南。

对于本教程，我假设你熟悉使用 GIMI 的基础知识（如何设置/导入/导出/加载）；如果没有，请阅读[移除莫娜帽子](CN_MonaWalkthrough.md)。我还假设你有 Blender 的基本知识 - 对于 Blender 的基本知识问题，如如何改变模式、选择顶点和打开某些菜单，请在 Google/Youtube 上搜索你需要的知识。

武器修改比基本的网格编辑要复杂，但比导入自定义角色要简单。对于自定义角色来说，大约 90%的步骤是相同的，但角色涉及的顶点组/骨骼结构比武器复杂得多。

我将演示三种不同的武器模型，按复杂程度排序。一般来说，武器的难度从最简单到最难的顺序是：没有流苏的单手剑/长柄/双手剑 → 有流苏的单手剑/长柄/双手剑 → 弓 → 法器。每种武器的复杂程度都建立在上一种武器之上，所以请按顺序阅读。

我会在全部 3 个 mods 中使用[这个](https://sketchfab.com/3d-models/banana-6d99c6c1a8bc4b3e97cebbc49d62115d) 香蕉模型（作者是 Marc Ed）

第一个模型: 香蕉大剑 ([jump to section](#banana-blade))  
Second model: Bownana ([jump to section](#the-bownana))  
Third model: Ripe Catalyst ([jump to section](#ripe-catalyst))

## 香蕉大剑

让我们从最简单的武器类型之一开始， 一个没有流苏的双手剑 - 我将用一个巨大的香蕉来代替螭骨剑

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231401-711a0bd9-b89a-4a54-aa55-9f35c12ac966.png" width="800"/>
</p>

1. 首先从 GI-Model-Importer-Asset 存储库中导入螭骨剑的 3dmigoto 数据

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231676-a73470a7-0cc4-4977-a17a-0ba1165485a8.png" width="600"/>
</p>

2. 检查确保我们是在最简单的武器类别中，检查武器没有任何顶点组。如果有，你可以继续跟着做，但你需要参考下面两节关于如何处理组的内容

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231678-1cd4d30b-274a-4a13-8deb-8da7b7ca5cf4.png" width="600"/>
</p>

3. 使用 File→Import→FBX 导入香蕉。我选择了一个简单的模型，只有一个纹理和组件，目的是演示这个过程是如何进行的 - 更复杂的模型可能需要你将多个纹理和组件合并在一起，这需要更高级的 Blender 知识。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231693-6007de52-ecdb-4fb7-8301-07af38e1f336.png" width="400"/> <img src="https://user-images.githubusercontent.com/107697535/183231698-8e0ab1e3-e07e-4fd3-bdc8-c31d8b2c1b05.png" width="400"/>
</p>

4. 正如你所看到的，香蕉模型和剑的模型在位置和大小上都是错位的。平移、旋转和缩放香蕉，直到两个模型重合。需要考虑的最重要的部分是剑柄（因为那是人物将持有武器的地方），并确保新武器不比旧武器明显大/小（因为你有可能最终出现碰撞或与实际命中偏移）。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231783-eb1f397a-c017-4398-950f-15a9d8dc66c9.png" width="600"/>
</p>

5. 虽然这样会起作用，但我们希望模型能多重叠一点，这样它实际上与剑的运动更接近 - 我们可以打开比例编辑，拖动和旋转香蕉的尖端，使它更直以改善结果。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231793-4f6c5365-8b45-4cb8-9543-8256a1440b25.png" width="600"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231811-c4b37248-dae3-42e2-9865-6554e41931da.png" width="410"/><img src="https://user-images.githubusercontent.com/107697535/183231814-55c7de2d-1d01-46c2-9da1-0deb9e5b108f.png" width="400"/>
</p>

请注意，对于这些类型的武器，新对象不需要与旧对象完全重叠。

6. 现在，我们需要将自定义的 3dmigoto 属性添加到新对象上。有两种方法可以做到这一点 - 你可以删除旧模型的所有顶点，然后将新模型合并到其中，或者你可以使用[自定义属性转移脚本](/Tools/blender_custom_property_transfer_script.txt)。我将在本教程中使用后一种方法

7. 打开脚本标签，把转移脚本复制到文本框中。首先点击你要转移属性的对象，然后 CTRL+点击你要转移属性的对象。点击顶栏上的播放按钮/三角形来运行脚本（旧方法：去掉 ORIGINAL USAGE 部分，然后将“transfer_to”和“transfer_from”分别替换为你要转移到的对象（新对象）和来自的对象（原 3dmigoto 对象）

8. 仔细检查新对象的 "自定义属性 "部分所显示的属性

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231907-d9c8dd16-f9b5-4806-8671-f211f865d783.png" width="400"/>
</p>

9. 现在，我们需要确保新对象的 UV 贴图和颜色数据将被正确导出。使用原始对象作为示范 - 螭骨剑有两个 UV 贴图 TEXCOORD.xy 和 TEXCOORD1.xy，以及一个名为 COLOR 的顶点颜色。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231917-2db88099-f9c9-4967-a8b5-c5fe194cc288.png" width="400"/>
</p>

对于武器来说，第一个 TEXCOORD 是用于贴图：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183231961-15a8ec7c-df73-4c68-ab81-b07a61419718.png" width="800"/>
</p>

而第二个控制武器的出现和消失：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232042-e06c3613-cadc-4026-bba8-11d6eef1635a.png" width="800"/>
</p>

顶点 COLOR 有四个组成部分。每个组件具体控制什么不在本教程的范围内，但简单地说，A 主要用于轮廓厚度，而 RGB 则用于环境遮挡、镜面和金属色。

注意：如果你的模型有多个 UV 贴图和纹理，你需要在继续之前将它们合并成一个。你可以通过将纹理并排排列，然后缩放 UV 贴图使其与每个组件相匹配来实现这一目的。确保最终纹理的宽度和高度是 2 的幂（即 1024x1024、1024x2048 或 2048x2048 等）。

10. 我们使用的香蕉模型只有 1 张 UV 图，我们将其重命名为 TEXCOORD.xy，以便与螭骨剑模型相匹配。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232096-f47f73af-77ad-4a4b-8ee4-d608c81279d1.png" width="800"/>
</p>

11. 对于第二个 TEXCOORD，我们创建一个名为 TEXCOORD1.xy 的新 UV 贴图，按数字键盘上的 7 转到顶视图，选择整个网格，然后按 UV→ 从视图中投影

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232109-8a88e9ac-5f87-42c4-b4ed-ff5c988dbdfe.png" width="800"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232115-ae7d3b9f-c924-4883-afdd-f18cf7618212.png" width="800"/>
</p>

然后我们缩放和旋转香蕉，使其与螭骨剑的 TEXCOORD1 相符。这将导致武器从香蕉的茎部开始进入相位。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232139-6003d62f-5a15-4e1d-834f-03a0acc2f0e5.png" width="800"/>
</p>

(注意：旧版本的插件有一个与 TEXCOORD1 有关的问题，即模型的轮廓消失了。虽然这有几个原因，但最常见的是由于游戏重复使用一个纹理槽，用于褪色和轮廓。尝试删除.ini 文件中的 ps-t2 和 ps-t3 行，看看是否能解决这个问题）。

12. 最后我们处理颜色问题。如果你的模型已经有了顶点颜色，你可以把它们重命名为 COLOR 就行了（不过要注意的是，无论你从哪里得到的模型，都可能没有使用和原神相同的 COLOR 值，所以删除它们并从 3dmigoto 网格转移过来可能更安全）。

这个香蕉模型没有顶点颜色，所以我们首先需要添加一个颜色变量。通过进入数据属性标签并按下 "+"按钮来完成。我们希望名字是 COLOR，区域是 Face Corner，数据类型是 Byte Color。你可以暂时将颜色保留为黑色，我们将在下一步从原始对象中变换它。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232163-f9abc26d-3cb0-4fa7-8ef8-1ff0d89e1de3.png" width="400"/>
</p>

13. 现在我们有了一个 COLOR，我们需要从螭骨剑转换正确的数值。选择香蕉，进入修改器标签，选择添加 modifier→data 的变换

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232193-d04a6d50-4493-431d-8be7-3bd3e243ab3f.png" width="400"/> <img src="https://user-images.githubusercontent.com/107697535/183232201-d2802655-944c-4ceb-b694-25546ff64cc8.png" width="400"/>
</p>

设置源为螭骨剑，检查面角数据框和颜色选项卡，确保选项为所有层和按颜色名称：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232208-bd3a2147-8f59-4050-9518-b3388dfea2f1.png" width="400"/>
</p>

(注意：对于具有多个顶点颜色的更复杂的模型，你可以使用滴管从组件的特定部分复制颜色数据，而不是选择整个对象）。

最后，按向下的箭头并点击应用。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232216-70505fa2-dd30-435a-9468-a1be2e984db0.png" width="400"/>
</p>

你可以通过进入顶点绘制模式并检查颜色是否匹配来仔细检查它是否正常工作：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232222-ec49ff63-d7dc-40d3-bc81-ca9317df2b20.png" width="800"/>
</p>

14. 接下来，我们需要将模型相对于原始模型进行旋转并应用变换。尽管这些模型看起来是重叠的，但原神在绘制屏幕的过程中会旋转它们，所以我们需要在 Blender 中也这样做以抵消这种影响。选择对象，然后相对于原件旋转 90 度，像这样：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232236-4369c7ff-3638-4a97-a1a7-e113702b86fa.png" width="600"/>
</p>

选择该对象并应用所有的变换（重要的是如果你不应用变换，武器将以完全不同的方向和比例出现，而不是你所期望的那样！)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232251-83682dd2-bde9-470e-9081-1b4af92b6dd2.png" width="600"/>
</p>

(注意：方向可能会混淆，所以当对哪个方向正确有疑问时，只需尝试旋转两个方向，看看哪个方向可行)

15. 我们几乎已经完成了! 最后一部分是将名称改为 "SerpentSpineHead"，并从原始对象中删除该文本，以便插件知道要导出哪个对象。一旦你正确地命名了东西，就使用 Export Genshin Mod Folder 导出到 SerpentSpine 数据文件夹（完整步骤见莫娜教程）。

如果你在导出时有任何问题，请参考[GIMI 故障排除指南](/Guides/CN_Troubleshooting.md#模型导出问题)，看看有没有你碰到的问题

16. 在我们开始处理纹理之前，最好先确认你的模型是否正确加载到游戏中。复制 Mod 文件夹并重新加载：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232283-3de96889-ec67-41ea-8595-a0ef20d9c654.png" width="800"/>
</p>

看起来形状和位置都是正确的，所以我们现在要继续修复纹理。

17. 我们从漫反射纹理开始。原神中的漫反射纹理是 BC7 SRGB 类型的.dds，它使用 alpha 层进行散射。原始螭骨剑纹理像这样（左边是阿尔法层上面的部分，右边是下面的部分）。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232304-34589d61-5654-42ed-9dbc-29aab182fbf5.png" width="600"/>
</p>

我们现在要用香蕉纹理替换这个纹理：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/189494245-17f20a5a-3974-498c-8c96-8c5ce66c1100.png" width="500"/>
</p>

对于这一部分，我们不会对香蕉纹理做太过花哨的处理：我们只是反转 alpha 通道，保存为.dds 并替换原来的 SerpentSpineHeadDiffuse.dds（关于原神基本纹理编辑的更多细节，见莫娜教程）。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232314-ca0a08ea-34dd-4902-84c4-ea62268a1997.png" width="600"/>
</p>

注意事项 1: 确保宽度和高度是 2 的幂（1024x1024，2048x2048，1024x2048，等等），否则你可能会遇到问题。

注意事项 2: 并非所有的漫反射纹理都有散射 - 有些根本就没有 alpha 通道。在这些情况下，你不需要反转通道，只需按原样使用该纹理。如果有疑问，请检查原始纹理，看看它看起来像什么，并模仿它。

18. 替换漫反射纹理并重新加载：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232327-74079c8d-9f5a-44e9-bbe7-01b7e3aa250f.png" width="800"/>
</p>

看起来好多了，但我们仍然可以看到一些反射和阴影问题。这些问题是由光照图引起的，我们也需要对它进行编辑。

19. 如果你的模型带有光照图，你可以重复上述操作，并将其保存为 BC7 Linear，然后替换原来的光照图。然而，这个模型并没有附带光照图，所以我们需要创建一个基本的光照图。原来的光照图在阿尔法层的上方和下方看起来是这样的：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232355-06724fe1-619e-44f8-be5d-d39474f61497.png" width="600"/>
</p>

关于光照图究竟是如何工作的细节超出了本教程的范围，将在以后的教程中介绍 - 现在，通过与漫反射纹理的比较，我们可以看到贴图似乎在剑的米色部分的 alpha 层上面使用了紫色，这是与我们的模型最相似的。所以我们可以直接把整个纹理涂成这个颜色，以获得一个合理的结果。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232372-a244d012-b35a-446b-b729-6f8ec4bab2bb.png" width="400"/>
</p>

20. 替换完光照纹理后，重新加载游戏。香蕉大剑完成!

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232383-1b97ed85-7965-4299-91bc-a233c5bfaa49.png" width="800"/>
</p>

## The Bownana

接着是更复杂的模型，我将演示如何通过替换试作澹月来创建一个 Bownana。这个方法也适用于任何带有顶点组的单手剑/长柄/双手剑（例如，普通的流苏）。大部分步骤与香蕉大剑相同，但有一些额外的复杂情况我们需要考虑。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183232781-149695c9-19ae-40d5-983d-bde544e4ceaa.png" width="800"/>
</p>

1. 用与上一节相同的方法导入弓和香蕉模型（步骤 1-3）。我们可以通过检查原始模型是否有顶点组来确认我们要替换的模型属于这一部分

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233096-e6e169e3-eef4-4318-afb7-96d117216182.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/183233106-6fa7122a-a0cd-44fc-873e-5ad550a56ea5.png" width="300"/>
</p>

2. 由于我们要替换的形状不同，我们还需要改变修改模型的方式，以便正确放置：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233186-4f23dec9-1fed-4ca5-8737-4d83948922e6.png" width="300"/>
</p>

3. 设置 3dmigoto 自定义属性、TEXCOORDs 和 COLORs，与上一节相同（步骤 6-13）

4. 当我们需要处理原始的顶点组时，第一个主要的区别就出现了。这些组负责弓弦的拉动和弓的变形等事情。弓一共有五个组（注意：第 0 组完全没有权重，但仍然必须包括在内，以便正确导出；实际上，你只需要考虑四个组的问题）

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233193-cd119af9-9bdc-4d34-b975-aaeaf62f85ac.png" width="800"/>
</p>

5. 如果我们使用的模型不需要弓弦拉动动画，我们可以只使用一个单组顶点组，只在第 1 组上完全涂抹。 要做到这一点，我们进入对象数据属性，添加 5 个顶点组，命名为 0、1、2、3、4，然后进入权重涂抹，在第 1 组上完全涂抹该对象：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233231-a80f39b3-3ff4-4637-9c98-6849ea35ecea.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/183233232-d2ca7009-018b-473e-ad66-7c45bfd4ddef.png" width="300"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233268-381443f0-4286-489d-919f-0bed57056871.png" width="800"/>
</p>

(注意：你仍然需要包括所有五个组，以便新的对象能够正常导出)

6. 虽然这样可以，但效果不是很好，除非你用枪之类的东西来替换模型 - 理想情况下，我们希望 Bownana 有一个弦，并能正常变形。如果你使用的模型已经带有与原神使用的相似的顶点组，你可以合并和重命名它们，直到它们与原始模型相匹配。这个香蕉模型没有任何顶点，所以我们需要进行自动权重转移

7. 我们需要给香蕉装上弓弦。我们可以做一个新的，或者重新使用原来的弓弦 - 在本教程中我将采用后者。复制原来的弓，并删除除弦以外的所有东西：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233287-92ad4e09-e0de-4340-bc18-4c06788c7935.png" width="300"/>
</p>

8. 确保弦和香蕉对象的 UV 图名称一致（TEXCOORD.xy，以便 UV 图也能合并），然后通过 CTRL+点击两个对象并使用 CTRL+J 将这两个对象合并在一起。还要确保字符串的 UV 贴图是在具有正确颜色的纹理区域上。如果你之前创建了 TEXCOORD1.xy，你将需要重新创建它或者将弦移动到正确的位置。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233320-b0958745-27ea-4e7c-bcd4-d1d96c65d55c.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233326-2555eb32-0cfb-42f3-8901-c21175a99b34.png" width="400"/><img src="https://user-images.githubusercontent.com/107697535/183233328-d7b8e9e0-c657-4f94-8f23-7502c5e55844.png" width="400"/>
</p>

9. 现在我们有了我们的弓弦，是时候分配权重了。确保香蕉有 5 个顶点组，命名为 0、1、2、3、4，然后创建一个 DataTransfer 修改器。选择 Prototype Crescent 作为源，并选择顶点数据对象和顶点组标签：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233355-c230a973-86d9-4126-a227-d14d752af18d.png" width="300"/>
</p>

点击箭头并按 "应用"。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233365-ebd690c7-e63b-40a8-bca6-043d20f23557.png" width="300"/>
</p>

如果一切都做得很正确，那么现在 Bownana 的权重应该与原来的大致相同：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233373-46d4c532-5cb5-45c3-8a0c-0f0d4d43b1c2.png" width="800"/>
</p>

再仔细检查一下，看起来弓弦在游戏中具有适当的物理特性：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234166-b5a0bf83-f8e9-4168-a5c4-5be4bcb54742.png" width="400"/>
</p>

(注意：还有一种转移权重的方法，即在权重绘制模式中使用转移权重选项 - 这两种方法应得到类似的结果)

10. 从这一点开始，其余的步骤与香蕉大剑的步骤相同（上一节的第 14-20 步）：旋转和应用变换，重命名，导出，修复纹理，并加载到游戏：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233408-75bba365-d62a-478f-b934-1cda4b4beb7d.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183233419-5c1616e1-767f-40e0-870d-7bc6d3b68b36.png" width="800"/>
</p>

## Ripe Catalyst

最后，我将演示替换一个具有连续运动的法器武器（昭心）。这从根本上说与弓箭的工作方式非常相似，但法器以不同的方式使用顶点组。在这个过程中，我还将演示一些更高级的技术。

我假设你已经读过前两节，所以我将跳过大部分基本步骤，重点讨论法器与弓和剑的不同之处。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234781-4b859e82-a59f-4a4f-836d-af8118883d0b.png" width="800"/>
</p>

1. 法器像弓一样有顶点组，但与弓不同，法器用它们来控制运动。昭心总共有 5 个组，但其中只有 2 个是非空的：顶点组 1，它被分配给内球，顶点组 4，它有外环。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234795-b19d8e83-8c7e-4313-8b07-3d29e10e43d7.png" width="600"/>
</p>

当从上面看时，两者都是逆时针旋转的。任何被涂上顶点组 1 的东西都会围绕其中心快速旋转，而任何被涂上顶点组 4 的东西都会更慢地旋转。

2. 像以前一样，我们导入并定位香蕉。这一次，我想让它在中心位置旋转：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234810-88b522ba-2ff0-41c8-919c-57430c95be3b.png" width="400"/>
</p>

3. 设置 3dmigoto 自定义属性，TEXCOORDs 和 COLORs。
4. 因为我们想让它快速旋转，所以我们用顶点组 1 来画整个香蕉：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234827-655f9ca6-e086-4ac9-87fd-80729f72a4d8.png" width="600"/>
</p>

5. 旋转，应用变换，重命名并输出（我稍微放大了香蕉的尺寸，这样它就会产生更大的影响）。用前面部分的香蕉纹理替换漫反射和光照图

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234840-b24d52fb-69f8-49e0-9985-8e245d2f7762.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234863-c72cbbcc-dcdd-478a-9915-cc597fabf0d0.png" width="800"/>
</p>

香蕉现在应该加载，并以法器的原始中心部分的相同速度旋转。

6. 虽然我们现在在技术上已经完成了，但让我们玩玩一些效果，以证明你可以用纹理做什么。让我们从制作一个彩虹香蕉开始。

7. 从某处获得一个彩虹图像，然后在香蕉纹理上创建一个新层。将彩虹图像放在香蕉上，应用 50%的透明度。注意接缝，并确保颜色在整个长度上是一致的。

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234887-23d862de-6a96-460b-b8b0-dc95c6d9072a.png" width="400"/><img src="https://user-images.githubusercontent.com/107697535/183234899-d34c87f6-b616-42b1-b5f9-3cb054f3497f.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234916-3c4ab414-16e7-4985-924c-5505f1a4ce5a.png" width="800"/>
</p>

(香蕉变大只是你的想象)

8. 现在，我们也可以玩玩散射。我将使用这张星空图案的图片：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234930-73da1c1a-2a3b-4332-bd7a-46d4c8248543.png" width="400"/>
</p>

将其叠加在阿尔法层之上，你就可以在香蕉上得到一个发光的星星图案：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234947-6a609268-653c-402c-beab-732dc4c1becd.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234952-1ccd69ca-a9f9-46c7-9563-f2b2943f4d4e.png" width="800"/>
</p>

9. 最后，让我们来玩玩渐变模式。之前，我们只是将 TEXCOORD1.xy 设置为沿武器的长度方向，所以它是线性渐变的，但实际上我们并不限于这样做。

如果我们把 TEXCOORD1 设置成这样，武器就会分三部分淡入：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234976-e5102f50-cd99-4ddc-9a15-7855f0318f0b.png" width="400"/>
</p>

如果我们这样设置，它就会在中途一下子淡化：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183234987-91f6cc37-1b83-4981-bac1-8cbfa96bb7f8.png" width="400"/>
</p>

最后，如果像这样设置，它会混乱地褪色：

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183235067-549af5b7-7c2b-48c7-b223-7f7002d460d8.png" width="400"/>
</p>

(到达终点的奖励：银河系香蕉)

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183235110-054ecd2a-0b60-4dc6-8a02-1d4db826d13d.png" width="400"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/107697535/183235121-7b745a4d-328d-4d1c-8622-c2f2f71010e5.png" width="800"/>
</p>
