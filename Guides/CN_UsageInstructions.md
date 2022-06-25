[EN](UsageInstructions.md) | 中文

## 使用指南

下面是关于如何使用 3Dmigoto 的各种功能以及如何修改原神的模型和贴图的介绍。我已把内容按难度从最简单到最难排列 - 我建议按顺序阅读，因为后面的部分依赖于你理解前面的部分的工作原理。

本指南建议你对 Blender 熟悉

注意这个项目仍在开发中，所以会有错误和功能缺失。如有任何部分有错误或不清楚，请让我知道。

我强烈推荐这些视频作为用 3Dmigoto 做MOD的介绍：https://www.youtube.com/watch?v=zWE0xP4MgR8 和 https://www.youtube.com/watch?v=z2nvJzkwHHQ 

虽然原神的结构使修改它变得更加复杂，但这些视频中包含的大量信息仍然是相关的，可以提供更多的细节和视觉效果来帮助你解释。

### TLDR

(又称我现在不想通读所有内容，只想进行基本的模型修改)

(去除莫娜帽子的步骤请看[这里](CN_MonaWalkthrough.md))

1. 在 blender 中，去到 File -> Import -> 3DMigoto Frame Analysis Dump（vb.txt + ib.txt）。

2. 从这个库中的的 CharacterData 文件夹中选择你想要改的角色的文件（所有的角色至少要有一个头和身体，但有些还有额外的部分，比如裙子，我已把它们标为额外）。将所有选项保留为默认值，然后按导入。

3. 对模型进行你想要的修改，注意有以下限制。
   - Vertices 被限制在64K左右
   - 角色的面部是单独存储的 - 这些脚本和步骤还不支持面部的修改
   - 模型必须包含所有原始的 Vertex Group、颜色和属性 - 如果你使用了自定义模型，请确保它与原始模型相匹配，并且没有空隙。
   - 你可以在Blender中把纹理贴图连接到物体上，但可能要把 .dds 转换为 .png，Blender 才能识别到它，最后再然后再转回 .dds。

4.（非必要）对角色的 Diffuse 和 Lightmap 进行编辑。

5. 确保有一个名为 CharHead 的对象，一个名为 CharBody的对象，以及 CharExtra（非必要，取决于模型最初是否有。使用 Exports Genshin Mod Folder选项导出模型，将该对象保存为原始角色文件夹中的 Char.vb。
   - 确保你使用的是最新的 hash_info.json，否则脚本可能无法找到所需的 Hash 值生成 .ini 文件。

7. 将生成的 CharMod 文件夹移到你在安装步骤中创建的 3DMigoto 的 Mods 文件夹中。

8. 在游戏中按F10键加载MOD

每个角色在Mods文件夹中一次只能有一个对应的文件夹 - 如果你想为一个角色加载新的模型，需要先从 Mods 文件夹中删除旧的。

&nbsp;
### 寻找 Buffers

当 3Dmigoto 开启时，在数字键盘上按 0 可以开启狩猎模式（显示绿色文本，默认）或关闭（无文本）。

在狩猎模式下，你可以循环查看原神当前用于将物体绘制到屏幕上的各种 Buffers 和着色器。选中的 Buffers或着色器将会跳过它们的绘制，以向你显示它们负责绘制屏幕的部分。

按 "+" 按钮可以将所有当前选定的 Buffers 重置为零，在搜索或重新加载之间进行重置是一个好习惯，否则会变动很乱，让人搞不清到底选择了什么。

我建议在角色菜单中进行搜索，否则对象的数量很快就会变得不堪重负。

- 在数字键盘上按 / 和 * 可以循环浏览 Vertex Buffers（VB），包含了正在绘制到屏幕上的物体的 Vertex 信息。
- 在数字键盘上按 7 和 8 可以循环浏览 Index Buffers (IB)，包含了 Vertices 如何连接形成模型的信息。你可以用数字键盘 9 复制 Hash 值。
- 在数字键盘上按 4 和 5 可以循环浏览 Vertex Shaders（VS），包含了 Vertices 或 Faces 在屏幕上的位置信息。使用数字键盘 6 来复制 Hash 值。
- 在数字键盘上按 1 和 2 可以循环浏览 Pixel Shaders（PS），包含了如何将贴图和颜色应用到物体上的信息。使用数字键盘 3 来复制 Hash 值。

&nbsp;
### 移除缓冲器和着色器

当你找到了一个你想跳过的 Buffer 或着色器，你可以告诉 3DMigoto 即便没被选中也跳过该对象的绘制。

要做到这一点，在 Mods 文件夹中创建一个 .ini 文件（.ini 的文件名随意），并添加以下内容以跳过 VB/IB 。

