import bpy
from bpy.types import (Panel, PropertyGroup)
from bpy.props import (PointerProperty)
from bpy.utils import (register_class, unregister_class)


class CharacterUIPhysicsUpdates:
    @staticmethod
    def update_physics_class(self, context):
        ch = context.scene.character_ui_object
        if ch:
            if "character_ui_cages" not in ch.data:
                ch.data["character_ui_cages"] = {"collection": None}
            ch.data["character_ui_cages"]["collection"] = context.scene.character_ui_physics_collection

class VIEW3D_PT_character_ui_physics(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Physics"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "character_ui_physics_collection")
        collection = context.scene.character_ui_physics_collection
        if collection:
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
            render_meshes([*collection.children, *collection.objects])
        else:
            layout.label(text="No collection has been chosen", icon="ERROR")
classes = [
    VIEW3D_PT_character_ui_physics
]   

def register():
    bpy.types.Scene.character_ui_physics_collection = PointerProperty(
        name="Physics Collection",
        description="Collection holding all of the mesh deform cages, for consistency should have the characters name in it as a prefix for example",
        type=bpy.types.Collection,
        update=CharacterUIPhysicsUpdates.update_physics_class
    )
    for c in classes:
        register_class(c)

def unregister():
    for c in reversed(classes):
        unregister_class(c)
