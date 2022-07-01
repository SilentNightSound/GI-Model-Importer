Current TODO/open issues:  

Weapon/face replacement  

Version 4.1 (July 1, 2022)  
	- Improved the collect script to now try and identify the correct objects and corresponding draw calls without needing to be explicitely told  
	- Fixed a bug for models with a stride of 92 but no extra component  

Version 4 (June 30, 2022)  
	- Added a method of using the original model tangents when exporting to partially fix outline issues. I was unable to figure out how genshin calculate the tangents, but if the new model is similar enough to the old one we can just re-use the tangents and the result looks much closer to the original. Can use either by adding the flag `--original_tangents` on the generate.py or by clicking the "Use original tangents" button when exporting in the genshin plugin  
	- Added a script that lets you forcibly set the vertex COLOR values to specific values. This helps fix the black outline issue that some models can end up. Use with `python genshin_set_color.py -n CharTexcoord.buf --stride X -r R -g G -b B -a A` where X is the stride for the texcoord (found in the .ini, probably either 12 or 20) and RGBA are the values you want to set (values between 0 and 255, do not need to specify all values - if only one value is specified, sets that one only and leaves the rest the same. Most of the time you will want to only modify the A value and set it lower/to 0 to fix border issues). This will generate a new file called   CharTexcoordModified.buf which you can rename to replace the original (or change the name in the .ini)  
	- Added support for four object characters (e.g. Rosaria, Xiao, Yelan) to the collect and plugin/generate scripts, and added them to the characterdata folder. The second object is just named Extra2 on those models, but behaves the same way as the regular Extra  
	- Updated the 3dmigoto .dll to raise the limit on the buffers even more since some people were reporting models were still hitting it. Also raised the limit for the four object characters  

Planned:  
	- QoL features for the blender plugin (transfer custom properties, fill in missing vertex groups)  
	- Weapon and face support  
	- Disabling transparency filter for characters  

Version 3 (June 24, 2022)

Features:  
Updated and organized github pages and guides  
Split 3dmigoto plugin into development and release versions depending on use case  
Updated scripts for increased compatability with some models  


Version 2 (June 22, 2022)

Features:  
Raised vertex limit to 64k for all characters  
Finished dumping all character data to the folder with a few exceptions  
Fixed support for characters with three components  
Fixed texture bleed issue between components  
Added one-click export to the blender plugin  

Issues:  
Outlines are broken on models after import  
Characters with four components not supported  
Some shading issues  


Version 1 Initial Release (June 18, 2022)

Features:  
Functional model exporter/importer using 3dmigoto for genshin impact  
Able to remove and modify mesh data, including vertices, edges and textures  
Added guides on how to use the program and modify data  

Issues:  
Limited characters currently supported  
Restricted to the original number of edges and vertices  
Textures can bleed between different components (e.g. head/body)  
Third component on some characters unsupported   