```
[TextureOverrideX]
hash = Y
handling = skip
```

其中的 X 是你想要的任何名字，Hash 值对应于狩猎时找的 Hash（注意：这些是 Buffers 而不是贴图，但命名惯例将两者都称为了 "贴图"）。

加以下内容以跳过 VS/PS：

```
[ShaderOverrideX]
hash = Y
handling = skip
```

注意，有些对象可能有多个 Buffer 或着色器与之相关联 - 如果在 .ini 文件中放置上述代码后，对象的某些部分仍然存在（如阴影、反射、轮廓），请再次循环查看 Buffer 和着色器，看是否有其他负责绘制该部分的单元。

如果你要删除的角色模型的部分是由特定的 VB/IB/VS/PS 绘制的，那么这个功能就很适用 - SpecialK 在其着色器部分也有类似的功能。

&nbsp;
### 替换贴图

替换角色贴图比较简单，和 SpecialK 的操作方法类似：

1. 找到用于绘制模型的 IB，找到正确的的话模型就会消失。
2. 创建一个 texture override 部分，类似于在移除 Buffers 和着色器部分创建的内容，但要用以下内容来替换贴图：

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

注意这里没有用到 handling=skip，因为我们需要游戏绘制这部分。我们还需要通过创建一个资源对象将我们的新贴图加载到内存中。

有些物品没有对应的 Lightmap，而有些物品（比如角色）有多个在同一个 Buffer 上的贴图。

&nbsp;
### 移除多索引对象和 Frame Analysis Dumps 的 Buffers

有时，多个对象会被绘制在同一个 Buffer 上。一个例子是角色模型 - 头部和身体是独立的对象，但它们的绘制都是用同一个 VB/IB，所以如果你跳过那个 Buffer，最终会跳过整个对象的绘制。同样地，如果你试图替换缓冲区的任何地方，你将只能替换一个而不是另一个。

这时，狩猎菜单就没什么用了 - 我们必须开始深入查询绘制的调用。按 F8，我们可以执行 Frame Analysis Dump 以获得更多的信息。这将把所有与绘制单一帧有关的 Buffer 转储到一个名为 FrameAnalysis-timestamp 的文件夹，以及一个名为 log.txt 的文件，其中可以看到执行了哪些命令。

- 注意1: Frame Analysis Dump 可能较大（几 GB），所以要小心，不要在有很多对象的区域按F8。像在城市这样密集的地方按F8可能会导致你的游戏崩溃。建议从角色菜单中执行。
- 注意2: Frame Analysis Dump 可能会导致游戏暂停很长一段时间。根据你的硬件情况，它可能需要几秒到一分以上的时间。
- 注意3：我在 d3dx.ini 文件中启用了 txt 和 buf dump，以及其他一些提供更多信息的选项 - 默认的 .ini 文件关闭了 frame analysis 功能。

有了 Frame Analysis Dump，我们可以对我们感兴趣的 IB 所对应的 Hash 进行搜索。这将产生多个 -ib.txt文件，你可以打开这些文件来查看对象索引的开始和结束位置。然后，你可以在一个单一的对象上指定一个重写：

```
[TextureOverrideX]
hash = Y
match_first_index = Z
handling = skip
```
其中Z是你要匹配的 Buffer 中的对象的索引。

&nbsp;
### 模型 Vertices 的删除与修改

该部分仍在建设中，见TLDR

当我们有了 frame dump，我们就可以从 Buffer 中提取角色模型，以便进行编辑。通常情况下，这需要找到涉及绘制角色的 VB/IB Hash 值，从 frame dump 中收集相应的文件，使用 3Dmigoto 插件将相应的 Buffer 导入 Blender进行编辑，然后导出修改后的版本并用以下代码覆盖模型：

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

其中 stride 代表对应于单个 Vertex 的所有数据的字节大小（可在 dump headers 中查看），format 是单个索引值的大小。

在这种情况下，我们使用 handling = skip 跳过游戏的绘制调用，然后用 drawindexed = auto 加载我们自己的绘制调用（它会自动从 i b文件和 Buffer 描述中计算要绘制的对象的区域）。这些新的 VB 和 IB 资源会被传递给着色器，着色器会计算它们的位置并应用贴图。

可惜的是，原神并不那么简单。原神实际上将角色对象的属性分成了多个不同的 Buffer - 准确地说，至少有六个。一个用于位置/脸部数据（位置、法线、切线），一个用于混合（混合重量、混合指数），一个用于纹理（颜色、texcoord），一个用于绘制物体（包含这个特定帧的物体的位置数据，每帧重新计算），还有至少两个用于指定指数（有些角色有两个，有些有三个，取决于其模型的复杂性）。

