# 故障排查

GIMI 工具的常见问题列表。

#### 在尝试本页面上的任何内容之前，请确保你使用的是最新版本的插件、人物数据和程序。我看到的大多数问题都是因为使用旧版本工具。

## 安装问题

三个最常见的问题是：

- 仔细检查你在 d3dx.ini 文件中的 Genshin.exe/Yuanshen.exe 位置是否正确(V7 及以上版本可以跳过这个步骤)，游戏文件夹中有两个 exe 程序，一个是启动器，一个是用于游戏本身，你需要的是后者
- 如果绿色文本没有显示出来，请确保你使用的是开发者版本。精简版没有绿色文本
- 确保你是以管理员身份运行 GIMI 加载器和原神

如果 3dmigoto 加载器的控制台窗口在游戏加载后关闭，这没有问题，这是预期的行为。

如果你得到一个类似“Unable to verify if 3dmigoto successfully loaded”的消息，这并不意味着该程序未能注入，只是加载器无法判断。如果它在游戏中看起来是正常的，你可以关闭这个窗口（事实上，你应该这样做，因为让这个窗口打开会导致计算机速度减慢）。

![image](https://user-images.githubusercontent.com/107697535/181086591-24f5be97-b6b0-4483-b694-2bc258c0d9e9.png)

3dmigoto 可以和其他类型的原神修改工具或加载器一起运行——只要先运行 3dmigoto 加载器，然后再运行你的其他程序。

我偶尔注意到一个问题，即使一切设置正确，3dmigoto 也无法注入——在这些情况下，重新尝试注入就能解决这个问题。

## 模型导入问题

如果你在该文件夹中没有看到任何东西，请确保你是从 ModelData 文件夹而不是 Mod 文件夹中载入数据的（目前不支持从 Mod 文件夹中载入文件）。正确的文件夹应该包含 vb 和 ib.txt 文件。

### 如果你在加载模型时得到这个错误，你使用的是一个过时的插件。旧的插件只支持 Blender 2.80-2.92

![image](https://user-images.githubusercontent.com/107697535/181087328-1a3769dc-ab8b-4d2d-b35c-2a42c3ea6bf8.png)

几乎所有其他错误都是由于你试图加载的模型的问题。最常见的是 4D 法线，这是由于收集脚本转储了模型的一个组件，并错误地将其标记为法线。

## 模型导出问题

在排除故障之前，请仔细检查你已经完成了以下列表中的所有事项:

- 你试图在 Blender 场景中导出的对象被命名为 ObjectHead、ObjectBody、ObjectDress 和 ObjectExtra，而且每个对象只有一个（你有多少个对象取决于原始模型有多少个）
- 你正在导出原始模型所在的 ObjectData 文件夹（不是 Mod 文件夹），并将其导出为 Object.vb。仔细检查你导出的文件夹是否有 hash.json。
- 你正试图导出与你要替换的模型原来相同数量的组件
- 你在场景中导出的对象没有一个是完全空的（需要在所有对象上至少有一个面，可以把它缩小来隐藏它）。
- 所有的对象都有 3dmigoto 的自定义属性，要么是通过与最初使用该插件导入的对象合并，要么是通过使用自定义属性转移脚本。(https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Tools/custom_property_transfer_script.txt)
- UV 图被命名为 TEXCOORD.xy、TEXCOORD1.xy、TEXCOORD2.xy......等等，直到模型的原始编号为止。
- 该模型有顶点色，颜色组件被称为 COLOR

现在，说说最常见的问题。你可以通过打开控制台窗口来获得更多关于导出时出现问题的细节：

<img src="https://user-images.githubusercontent.com/107697535/181120815-a4edf981-3a9c-4b7e-a4ff-971525fc51a4.png" width="600"/>

- ### 这是由于没有导出到 ObjectData 文件夹，或者没有导出为 Object.vb 的结果。

<img src="https://user-images.githubusercontent.com/107697535/181119266-3dad9f81-e06a-483a-b8da-ad3a7749fd15.png" width="600"/>

- ### 这通常是由于命名不正确造成的，请确保将其称为 Object.vb

<img src="https://user-images.githubusercontent.com/107697535/181120923-0400c672-9fea-45b4-8200-f439680a0882.png" width="600"/>

- ### 这是因为某个组件有太多匹配的名字（例如 HuTaoBody 在场景中出现了两次）。删除或重命名组件，直到只剩下一个与之匹配的名字

![image](https://user-images.githubusercontent.com/107697535/181121033-179fefe9-db4f-49bc-a8f5-29cfa047fcd6.png)

- ### 如果你在使用自定义属性转移脚本时遇到这个错误，确保你在 blender 中替换了名称

![image](https://user-images.githubusercontent.com/107697535/181121317-19ded6ec-0e39-430e-a476-ae3335ced1a9.png)

- ### 这是因为缺少 COLOR 组件或命名错误。确保顶点颜色存在并且被正确命名

![image](https://user-images.githubusercontent.com/107697535/181121492-9d1e4bdd-7cb0-46ee-bceb-8621e92577fd.png)

- ### 这个问题是由于你使用的模型有超过 64k 的顶点。要么删除部分，要么使用精简

![image](https://user-images.githubusercontent.com/107697535/181123500-2afc4794-e982-4d95-8a42-c4e914341d30.png)

- ### 这个是因为你的一个对象是完全空的。请确保至少有一个面，这样 UV 贴图才能正常导出。

![image](https://user-images.githubusercontent.com/107697535/181129949-fb92afe5-240e-4baa-bf8e-145345d02456.png)

- ### 这个是旧版本的插件的一个错误，请确保更新

<img src="https://user-images.githubusercontent.com/107697535/181120616-55ae3885-181f-4f82-8282-c080ddccbb4b.png" width="600"/>

## 游戏中的模型问题

这是故障排除中最棘手的部分——在将模型导入游戏时，有很多很多东西会出错。我将尝试涵盖一些最常见的问题类别

- ### 模型无法全部加载

确保 3dmigoto 确实在运行，并且你已经把 mod 放在正确的 Mods 文件夹中。还要确保在游戏中按下 F10 键，重新加载 mods。最后，如果所有其他方法都失败了，试着清空你的 ShaderCache 和 ShaderFixes 文件夹，因为这些有时会导致加载 mods 时出现问题。

- ### 模型加载，但一些部分没有被绘制出来

<img src="https://user-images.githubusercontent.com/107697535/181122972-385a6fef-e925-4f80-8469-65be168ef678.png" width="300"/>

这是由于模型上的顶点限制。任何带有混合权重/顶点组的东西都有一个奇怪的地方，顶点限制实际上需要在 3dmigoto dll 中提高，以便它能正常工作。我提高了大多数角色的顶点限制，但漏掉了一些——仍在研究为所有对象设置顶点限制的方法。

- ### 大量关于 mod 冲突的警告

<img src="https://user-images.githubusercontent.com/107697535/181122365-2280b266-3313-4807-b2a5-be23bf92b650.png" width="300"/>

这是由于游戏试图将一个以上的文件加载到同一个哈希值而造成的。这通常是由于同时为同一个角色使用两个 mods 造成的，但旧版本的工具也有一个 bug，共享的脸部组件在多个地方被覆盖。

要解决这个问题，请删除任何重复的 mod 文件夹。如果你确定你已经删除了所有这些文件夹，但警告仍然出现，请进入警告中提到的.ini 文件，删除或注释这些行。

- ### 模型加载，但在游戏中不显示出来/加载模型时出现错误

<img src="https://user-images.githubusercontent.com/107697535/181129048-51bc2c88-3614-4490-980a-ac26308e97dd.png" width="600"/>

与警告不同，错误通常表明程序在 mod 中加载失败。原因可能各不相同，但一些常见的原因是：

1. 名称不正确（.ini 文件中的名称与文件夹中的文件不一致，如扩展名不同）
2. 纹理有错误的格式（查看原件以了解什么格式，通常是 dds，并且必须有高度/宽度是 2 的幂，并且有 1024x1024、2048x2048、1024x2048 等整数比例）。
3. 当旧模型有顶点组时，没有在新模型上绘制/转移任何顶点组。

- ### 物体以错误的方向载入

<img src="https://user-images.githubusercontent.com/107697535/181124642-22c9ca43-5dc7-46df-aab8-63ad20dde1ae.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181126765-89546874-3ebc-42bb-9b64-a5584a6d6154.png" width="300"/>

这是因为在 blender 中由 3dmigoto 导入的对象和你要替换的对象使用的是不同的坐标空间。即使它们在 Blender 中看起来是一致的，你实际上可能需要相对于 3dmigoto 模型进行旋转和平移，以获得正确的方向。最常见的是，将角色模型旋转 90 度，使其朝上，然后选择所有的模型并应用所有的变换。

旧（枫原万叶）和新（诺艾尔）之间正确方向的例子

<img src="https://user-images.githubusercontent.com/107697535/181127089-41f5ba37-5882-4666-a7e5-70814876ace5.png" width="300"/>

- ### 模型是完全错误的

<img src="https://user-images.githubusercontent.com/107697535/181131070-f19c14d4-2e59-4bf2-8a59-a41ee45ddc24.png" width="150"/> <img src="https://user-images.githubusercontent.com/107697535/181132251-1f118616-c011-4af9-9bb3-21000ac5ba3b.png" width="150"/> <img src="https://user-images.githubusercontent.com/107697535/181132357-f7721ddc-201d-4fb6-8b3a-5d546059c224.png" width="300"/>

很可能是由于顶点组的问题。顶点组的数量、顺序和位置需要在新模型和旧模型之间进行匹配。确认所有的顶点组在新模型中都存在，它们的顺序是正确的（例如 4 6 7 8 5 应该是 4 5 6 7 8）并且没有缺少（例如 4 7 8 9 -> 4 5 6 7 8 9）。

- ### 模型有轻微的故障

<img src="https://user-images.githubusercontent.com/107697535/181132663-e1dd363a-51e3-488b-8c4c-09a35fcfc00a.png" width="150"/> ![image](https://user-images.githubusercontent.com/107697535/181132608-84c4082c-1d0a-44c8-94ed-f06a3f62c014.png)

仍然是顶点组的问题——仔细检查上述内容，并确保该部分的新模型的重量与原模型的重量相一致

- ### 纹理不正确

<img src="https://user-images.githubusercontent.com/107697535/181128459-e09c9d4a-2b04-4a5c-b338-2f46c455f0b7.png" width="300"/><img src="https://user-images.githubusercontent.com/107697535/181128502-b5587610-b61c-4b50-b60c-a73f68e89bab.png" width="100"/>

这可能是由于各种各样的原因，最常见的是:

1. 没有将 uv 图命名为 TEXCOORD.xy
2. 反转法线
3. 损坏或不正确的 ObjectTexcoord.buf
4. 忘了用新的纹理替换，所以仍然在加载原始模型的旧纹理。

- ### 非常明亮/发光的纹理

<img src="https://user-images.githubusercontent.com/107697535/181130063-abafbd57-c44b-409e-b502-36957a96d776.png" width="300"/>

这很可能是由于你使用的纹理图没有 alpha 通道。详细情况请参考本项目中的指南，基本上要确保你在任何纹理文件的顶部有一个透明层（顶层用于控制发射并使事物明亮，底层用于绘制模型的颜色和图案）。

- ### 厚重或异常的颜色轮廓

![image](https://user-images.githubusercontent.com/107697535/181130423-54b0b03a-3f8f-4b66-99f8-36a98bca16ee.png) <img src="https://user-images.githubusercontent.com/107697535/181130493-1efae42a-2a48-4e69-807e-7865776fda9b.png" width="150"/>

这是由于一个不正确的顶点色值造成的，有三种方法可以解决：

1. 从模型的某个部分复制顶点色数据，该部分在原件上有正确的轮廓。（详见https://youtu.be/z2nvJzkwHHQ?t=475）
2. 用这个脚本改变轮廓的厚度：https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Tools/genshin_set_outlines.py （放置在 mod 文件夹中，使用 cmd 或者 powershell 命令输入：`python .\genshin_set_outlines.py --thickness t` 其中 t 是 0-255 的数字，代表轮廓的粗细，0 是没有轮廓，255 是轮廓最大值，大部分游戏使用的值是 80-130，但你应该试验下多少数值才是最适合你的模型）
3. 使用这个脚本删除轮廓: https://github.com/SilentNightSound/GI-Model-Importer/blob/main/Tools/genshin_remove_outlines.py

- ### 其他问题

在正常使用中，你可能不会遇到这些东西，但我只是想展示一下我的古神图片集。

步骤不正确的.ini 文件

<img src="https://user-images.githubusercontent.com/107697535/181133398-29294888-5c86-4477-9627-de6e11814e0e.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181133297-6ffdc6ba-df60-403d-be09-95f2ab62f889.png" width="300"/>

不匹配的 IB 和 VB

<img src="https://user-images.githubusercontent.com/107697535/181133473-a3ee5ff1-f138-4b0a-aa03-3cad5b592a0e.png" width="300"/> <img src="https://user-images.githubusercontent.com/107697535/181133485-372ddb47-9de6-4506-957c-017ed524737e.png" width="300"/>

在 VB 上重写而不是 IB

<img src="https://user-images.githubusercontent.com/107697535/181133582-ca88149a-8a9b-4838-a9f0-9e9008a55fe7.png" width="300"/>

## 模型倾倒问题

Section 即将到来，模型转储脚本仍然是实验性的。
