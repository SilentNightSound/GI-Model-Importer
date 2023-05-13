[EN](README.md) | 中文

# Genshin-Impact-Model-Importer (GIMI)

原神导入自定义模型的工具和说明

#### 我强烈建议只使用私人服务器进行修改。在官方服务器会有被封号的高风险。我不赞成在官方服务器上使用这些工具和程序，如果你依然要在官服上使用，我对由此产生的任何后果不承担责任。

GIMI 是我对 3DMigoto 修改后的一个版本，以便与原神兼容。

你可以随意使用或修改本库内的脚本，但如果你在你的项目中使用这里提供的程序，请注明出处。我将持续更新并修复这个页面，所以请经常回来查看。

故障排除指南: [看这里](Guides/CN_Troubleshooting.md)

关于如何使用这些工具移除角色建模的简单指南，请参见[莫娜帽子移除教程](Guides/CN_MonaWalkthrough.md)。关于创建自定义武器的中级指南，请参见[自定义武器修改指南](Guides/CN_BananaWeaponWalkthrough.md)。关于导入自定义模型的更高级的例子，请看塞伯坦伟大的视频指南[这里](https://www.youtube.com/watch?v=7ijMOjhEvBw)和 SinsOfSeven#3164 文字记录和故障排除指南[这里](https://rentry.co/3dmigPlug_AnimeGame)。

模型文件位于 [GI-Model-Importer-Assets](https://github.com/SilentNightSound/GI-Model-Importer-Assets)

## 安装说明 (3DMigoto)

1. 从[此处](https://github.com/SilentNightSound/GI-Model-Importer/releases)中下载并解压 3dmigoto.zip。我提供了两个版本：

   - "3dmigoto-GIMI-for-development.zip" 是开发者版本，用于创作 mods，但比较慢。
   - "3dmigoto-GIMI-for-playing-mods.zip" 是给玩家的精简版本，它关闭了开发功能（没有绿色文本），速度更快。

2. (V7 及以上版本会自动完成，你可以跳过这一步)根据你的 Genshin Impact.exe 文件的位置，你可能需要更改 d3dx.ini 文件中的这一行，以指向你自己的安装位置。（游戏.exe，而不是启动器.exe）

<img src="https://user-images.githubusercontent.com/107697535/174322200-b1afea95-53f5-4add-be89-698f85503908.png" width="800"/>

3. 双击 "3DMigoto Loader.exe"启动加载器，然后通过 GenshinImpact.exe 启动原神。如果到目前为止一切正常，3DMigoto 应该已被注入到游戏中，你应该可以在游戏中看到绿色文本（只有使用开发者版本才会显示，精简版不显示绿色文本）：

![image](https://user-images.githubusercontent.com/107697535/174324967-049b9879-c537-4bd0-b190-4ad7444fb8f1.png)

<img src="https://user-images.githubusercontent.com/107697535/174325193-1f58ab2c-86f8-4ce9-8697-6e7d140b2014.png" width="800"/>

- 注意：加载器显示 “unable to verify if 3dmigoto was loaded” 并不意味着 3dmigoto 未能注入 - 如果绿色文本/mods 有显示，就没有问题。

![image](https://user-images.githubusercontent.com/107697535/175563985-1e7d1298-08d0-4334-b6e8-c69769e3877a.png)

4. 安装完成！你现在应该可以使用 3DMigoto 加载自定义 mods 并覆盖贴图和着色器了。想要添加 mods，就把它们放在 Mods 文件夹中（每个角色只能有一个 mod），并在游戏中按 F10 加载。

![image](https://user-images.githubusercontent.com/107697535/175611402-c3f600ca-4136-4561-b33a-f4edf6153d1a.png)

&nbsp;

## 安装说明 (3DMigoto Blender 插件)

要是你想自行修改游戏模型，你还需要配置 Blender 插件和环境。3DMigoto 插件只适用于 Blender 2.80 以上的版本

1. 下载并安装 Blender

2. 下载并安装修改过的 [3DMigoto 插件](https://github.com/SilentNightSound/GI-Model-Importer/releases)。前往 Edit -> Preferences -> Add-Ons -> Install，选择刚下载的 .py 文件以安装插件。

3. 如果操作正确，你应该会在插件列表中看到 3DMigoto，以及在导入和导出菜单中的新选项。

<img src="https://user-images.githubusercontent.com/107697535/174328624-ccb14ded-57b2-4ac7-b0a0-0de118119174.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174329025-981a1a9f-7c56-4f44-804b-1b0394b8bd33.png" width="800"/>

&nbsp;

## 使用指南

看[这里](Guides/CN_UsageInstructions.md)

另外，如果你有任何关于修改的问题，请加入原神 mod 制作的 Discord，网址是 https://discord.gg/agmg

&nbsp;

## 致谢

衷心感谢 DarkStarSword，bo3b，和 Chiri 的 3dmigoto!
