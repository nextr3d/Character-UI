import random
import string
import bpy
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_GenerateID(Operator):
    bl_idname = 'characterui_generate.generate_id'
    bl_label = 'Generate random ID'
    bl_description = 'Generates random ID to identify the character, if one exists it will be overwritten!'

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        data = context.scene.character_ui_object.data
        # use character_id as the default key
        key = context.scene.character_ui_object_id if context.scene.character_ui_object_id else "character_id"
        data[key] = ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(16))
        self.report({"INFO"}, "Generated new ID: %s" % (data[key]))
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
            box.label(text="Generate UI for %s" % (o.name))
            box.prop(context.scene, "character_ui_object_id")

            row = box.row()
            row.operator(OPS_OT_GenerateID.bl_idname)
            if context.scene.character_ui_object_id in o.data:
                character_id_key = context.scene.character_ui_object_id
                character_id = o.data[character_id_key]
                rig_layers_key = context.scene.character_ui_rig_layers_key
                always_show = context.scene.character_ui_always_show

                row.label(text="Rig ID: %s" % (character_id))
                visual_box = box.box()
                visual_box.label(text="UI Settings")
                row = visual_box.row(align=True)

                row.prop(context.scene, "character_ui_custom_label")
                row.prop(context.scene, "character_ui_always_show", toggle=True)
                if "character_ui_generation_date" in o.data:
                    row_disabled = visual_box.row()
                    row_disabled.enabled = False
                    row_disabled.prop(o.data, '["character_ui_generation_date"]', text="UI Generation date", icon="TIME")
                if "character_ui_char_version" in o.data:
                    visual_box.prop(o.data, '["character_ui_char_version"]', text="Version", icon="BLENDER")

                op = box.operator("characterui_generate.generate_script")
                op.character_id = character_id
                op.character_id_key = character_id_key
                op.rig_layers_key = rig_layers_key
                op.always_show = always_show

        else:
            box.label(text="You have to select an object!", icon="ERROR")


classes = (
    OPS_OT_GenerateID,
    VIEW3D_PT_character_ui_generate
)


def register():
    bpy.types.Scene.character_ui_object_id = StringProperty(
        name="Custom Property Name",
        description="Custom Property used for storing the Character UI ID, if your character has a unique ID you can use it too",
        default="character_id",
    )
    bpy.types.Scene.character_ui_custom_label = StringProperty(
        name="Label",
        description="Text used as the label for the tab in the Sidebar"
    )
    bpy.types.Scene.character_ui_always_show = BoolProperty(
        name="Always Show",
        default=False,
        description="Always show the UI panel instead of hiding it when the character is not selected"
    )
    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_object_id
    del bpy.types.Scene.character_ui_custom_label
    del bpy.types.Scene.character_ui_always_show

    for c in reversed(classes):
        unregister_class(c)
