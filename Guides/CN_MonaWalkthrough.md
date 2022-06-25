[EN](MonaWalkthrough.md) | CN

## 莫娜帽子移除教程

这个教程描述了从角色网格中删除一个对象（莫娜的帽子）的全过程。

在 3Dmigoto 之前，没有办法干净地删除她的帽子 - 它没有独特的着色器，所以不能在 SpecialK 中删除；它在 unity 对象层次中也不是一个独特的对象，所以不能用 Melon 删除；与它相连的骨骼也与莫娜的头发相连，意味着任何试图改变骨骼结构的行为都会导致头发被破坏。

以下的说明通常可以应用于移除网格的任何部分，不过在某些情况下，模型下面会有一个洞（特别是对于较大的物体） - 关于如何修补网格洞的教程以后会加。

1. 确保你已安装了 3DMigoto 和 3DMigoto Blender 插件 （请看 [README](../CN_README.md)）
2. 从此库中的 CharacterData 文件夹中下载莫娜角色文件。文件结构应该像下图：

<img src="https://user-images.githubusercontent.com/107697535/174457855-299ecb18-70d8-4ade-ae06-c178ab0b8779.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174457572-77532f14-02ab-4bfb-904d-fe2ad251d84a.png" width="800"/>

3. 我们现在要把模型导入到 Blender 中。在 File->Import 中，有一个选项可以导入 3DMigoto Frame Analysis Dumps。如果你没有看到这个选项，请确保3DMigoto 插件已经正确安装并激活。

<img src="https://user-images.githubusercontent.com/107697535/174457627-5b52357a-0983-4dd5-bf64-301ada192a07.png" width="800"/>

4. 去到角色文件夹并选中所有的 .txt 文件。将所有设置保留为默认，然后按导入。

<img src="https://user-images.githubusercontent.com/107697535/174457693-c5fa6ef1-799a-471a-ba2d-7ecc55decc8f.png" width="800"/>

5. 如果没出错，你应该能看到莫娜的模型被导入到视口中。它由两个对象组成，头部和身体。

<img src="https://user-images.githubusercontent.com/107697535/174457712-3499f864-50cb-4b18-b01e-bf88a5d8fd5e.png" width="800"/>

6. 我们要删除帽子，所以选择头部网格并进入编辑模式。选中显示帽子的所有顶点，然后删除它们。

<img src="https://user-images.githubusercontent.com/107697535/174457736-387f6a53-1d33-4a5b-88c5-972d52e05304.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174457765-c59e3e10-0187-4578-9b0b-21dd47d316e7.png" width="800"/>

7. 现在已经把莫娜的帽子去掉了，我们要导出模型。确保有一个名为 "MonaHead" 的对象和一个名为 "MonaBody "的对象（还有一个名为 "CharExtra" 的对象，用于有第三部分的角色 - 莫娜只有两部分）。导出的选项在 File->Export->Exports Genshin Mod folder。去到你加载原始数据的角色文件夹，并将模型导出为 "Mona.vb"

<img src="https://user-images.githubusercontent.com/107697535/175569818-4d150043-555c-41a7-90ca-3d0e05c1c3f5.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/175570101-9717b9eb-7ef9-4e1c-82e2-f6871497f5f6.png" width="800"/>

8. 这会在原始文件夹旁生成一个 MonaMod 文件夹

<img src="https://user-images.githubusercontent.com/107697535/174458059-363b1c56-ea76-4a01-9e1f-6e22f3b0949f.png" width="800"/>

   - (注意：生成 Mod 文件夹的另一种方法是用 3DMigoto raw buffers 选项将每个组件分别导出为 MonaHead 和 MonaBody，然后使用genshin_3dmigoto_generate.py 脚本，`python .\genshin_3dmigoto_generate.py -n "Mona"`)

9. 把 MonaMod 文件夹复制到 3DMigoto Mods 文件夹里

<img src="https://user-images.githubusercontent.com/107697535/174458172-01751459-13a5-4e11-9827-f039dc762066.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174458178-e09637de-7149-463e-bd7a-499e986cba1d.png" width="800"/>

10. 原神里按 F10 重新加载所有 .ini 文件和应用 MOD。如果一切都按计划进行，你的莫娜现在就没有帽子了!

<img src="https://user-images.githubusercontent.com/107697535/174458194-426f8602-31d5-416a-96ed-d58ecdcee39d.png" width="800"/>

我们可以再做一些改进。注意到莫娜的头发在帽子的位置有阴影 - 这是由她头部的 lightmap 控制的。角色文件夹中包括这个文件 MonaHeadLightMap.dds，我们可以修改它来进一步改善效果。

11. 在安装了 dds 插件的 Paint.net 中打开 MonaHeadLightMap.dds，并去除透明层，我们可以看到莫娜的部分头发贴图被阴影所覆盖。

<img src="https://user-images.githubusercontent.com/107697535/174458242-75283d3c-72d5-4043-b75d-6273dce32671.png" width="800"/>

12. 我们可以将颜色平滑化、标准化，并重新应用透明层。

<img src="https://user-images.githubusercontent.com/107697535/174458258-1c92a244-40e9-45c5-9a50-da3bfaa2bca4.png" width="800"/>

13. 最后，我们可以通过直接覆盖 MonaMod 文件夹中的 MonaHeadLightMap.dds 或将其放回 Mona 角色文件夹中并重新创建 MOD 文件夹（插件每次运行时都会从角色文件夹中提取贴图 .dds）来替换 MOD 当前使用的 MonaHeadLightMap.dds。

<img src="https://user-images.githubusercontent.com/107697535/174458283-1bec92ab-5008-4ae6-a6f8-110d7a0dee49.png" width="800"/>