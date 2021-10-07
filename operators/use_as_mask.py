import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_UseAsMask(Operator):
    bl_idname = "character_ui.use_as_mask"
    bl_label = "Select object to trigger mask change for:"
    bl_description = "Sets the modifier to be toggled on/off based on an outfit piece"

    modifier: StringProperty()

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        context.scene.character_ui_mask_outfit_piece = None
        if "character_ui_masks" in ch.data:
            for item in ch.data["character_ui_masks"]:
                if item["modifier"] == self.modifier:
                    context.scene.character_ui_mask_outfit_piece = item["driver_id"] 
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        self.layout.label(text=self.modifier)
        self.layout.prop(context.scene, 'character_ui_mask_outfit_piece')

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            new_masks = []
            found = False
            outfit_piece = context.scene.character_ui_mask_outfit_piece
            if "character_ui_masks" not in ch.data:
                ch.data["character_ui_masks"] = []
            for item in ch.data["character_ui_masks"]:
                if item["modifier"] == self.modifier:
                    item["driver_id"] = outfit_piece 
                    found = True
            if not found:
                masks = ch.data["character_ui_masks"].to_list()
                masks.append({"modifier": self.modifier, "driver_id": outfit_piece})
                ch.data["character_ui_masks"] = masks
        return {"FINISHED"}
classes = [
    OPS_OT_UseAsMask
]
def register():
    bpy.types.Scene.character_ui_mask_outfit_piece = PointerProperty(type=bpy.types.Object, name="Outfit piece")

    for c in classes:
        register_class(c)
  

def unregister():
    del bpy.types.Scene.character_ui_mask_outfit_piece
    for c in reversed(classes):
        unregister_class(c)

