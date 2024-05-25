import bpy
from bpy.types import (Panel, Object)
from bpy.props import (IntProperty)
from bpy.utils import (register_class, unregister_class)
from ..constants import  SceneProperties, CharacterProperties
from enum import Enum

class OutfitSceneProperties(Enum):
    ACTIVE_OUTFIT = "character_ui_active_outfit_index"
    ACTIVE_PIECE = "character_ui_active_outfit_piece_index"



class VIEW3D_PT_character_ui_outfits(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Outfits"
    bl_idname = "VIEW3D_PT_character_ui_outfits"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, SceneProperties.OBJECT.value): return False

        o: Object | None = context.scene[SceneProperties.OBJECT.value]

        return o and CharacterProperties.OUTFITS_COLLECTION.value in o

    def draw(self, context):
        layout = self.layout
        o: Object = context.scene[SceneProperties.OBJECT.value]
        outfits_collection = o[CharacterProperties.OUTFITS_COLLECTION.value]

        if len(outfits_collection.objects):
            loose_objects_box = layout.box()
            row = loose_objects_box.row()
            row.alert = True
            row.label(text="%s can't contain objects directly!"%(outfits_collection.name))
            row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "cant_contain_directly"
            loose_objects_box.operator("character_ui.move_unassigned_objects")

        active_outfit = context.scene[OutfitSceneProperties.ACTIVE_OUTFIT.value]
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

classes = [
    VIEW3D_PT_character_ui_outfits
]

def register():
    setattr(bpy.types.Scene, OutfitSceneProperties.ACTIVE_OUTFIT.value, IntProperty(name="Active outfit"))
    setattr(bpy.types.Scene, OutfitSceneProperties.ACTIVE_PIECE.value, IntProperty(name="Active outfit piece"))
    
    for c in classes:
        register_class(c)


def unregister():
    delattr(bpy.types.Scene, OutfitSceneProperties.ACTIVE_OUTFIT.value)
    delattr(bpy.types.Scene, OutfitSceneProperties.ACTIVE_PIECE.value)

    for c in reversed(classes):
        unregister_class(c)
