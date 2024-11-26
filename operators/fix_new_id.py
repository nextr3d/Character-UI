import bpy
from bpy.types import (Operator)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_FixNewId(Operator):
    bl_idname = "character_ui.fix_new_id"
    bl_label = "Fix"
    bl_description = "After new id has been generated outside of Character UI's control you need to fix the character."
    bl_options = {"INTERNAL"}

    def execute(self, context):
        ch = context.scene.character_ui_object
        if "hair_collection" not in ch.data:
            ch.data["hair_collection"] = context.scene.character_ui_hair_collection
        if "outfits_collection" not in ch.data:
            ch.data["outfits_collection"] = context.scene.character_ui_outfits_collection
        if "character_ui_cages" not in ch.data:
            ch.data["character_ui_cages"] = {}
        if "collection" not in ch.data["character_ui_cages"]:
            ch.data["character_ui_cages"]["collection"] = context.scene.character_ui_physics_collection

        character_id_key = context.scene.character_ui_object_id
        character_id = ch.data[character_id_key]
        context.scene.character_ui_object_id_value = character_id
        self.report({"INFO"}, "Fixed character")

        return {"FINISHED"}


classes = [
    OPS_OT_FixNewId
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
