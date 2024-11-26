import bpy
from bpy.types import (Panel)
from bpy.props import (IntProperty)
from bpy.utils import (register_class, unregister_class)


class VIEW3D_PT_character_ui_outfits(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Outfits"
    bl_idname = "VIEW3D_PT_character_ui_outfits"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        collection = context.scene.character_ui_outfits_collection
        return collection

    def draw(self, context):
        layout = self.layout
        outfits_collection = context.scene.character_ui_outfits_collection
        loose_objects = outfits_collection.objects
        if len(loose_objects):
            loose_objects_box = layout.box()
            row = loose_objects_box.row()
            row.alert = True
            row.label(text="%s can't contain objects directly!"%(outfits_collection.name))
            row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "cant_contain_directly"
            loose_objects_box.operator("character_ui.move_unassigned_objects")

        active_outfit = context.scene.character_ui_active_outfit_index
        if active_outfit < len(outfits_collection.children):
            
            outfits_box = layout.box()
            outfits_label_row = outfits_box.row(align=True)
            outfits_label_row.label(text="Outfits")
            outfits_label_row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "outfits"
            outfits_box.template_list("UI_UL_list", "character_ui_outfits", outfits_collection, "children", context.scene, "character_ui_active_outfit_index")

            outfit_pieces_box = layout.box()
            outfit_pieces_box.label(text="Outfit Pieces")
            outfit_pieces_row = outfit_pieces_box.row()
            outfit_pieces_row.template_list("UI_UL_list", "character_ui_outfit_pieces", outfits_collection.children[active_outfit], "objects", context.scene, "character_ui_active_outfit_piece_index")
            outfit_pieces_row.operator("character_ui.edit_outfit_piece", text="", icon="PREFERENCES")
            outfit_pieces_box.operator("character_ui.parent_to_character")
            outfit_pieces_box.operator("character_ui.format_outfit_piece_name")

        



classes = [
    VIEW3D_PT_character_ui_outfits
]


def register():
    bpy.types.Scene.character_ui_active_outfit_index = IntProperty(name="Active outfit")
    bpy.types.Scene.character_ui_active_outfit_piece_index = IntProperty(name="Active outfit piece")
    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_active_outfit_index
    del bpy.types.Scene.character_ui_active_outfit_piece_index
    for c in reversed(classes):
        unregister_class(c)
