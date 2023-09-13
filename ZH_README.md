[EN](README.md) | [简体中文](CN_README.md) | 繁體中文

# Genshin-Impact-Model-Importer (GIMI)

將客製化模型匯入原神的說明及工具

#### 強烈建議只在私人伺服器開啟模組遊玩。在官方伺服器下使用這些工具很可能會被封鎖帳號。如果你堅持要在官方伺服器中使用，我將不對任何後果負責。

GIMI 是我修改 3DMigoto 後支援原神的版本。

這個程式庫內的程式皆能自由使用，但請記得，如果你使用了這裡的任何程式，請註明出處。這裡將會持續更新更多功能和錯誤修復，所以請經常來查看。

故障修復: [>按這裡<](Guides/Troubleshooting.md)

一個用這些工具移除角色建模的簡單教學： [莫娜帽子移除教學](Guides/MonaWalkthrough.md).
更加進階的自訂武器模型製作 [自訂武器模型製作](Guides/BananaWeaponWalkthrough.md).
更進階的模型匯入可以看這個由 Cybertron 製作的優秀教學影片 [這裡！](https://www.youtube.com/watch?v=7ijMOjhEvBw) 還有 SinsOfSeven#3164 的註釋腳本與故障排除教學 [這裡](https://rentry.co/3dmigPlug_AnimeGame).

模型的檔案位於 [GI-Model-Importer-Assets](https://github.com/SilentNightSound/GI-Model-Importer-Assets)

## 安裝說明 (3DMigoto)

1. 下載 [這裡](https://github.com/SilentNightSound/GI-Model-Importer/releases)的 3dmigoto.zip 檔並且解壓縮，裡面有兩種版本：
   - "3dmigoto-GIMI-for-development.zip" 打開了所有的功能(所以載入會比較慢)，用於創作模組，會有綠色的文字出現。
   - "3dmigoto-GIMI-for-playing-mods.zip" 是給模組玩家的精簡版本，因為關閉了開發者的功能，會執行得更快。
   

2. (V7以上會自動完成這步，可以跳過) 根據你安裝原神(Genshin Impact.exe)的位置，你可能需要在 d3dx.ini 的這一行將 target 指向你的遊戲。(不是啟動器，是你的遊戲本體，本體通常會在叫 Genshin Impact Game 的資料夾裡)。如果這沒有效果，可以試試看 `target = GenshinImpact.exe`:

<img src="https://user-images.githubusercontent.com/107697535/174322200-b1afea95-53f5-4add-be89-698f85503908.png" width="800"/>

3. 點兩下 "3DMigoto Loader.exe" 來打開模組載入器，然後用打開  GenshinImpact.exe 的方法啟動原神。如果前面沒出差錯， 3DMigoto應該已經植入遊戲，且你會看到綠色的文字。(如前面所述，玩家版本並不會顯示綠色文字)

![image](https://user-images.githubusercontent.com/107697535/174324967-049b9879-c537-4bd0-b190-4ad7444fb8f1.png)

<img src="https://user-images.githubusercontent.com/107697535/174325193-1f58ab2c-86f8-4ce9-8697-6e7d140b2014.png" width="800"/>

   - 注意：載入器顯示 “unable to verify if 3dmigoto was loaded” 不代表3DMigoto沒有載入。只要mod和綠色文字有出現，就是成功了。

![image](https://user-images.githubusercontent.com/107697535/175563985-1e7d1298-08d0-4334-b6e8-c69769e3877a.png)

4. 安裝完成！你現在可以用 3DMigoto 載入各種模組，並覆蓋原本的貼圖與著色器了。要加入新的模組，就將它們放入 Mods 資料夾裡，並按 F10 載入。

![image](https://user-images.githubusercontent.com/107697535/175611402-c3f600ca-4136-4561-b33a-f4edf6153d1a.png)

&nbsp;
## 安裝說明 (3DMigoto 的 Blender 外掛)

如果你想自己修改模組，你還需要將你的 Blender 外掛和環境設定好。這個外掛能在 Blender 2.8 以上使用。

1. 下載並安裝 Blender。

2. 下載並安裝修改過的(blender_3dmigoto_gimi.py) [3DMigoto 外掛](https://github.com/SilentNightSound/GI-Model-Importer/releases). 在 Edit -> Preferences -> Add-Ons -> Install 選擇剛剛下載的 .py 檔案，即可安裝。 

3. 如果正確安裝了，你會在外掛列表中看到 3DMigoto，以及在匯入、匯出選單中的新選項。

<img src="https://user-images.githubusercontent.com/107697535/174328624-ccb14ded-57b2-4ac7-b0a0-0de118119174.png" width="800"/>

<img src="https://user-images.githubusercontent.com/107697535/174329025-981a1a9f-7c56-4f44-804b-1b0394b8bd33.png" width="800"/>

&nbsp;
## 使用指南

參見 [這裡](Guides/CN_UsageInstructions.md)(繁體中文翻譯中！)

另外，如果對於模組製作有任何問題，歡迎加入我們在discord的社群：https://discord.gg/gR2Ts6ApP7。認證只需要你證明自己能透過上面的步驟啟動 GIMI 。

&nbsp;
## 致謝

誠摯感謝 DarkStarSword, bo3b and Chiri 為 3DMigoto 付出的心力！