此外，大多数 Buffer 有不同的 Hash 值，而不仅仅是一个单一的 Hash 对象被分割到不同的缓冲区槽中。这意味着如果我们只覆盖一个 Hash，模型就会崩溃，除非我们同时在每个相关的 Buffer 上覆盖正确的数据。

更加困难的是，3DMigoto 导出的 Header 文件实际上也是错误的。导出的 Header 文件包含所有 Vertex 数据的信息，而不仅仅是当前在 Buffer 中的数据。这导致了 Header 的编号/字节偏移，和实际数据不匹配，这意味着你必须直接从原始 Buffer 中重新计算实际数据是什么。

玩得开心吗？还有呢! 除了在一个 Buffer 上放置多个对象，然后在几个 Buffer 之间分割属性之外，它还使用更高的 Buffer 槽（VB1+）和点列表拓扑结构，这两个 3Dmigoto 都不支持，所以你必须转换回它支持的格式。

即使你做了以上所有的工作并将其导出到 Blender，3Dmigoto 也会将结果以一种不能被摄取回游戏的格式输出。所以你必须把上述过程倒过来，把它重新分割成各个部分。

总之，我写的脚本可以处理大部分的问题。你可以在一个只有主绘图 VB 的 frame dump 上运行 genshin_3dmigoto_collect.py 脚本，它将找到相关的 Buffer 文件并正确组织它们。同样，在 Blender 导出的 3Dmigoto 上运行 genshin_3dmigoto_generate，会将其分割成正确的 Buffer 文件，并重新整理 .ini 文件，以让所有东西都能正确加载。如果你对这个工作的具体细节感兴趣，可以看一下这些脚本。

&nbsp;
### 本地化的模型重写

仍在开发中，请参阅本页顶部的视频，以获得更多解释和不同游戏中的指南。

- 来自其他模型的模型不会有正确的 weights 或 vertex groups
- 导入模型，把它放在靠近/重叠原模型的地方，并把 vertex groups 和颜色转移给它。还要确保它有纹理uv值。
- 在移除部分 mesh 后修补模型上的小洞，或用其他 mesh 替换部分原 mesh 时效果最好（例如：鞋 -> 脚）。
- 如果你获得补丁的模型也来自游戏，并且是相同的身体类型，或者是从游戏模型衍生出来的模型，那么效果会更好。可以使用这些模型，但可能要改变格式来匹配。
- 较大的洞或物体的 Vertex weight将无法正确转移，因为Blender将无法正确插值。在这些情况下，你必须手动操作，或者从其他游戏模型中找到一个已经有正确分组的物体

&nbsp;
### 完整模型覆盖

仍在开发中，更多解释见本页顶部的视频。目前还不可靠，所以请自行尝试。以下是我在实验中发现的一些提示/观察：

- 基本概念是将你要替换的模型与新的模型尽可能地重叠，然后将 Vertex Groups、Weights、颜色和自定义属性转移过去。
- 模型的复杂性（Vertex/边缘）和形状需要大致相同，否则转移将无法顺利进行。即使模型非常相似，仍然可能遇到问题。
- 与原始模型相差太远的模型是不可能的，因为没有办法以一种合理的方式分配混合指数和 Vertices（如果你不在意动画，那就还是可以做到的）。
- 复杂的头发结构是一场噩梦。原神中几乎每个角色的头发都很简单是有原因的。除非你对 blender 很精通，否则我建议把所有的头发都分配给头部的 Veretex group，并放弃尝试让头发运动起来（或者坚持使用原来的头发）。
- 确保模型中的所有 Vertex 都有 Weights 或已被分配到一个组，并且组是正确的。通常情况下，由于手和手臂组离身体很近，Weight 转移最终会将它们转移到不正确的区域（最好是T-pose模型，但我还不确定如何从恒定缓冲区加载姿势信息），手指也有问题。
- 模型只使用两个 UV 图 - 一个用于头部，一个用于身体。有些角色实际上使用了第三个，比如裙子，但那只是身体纹理的一个副本，我不确定它是否可以被修改（即将进行测试）
- 一个特定的 Vertex 使用哪种 UV 取决于游戏将其分配给哪个对象。据我所知，游戏为每个角色硬编码了一个特定的索引值，并在此基础上进行分离。目前正在研究如何改变这一点并增加灵活性 
- 如果模型在加载时是朝下的，可能要相对于原始模型进行旋转（不确定是什么原因造成的，只在 mmd 模型中发生）。