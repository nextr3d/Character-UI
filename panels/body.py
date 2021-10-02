import bpy
from bpy.types import (Panel, PropertyGroup, Operator, UIList)
from bpy.props import (PointerProperty, StringProperty, BoolProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)

class VIEW3D_PT_character_ui_body(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Body"
    bl_idname = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        body = context.scene.character_ui_object_body
        return body and hasattr(body, "modifiers")

    def draw(self, context):
        pass

class VIEW3D_PT_character_ui_shape_keys(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Shape Keys"
    bl_idname = "VIEW3D_PT_character_ui_shape_keys"
    bl_parent_id = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        return context.scene.character_ui_object_body.type == "MESH"

    def draw(self, context):
        layout = self.layout
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]       
        
        layout.template_list("MESH_UL_shape_keys", "", ch.data["body_object"].data.shape_keys,
                          "key_blocks", context.scene, "character_ui_active_shape_key_index")
        op = layout.operator("character_ui.use_as_deformer", text="Use as deformer")
        op.shape_key = context.scene.character_ui_active_shape_key_index
class VIEW3D_PT_character_ui_masks(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Masks"
    bl_idname = "VIEW3D_PT_character_ui_masks"
    bl_parent_id = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        return context.scene.character_ui_object_body.type == "MESH"

    def draw(self, context):
        layout = self.layout
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]
        for m in body.modifiers:
            op = layout.operator("character_ui.use_as_mask", text=m.name)
            op.modifier = m.name

classes = [
    VIEW3D_PT_character_ui_body,
    VIEW3D_PT_character_ui_masks,
    VIEW3D_PT_character_ui_shape_keys
]

def register():
    bpy.types.Scene.character_ui_active_shape_key_index = IntProperty()
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

