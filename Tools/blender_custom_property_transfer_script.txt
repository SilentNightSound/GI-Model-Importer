# Author: SilentNightSound#7430
# Transfers custom properties between objects

import bpy


##### USAGE INSTRUCTIONS

# DEFAULT USAGE
# Click the object you are transferring TO first and then ctrl+click the object you are transferring FROM second
# You can transfer TO multiple objects with ctrl+click, just make sure that the object you are transferring FROM is selected last
active_obj = bpy.context.active_object
selected_obj = [obj for obj in bpy.context.selected_objects]

if len(selected_obj)>1:
    original_object = active_obj.name
    new_objects = [x.name for x in selected_obj if x.name != original_object]
 

# ORIGINAL USAGE, uncomment if needed. Overrides the above if uncommented
# Replace "transfer_to" with the name of the object(s) are are transferring properties TO, and "transfer_from" with the name of the object you are transferring properties FROM 
# new_objects = ["transfer_to"]
# original_object = "transfer_from"

#####


if not new_objects:
    print("Not enough objects selected - either select at least two objects, or manually add the names in the script")

print(new_objects, original_object)
for new_object in new_objects:
    for k in bpy.data.objects[original_object].keys():
        bpy.data.objects[new_object][k] =  bpy.data.objects[original_object][k]
