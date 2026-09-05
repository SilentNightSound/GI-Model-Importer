import bpy

def select_all_vertex_groups_and_delete():
    # Get the active object (the one currently selected/active)
    obj = bpy.context.active_object

    # Make sure the object is in Edit Mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all elements in Edit Mode
    bpy.ops.mesh.select_all(action='DESELECT')

    # Select all vertex groups
    for vg in obj.vertex_groups:
        bpy.ops.object.vertex_group_set_active(group=vg.name)
        bpy.ops.object.vertex_group_select()

    # Invert the selection
    bpy.ops.mesh.select_all(action='INVERT')

    # Delete the selected vertices
    bpy.ops.mesh.delete(type='VERT')

# Call the function to select all vertex groups and delete the selected vertices
select_all_vertex_groups_and_delete()
