import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_UseAsDeformer(Operator):
    bl_idname = "character_ui.use_as_deformer"
    bl_label = "Select object to trigger shape key change for:"
    bl_description = "Sets the shape key to be toggled on/off based on an outfit piece"

    shape_key: StringProperty()

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        context.scene.character_ui_shape_key_outfit_piece = None
        if "character_ui_shape_keys" in ch.data:
            for item in ch.data["character_ui_shape_keys"]:
                if item["shape_key"] == self.shape_key:
                    context.scene.character_ui_shape_key_outfit_piece = item["driver_id"] 
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        ch = context.scene.character_ui_object
        shape_key_name = ch.data["body_object"].data.shape_keys.key_blocks[self.shape_key].name
        self.layout.label(text=shape_key_name)
        self.layout.prop(context.scene, 'character_ui_shape_key_outfit_piece')

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            found = False
            outfit_piece = context.scene.character_ui_shape_key_outfit_piece
            shape_key_name = ch.data["body_object"].data.shape_keys.key_blocks[self.shape_key].name
            if "character_ui_shape_keys" not in ch.data:
                ch.data["character_ui_shape_keys"] = []
            for item in ch.data["character_ui_shape_keys"]:
                if item["shape_key"] == shape_key_name:
                    item["driver_id"] = outfit_piece 
                    found = True
            if not found:
                shape_keys = []
                try:
                    shape_keys = ch.data["character_ui_shape_keys"].to_list()
                except:
                    shape_keys = ch.data["character_ui_shape_keys"]
                shape_keys.append({"shape_key": shape_key_name, "driver_id": outfit_piece})
                ch.data["character_ui_shape_keys"] = shape_keys
        return {"FINISHED"}
classes = [
    OPS_OT_UseAsDeformer
]
def register():
    bpy.types.Scene.character_ui_shape_key_outfit_piece = PointerProperty(type=bpy.types.Object, name="Outfit piece")

    for c in classes:
        register_class(c)
  

def unregister():
    del  bpy.types.Scene.character_ui_shape_key_outfit_piece
    for c in reversed(classes):
        unregister_class(c)

