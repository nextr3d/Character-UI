import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, EnumProperty)
from bpy.utils import (register_class, unregister_class)
from . import format_outfit_piece_name

class OPS_OT_EditOutfitPiece(Operator):
    bl_idname = "character_ui.edit_outfit_piece"
    bl_label = "Edit Outfit Piece"
    bl_description = "Set outfit piece properties"
    bl_options = {"INTERNAL"}

    prefix : StringProperty(name="Prefix", description="If the outfit piece contains this prefix it will remove it for the buttons in the generated UI.")


    def invoke(self, context, event):
        outfit_collection = context.scene.character_ui_outfits_collection.children[context.scene.character_ui_active_outfit_index]
        outfit_piece_index = context.scene.character_ui_active_outfit_piece_index
        if outfit_piece_index < len(outfit_collection.objects):
            outfit_piece = outfit_collection.objects[outfit_piece_index]
            context.scene.character_ui_outfit_piece_parent = outfit_piece.parent
            if "chui_outfit_piece_settings" in outfit_piece:
                if "prefix" in outfit_piece["chui_outfit_piece_settings"]:
                    self.prefix =  outfit_piece["chui_outfit_piece_settings"]["prefix"]
            return context.window_manager.invoke_props_dialog(self, width=350)
        return {"FINISHED"}


    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(context.scene, "character_ui_outfit_piece_parent")
        row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "outfit_piece_parent"

        toggle_box = layout.box()
        toggle_box.label(text="UI toggle style")
        toggle_box.prop(self, "prefix")


    def execute(self, context):
        outfit_collection = context.scene.character_ui_outfits_collection.children[context.scene.character_ui_active_outfit_index]
        outfit_piece = outfit_collection.objects[context.scene.character_ui_active_outfit_piece_index]
        outfit_piece.parent = context.scene.character_ui_outfit_piece_parent
        format_outfit_piece_name.format_name(outfit_piece, self.prefix)
        return {"FINISHED"}


classes = [
    OPS_OT_EditOutfitPiece
]


def register():
    bpy.types.Scene.character_ui_outfit_piece_parent = PointerProperty(
        name="Parent",
        description="Parent of the outfit piece",
        type=bpy.types.Object)
    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_outfit_piece_parent
    for c in reversed(classes):
        unregister_class(c)
