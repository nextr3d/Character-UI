import bpy
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy.props import (PointerProperty, StringProperty,
                       BoolProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)


class CharacterUIRigLayerUpdates():
    @staticmethod
    def update_rig_layer_key(self, context):
        key = context.scene.character_ui_rig_layers_key
        o = context.scene.character_ui_object
        for i in range(32):
            visible = False
            name = ""
            row = i + 1
            if key in o.data:
                if len(o.data[key][i]["name"][:1]) > 0:
                    visible = not o.data[key][i]["name"][:1] == "$"
                    name = o.data[key][i]["name"] if visible else o.data[key][i]["name"][1:]
                    row = o.data[key][i]["row"] + 1

            context.scene["character_ui_row_visible_%i" % (i)] = visible
            context.scene["character_ui_row_name_%i" % (i)] = name
            context.scene["character_ui_row_index_%i" % (i)] = row


class VIEW3D_PT_character_ui_rig_layers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Rig Layers"
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="")
        row = self.layout.row(align=True)
        row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "character_ui_rig_layers"

    @classmethod
    def poll(self, context):
        ch = context.scene.character_ui_object
        return ch and ch.type == "ARMATURE"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Rig Layers")
        ch = context.scene.character_ui_object
        if ch:
            if ch.type == "ARMATURE":
                active_bcoll = ch.data.collections.active

                row = layout.row()
                row.template_bone_collection_tree()

                col = row.column(align=True)
                col.operator("armature.collection_add", icon='ADD', text="")
                col.operator("armature.collection_remove", icon='REMOVE', text="")

                col.separator()

                col.menu("ARMATURE_MT_collection_context_menu", icon='DOWNARROW_HLT', text="")

                if active_bcoll:
                    col.separator()
                    col.operator("armature.collection_move", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("armature.collection_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

                row = layout.row()

                sub = row.row(align=True)
                sub.operator("armature.collection_assign", text="Assign")
                sub.operator("armature.collection_unassign", text="Remove")

                sub = row.row(align=True)
                sub.operator("armature.collection_select", text="Select")
                sub.operator("armature.collection_deselect", text="Deselect")

            else:
                box.label(text="Object is not an armature", icon="ERROR")
        else:
            box.label(text="You have to select an object!", icon="ERROR")


def character_ui_generate_rig_layers(self, context):
    "generates UI rig layers for the UI"
    ch = context.scene.character_ui_object
    key = context.scene.character_ui_rig_layers_key
    if ch and key:
        ch.data[key] = []
        layers = []
        for i in range(32):
            row = i
            if "character_ui_row_index_%i" % (i) in context.scene:
                row = context.scene["character_ui_row_index_%i" % (i)] - 1
            name = "Layer "+str(i+1)
            if "character_ui_row_name_%i" % (i) in context.scene:
                if context.scene["character_ui_row_name_%i" % (i)] not in ["", " "]:
                    name = context.scene["character_ui_row_name_%i" % (i)]

            if "character_ui_row_visible_%i" % (i) in context.scene:
                if not context.scene["character_ui_row_visible_%i" % (i)]:
                    name = "$%s" % (name)
            else:
                name = "$%s" % (name)

            layers.insert(i, {'name': name, "row": row})
        ch.data[key] = layers


classes = [
    VIEW3D_PT_character_ui_rig_layers
]


def register():
    bpy.types.Scene.character_ui_rig_layers_key = StringProperty(
        name="Rig Layers Key", default="rig_layers", update=CharacterUIRigLayerUpdates.update_rig_layer_key)
    for i in range(32):
        setattr(bpy.types.Scene, "character_ui_row_visible_%i" % (i),
                BoolProperty(name="", update=character_ui_generate_rig_layers))
        setattr(bpy.types.Scene, "character_ui_row_name_%i" % (
            i), StringProperty(name="", update=character_ui_generate_rig_layers))
        setattr(bpy.types.Scene, "character_ui_row_index_%i" % (i), IntProperty(
            name="UI Row", min=1, max=32, default=i+1, update=character_ui_generate_rig_layers))

    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_rig_layers_key
    for i in range(32):
        delattr(bpy.types.Scene, "character_ui_row_visible_%i" % (i))
        delattr(bpy.types.Scene, "character_ui_row_name_%i" % (i))
        delattr(bpy.types.Scene, "character_ui_row_index_%i" % (i))

    for c in reversed(classes):
        unregister_class(c)
