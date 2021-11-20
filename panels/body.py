import bpy
from bpy.types import (Panel)
from bpy.props import (IntProperty)
from bpy.utils import (register_class, unregister_class)


class VIEW3D_PT_character_ui_body(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Body"
    bl_idname = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        body = context.scene.character_ui_object_body
        return body and hasattr(body, "modifiers")

    def draw(self, context):
        pass


class VIEW3D_PT_character_ui_shape_keys(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Shape Keys"
    bl_idname = "VIEW3D_PT_character_ui_shape_keys"
    bl_parent_id = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]
        return context.scene.character_ui_object_body.type == "MESH" and hasattr(body.data.shape_keys, "key_blocks")

    def draw(self, context):
        layout = self.layout
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]
        layout.template_list("MESH_UL_shape_keys", "", ch.data["body_object"].data.shape_keys,
                             "key_blocks", context.scene, "character_ui_active_shape_key_index")
        shape_key_name = body.data.shape_keys.key_blocks[
            context.scene.character_ui_active_shape_key_index].name
        op = layout.operator("character_ui.use_as_deformer",
                             text="Use %s as deformer" % (shape_key_name), emboss=True)
        op.shape_key = shape_key_name


class VIEW3D_PT_character_ui_masks(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Masks"
    bl_idname = "VIEW3D_PT_character_ui_masks"
    bl_parent_id = "VIEW3D_PT_character_ui_body"

    @classmethod
    def poll(self, context):
        return context.scene.character_ui_object_body.type == "MESH"

    def draw(self, context):
        pass


class VIEW3D_PT_character_ui_masks_masks(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Masks modifiers"
    bl_idname = "VIEW3D_PT_character_ui_masks_masks"
    bl_parent_id = "VIEW3D_PT_character_ui_masks"

    def draw(self, context):
        layout = self.layout
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]
        for m in body.modifiers:
            if m.type in ["MASK", "VERTEX_WEIGHT_MIX"]:
                op = layout.operator("character_ui.use_as_mask", text=m.name)
                op.modifier = m.name


class VIEW3D_PT_character_ui_masks_other(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Other modifiers"
    bl_idname = "VIEW3D_PT_character_ui_masks_other"
    bl_parent_id = "VIEW3D_PT_character_ui_masks"

    def draw(self, context):
        layout = self.layout
        ch = context.scene.character_ui_object
        body = ch.data["body_object"]
        for m in body.modifiers:
            if m.type not in ["MASK", "VERTEX_WEIGHT_MIX"]:
                op = layout.operator("character_ui.use_as_mask", text=m.name)
                op.modifier = m.name


classes = [
    VIEW3D_PT_character_ui_body,
    VIEW3D_PT_character_ui_masks,
    VIEW3D_PT_character_ui_shape_keys,
    VIEW3D_PT_character_ui_masks_masks,
    VIEW3D_PT_character_ui_masks_other
]


def register():
    bpy.types.Scene.character_ui_active_shape_key_index = IntProperty()
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
