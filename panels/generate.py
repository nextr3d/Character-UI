import random
import string
import bpy
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy.props import (PointerProperty, StringProperty)
from bpy.utils import (register_class, unregister_class)

class OPS_OT_GenerateID(Operator):
    bl_idname = 'characterui_generate.generate_id'
    bl_label = 'Generate random ID'
    bl_description = 'Generates random ID to identify the character, if one exists it will be overwritten!'

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        data = context.scene.character_ui_object.data
        key = context.scene.character_ui_object_id if context.scene.character_ui_object_id else "character_id" #use character_id as the default key
        data[key] = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
        self.report({"INFO"}, "Generated new ID: %s"%(data[key]))
        return {"FINISHED"}

class VIEW3D_PT_character_ui_generate(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Generate"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        if context.scene.character_ui_object:
            o = context.scene.character_ui_object
            box.label(text="Generate UI for %s"%(o.name))
            box.prop(context.scene, "character_ui_object_id")
            row = box.row()

            row.operator(OPS_OT_GenerateID.bl_idname)
            if context.scene.character_ui_object_id in o.data:
                character_id_key = context.scene.character_ui_object_id
                character_id = o.data[character_id_key]
                rig_layers_key = context.scene.character_ui_rig_layers_key
                row.label(text="Rig ID: %s"%(character_id))
                op = box.operator("characterui_generate.generate_script")
                op.character_id = character_id
                op.character_id_key = character_id_key
                op.rig_layers_key = rig_layers_key


        else:
            box.label(text="You have to select an object!", icon="ERROR")
classes = (
    OPS_OT_GenerateID,
    VIEW3D_PT_character_ui_generate
)
def register():
    bpy.types.Scene.character_ui_object_id = StringProperty(
        name = "Custom Property Name",
        description = "Custom Property used for storing the Character UI ID, if your character has a unique ID you can use it too",
        default = "character_id",
    )
    for c in classes:
        register_class(c)
  

def unregister():
    del bpy.types.Scene.character_ui_object_id
    for c in reversed(classes):
        unregister_class(c)

