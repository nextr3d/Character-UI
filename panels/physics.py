import bpy
from bpy.types import (Panel, PropertyGroup)
from bpy.props import (PointerProperty)
from bpy.utils import (register_class, unregister_class)

class VIEW3D_PT_character_ui_physics(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Physics"

    @classmethod
    def poll(self, context):
        collection = context.scene.character_ui_physics_collection
        return collection != None

    def draw(self, context):
        layout = self.layout
        collection = context.scene.character_ui_physics_collection
        def render_meshes(items):
            for i in items:
                if hasattr(i, "type"):
                    if i.type == "MESH":
                        for m in i.modifiers:
                            if m.type == "CLOTH":
                                op = layout.operator("character_ui.use_as_cage", text=i.name)
                                op.cage = i.name
                                
                else:
                    render_meshes([*i.children, *i.objects])
        objects_to_render = [*collection.children, *collection.objects]
        if len(objects_to_render):
            render_meshes(objects_to_render)
        else:
            layout.label(text="Collection has no objects or children collections", icon="ERROR")
classes = [
    VIEW3D_PT_character_ui_physics
]   

def register():
    for c in classes:
        register_class(c)

def unregister():
    for c in reversed(classes):
        unregister_class(c)
