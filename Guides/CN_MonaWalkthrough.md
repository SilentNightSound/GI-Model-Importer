[EN](MonaWalkthrough.md) | 中文

## 莫娜帽子移除教程

这个教程描述了从角色网格中删除一个对象（莫娜的帽子）的全过程。

在 3Dmigoto 之前，没有办法干净地删除她的帽子——它没有独特的着色器，所以不能在 SpecialK 中删除；它在 unity 对象层次中也不是一个独特的对象，所以不能用 Melon 删除；与它相连的骨骼也与莫娜的头发相连，意味着任何试图改变骨骼结构的行为都会导致头发被破坏。

以下的说明通常可以应用于移除网格的任何部分，不过在某些情况下，模型下面会有一个洞（特别是对于较大的物体）——关于如何修补网格洞的教程以后会加。

1. 确保你已安装了 3DMigoto 和 3DMigoto Blender 插件 （请看 [README](../CN_README.md)）
2. 从[此库](https://github.com/SilentNightSound/GI-Model-Importer-Assets)下载莫娜角色文件。文件夹应该像下图：

<img src="https://user-images.githubusercontent.com/107697535/178895141-ba8572ba-091c-4c49-85e6-841634747211.png" width="600"/>

3. 我们现在要把模型导入到 Blender 中。在 File->Import 中，有一个选项可以导入 3DMigoto Frame Analysis Dumps。如果你没有看到这个选项，请确保 3DMigoto 插件已经正确安装并激活。

<img src="https://user-images.githubusercontent.com/107697535/174457627-5b52357a-0983-4dd5-bf64-301ada192a07.png" width="800"/>

4. 进入角色文件夹并选中所有的 .txt 文件。将所有设置保留为默认，然后按导入。

<img src="https://user-images.githubusercontent.com/107697535/174457693-c5fa6ef1-799a-471a-ba2d-7ecc55decc8f.png" width="800"/>

5. 如果没出错，你应该能看到莫娜的模型被导入到场景中。它由两个对象组成，头部和身体。

<img src="https://user-images.githubusercontent.com/107697535/174457712-3499f864-50cb-4b18-b01e-bf88a5d8fd5e.png" width="800"/>

6. 我们要删除帽子，所以选择头部网格并进入编辑模式。选中显示帽子的所有顶点，然后删除它们。

<img src="https://user-images.githubusercontent.com/107697535/174457736-387f6a53-1d33-4a5b-88c5-972d52e05304.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174457765-c59e3e10-0187-4578-9b0b-21dd47d316e7.png" width="800"/>

7. 现在已经把莫娜的帽子去掉了，我们要导出模型。确保有一个名为 "MonaHead" 的对象和一个名为 "MonaBody "的对象（还有一个名为 "CharExtra" 的对象，用于有第三部分的角色——莫娜只有两部分）。导出的选项在 File->Export->Exports Genshin Mod folder。进入加载原始数据的角色文件夹，并将模型导出为 "Mona.vb"

<img src="https://user-images.githubusercontent.com/107697535/175569818-4d150043-555c-41a7-90ca-3d0e05c1c3f5.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/175570101-9717b9eb-7ef9-4e1c-82e2-f6871497f5f6.png" width="800"/>

8. 这会在原始文件夹旁生成一个 MonaMod 文件夹（如果 mod 文件夹没有生成，请仔细检查你要导出的文件夹是否有 hash.json）：

<img src="https://user-images.githubusercontent.com/107697535/174458059-363b1c56-ea76-4a01-9e1f-6e22f3b0949f.png" width="800"/>

- (注意：生成 Mod 文件夹的另一种方法是用 3DMigoto raw buffers 选项将每个组件分别导出为 MonaHead 和 MonaBody，然后使用 genshin_3dmigoto_generate.py 脚本，`python .\genshin_3dmigoto_generate.py -n "Mona"`)

9. 把 MonaMod 文件夹复制到 3DMigoto Mods 文件夹里

<img src="https://user-images.githubusercontent.com/107697535/174458172-01751459-13a5-4e11-9827-f039dc762066.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458178-e09637de-7149-463e-bd7a-499e986cba1d.png" width="800"/>

10. 原神里按 F10 重新加载所有 .ini 文件并应用 MOD。如果一切都按计划进行，你的莫娜现在就没有帽子了!

<img src="https://user-images.githubusercontent.com/107697535/174458194-426f8602-31d5-416a-96ed-d58ecdcee39d.png" width="800"/>

我们可以再做一些改进。注意到莫娜的头发在帽子的位置有阴影——这是由她头部的 光照图控制的。角色文件夹中包括这个文件 MonaHeadLightMap.dds，我们可以修改它来进一步改善效果。

11. 为了编辑 dds 纹理，我们使用 Paint.net 的[DDS 插件](https://forums.getpaint.net/topic/111731-dds-filetype-plus-04-11-2022/)和任何允许我们编辑 alpha 层的插件 [Alpha Mask Import](https://forums.getpaint.net/topic/1854-alpha-mask-import-plugin-20/) 或 [Modify Channels](https://forums.getpaint.net/topic/110805-modify-channels-v111-2022-03-07/)——我将在本教程中使用前者，关于后者的例子，请参见 [GI_Assets](https://github.com/zeroruka/GI_Assets/wiki/Creating-Skins)。

12. 打开 MonaHeadLightMap.dds，我们可以通过点击 Effects->Alpha Mask 并确保所有选项都未被选中，然后按 OK 键来移除透明层：

<img src="https://user-images.githubusercontent.com/107697535/175790813-24c1e522-41d1-42f5-a661-f25f7787dd4a.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/175790898-f26b3f1d-6ed2-4f71-b186-c94ddf44174b.png" width="800"/>

13. 我们现在可以看到，莫娜的头发纹理的部分是比较暗的。我们可以把这些抹平，以消除莫娜头发上的阴影：

<img src="https://user-images.githubusercontent.com/107697535/174458242-75283d3c-72d5-4043-b75d-6273dce32671.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458258-1c92a244-40e9-45c5-9a50-da3bfaa2bca4.png" width="800"/>

14. 然后，我们可以先选择整个图像，然后点击 Effects->Alpha Mask，勾选 "Invert Mask" 选项，重新应用透明层：

<img src="https://user-images.githubusercontent.com/107697535/175790958-5530e001-655b-4966-9e03-23be7dd93c7d.png" width="800"/>

- 注意：此步骤会导致部分材质效果消失（比如神之眼的亮光），因为我们正在反转整个图像的透明通道——如果你想在重新应用时保留原始效果，请参阅 https://www.youtube.com/watch?v=1y8oZ1TFZtg ，了解使用蒙版选择性地将反转应用于图像的一部分的例子（教程是针对 Special K，但 3dmigoto 功能相同），或者你可用 [Modify Channels](https://forums.getpaint.net/topic/110805-modify-channels-v111-2022-03-07/) 插件。

15. 将图保存为 .dds，确保使用 "BC7（Linear，DX 11+）"并设置 Generate Mip Maps（注意：导出时 lightmap 需要使用 BC7 Linear，Diffuse 使用 BC7 SRGB）

<img src="https://user-images.githubusercontent.com/107697535/175790979-3f20d159-0eec-4fc0-947d-0cd6b02c95c9.png" width="800"/>

16. 最后，我们可以通过直接覆盖 MonaMod 文件夹中的 MonaHeadLightMap.dds 或将其放回 Mona 角色文件夹中并重新创建 mod 文件夹（插件每次运行时都会从角色文件夹中提取最新的纹理.dds）来替换 mod 当前使用的 MonaHeadLightMap.dds

<img src="https://user-images.githubusercontent.com/107697535/174458283-1bec92ab-5008-4ae6-a6f8-110d7a0dee49.png" width="800"/>
