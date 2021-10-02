import bpy
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)

class VIEW3D_PT_character_ui_body(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Body"

    @classmethod
    def poll(self, context):
        body = context.scene.character_ui_object_body
        return body and hasattr(body, "modifiers")

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Masks", icon="MOD_MASK")
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]

        for m in body.modifiers:
            op = box.operator("character_ui.use_as_mask", text=m.name)
            op.modifier = m.name
      

classes = [
    VIEW3D_PT_character_ui_body
]

def register():
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

