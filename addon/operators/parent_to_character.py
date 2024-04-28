import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, EnumProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_ParentToCharacter(Operator):
    bl_idname = "character_ui.parent_to_character"
    bl_label = "Parent to the Character UI Object"
    bl_description = "Parents all of the outfit pieces from the current outfit to the Character UI Object."
    bl_options = {"INTERNAL"}


    def execute(self, context):
        outfit_collection = context.scene.character_ui_outfits_collection.children[context.scene.character_ui_active_outfit_index]
        chr = context.scene.character_ui_object
        no_parent = 0
        for o in outfit_collection.objects:
            if not o.parent:
                no_parent += 1
                o.parent = chr
        self.report({'INFO'}, "Parented all (%i) of outfit pieces to the character (%s)"%(no_parent, chr.name))
        return {"FINISHED"}


classes = [
    OPS_OT_ParentToCharacter
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
