import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_FormatOutfitPieceName(Operator):
    bl_idname = "character_ui.format_outfit_piece_name"
    bl_label = "Format Outfit Piece name"
    bl_description = "Format the label of outfit piece"
    bl_options = {"INTERNAL"}


    prefix : StringProperty(name="Prefix", description="If the outfit piece contains this prefix it will remove it for the buttons in the generated UI.")
    whole_outfit : BoolProperty(default=True)

    def invoke(self, context, event):
        if self.whole_outfit:
            return context.window_manager.invoke_props_dialog(self, width=350)
        return

    def execute(self, context):
        outfit_collection = context.scene.character_ui_outfits_collection.children[context.scene.character_ui_active_outfit_index]
        if self.whole_outfit:
            for o in outfit_collection.objects:
                format_name(o, self.prefix)
        l = len(outfit_collection.objects)
        self.report({"INFO"}, "Changed format of %i outfit piece%s"%(l, "s" if l > 1 else ""))
        
        return {"FINISHED"}
    def draw(self, context):
        self.layout.prop(self, "prefix");

   
def format_name(outfit_piece, prefix):
    if "chui_outfit_piece_settings"not in outfit_piece:
        outfit_piece["chui_outfit_piece_settings"] = {}
    outfit_piece["chui_outfit_piece_settings"]["prefix"] = prefix


classes = [
    OPS_OT_FormatOutfitPieceName
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
