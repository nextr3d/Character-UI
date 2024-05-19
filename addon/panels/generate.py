import random
import string
from ..constants import CharacterProperties, SceneProperties
import bpy
from bpy.types import (Object, Panel, Operator)
from bpy.props import (BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_GenerateID(Operator):
    bl_idname = 'characterui_generate.generate_id'
    bl_label = 'Generate random ID'
    bl_description = 'Generates random ID to identify the character, if one exists it will be overwritten!'

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        o = context.scene[SceneProperties.OBJECT.value]
        id =''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(16))
        o[CharacterProperties.CHARACTER_ID.value] = id
        o[CharacterProperties.CHARACTER_LABEL.value] = o.name
        self.report({"INFO"}, "Generated new ID: %s" % (id))
        return {"FINISHED"}


class VIEW3D_PT_character_ui_generate(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Generate"



    def draw(self, context):
        layout = self.layout
        box = layout.box()
        o: Object | None = context.scene[SceneProperties.OBJECT.value]
        if not o:
            return  box.label(text="You have to select an object!", icon="ERROR")

        box.label(text="Generate UI for %s" % (o.name))
        row = box.row(align=True)
        if CharacterProperties.CHARACTER_ID.value not in o:
            row.operator(OPS_OT_GenerateID.bl_idname)
        else:
            row.prop(o, "[\"%s\"]"%(CharacterProperties.CHARACTER_ID.value), text="Character UI ID")
        row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "chui_id"
       

           

classes = (
    OPS_OT_GenerateID,
    VIEW3D_PT_character_ui_generate
)


def register():
    setattr(bpy.types.Scene, SceneProperties.ALWAYS_SHOW.value, BoolProperty(name='Always show', description="Always show the UI, if set to false the UI is going to be visible only when the active object is a Character UI object"))
   
    for c in classes:
        register_class(c)


def unregister():
    delattr(bpy.types.Scene, SceneProperties.ALWAYS_SHOW.value)

    for c in reversed(classes):
        unregister_class(c)
