import bpy
from bpy.types import (Panel, PropertyGroup)
from bpy.props import (PointerProperty)
from bpy.utils import (register_class, unregister_class)


class CharacterUIMainUpdates:
    @staticmethod
    def update_character_ui_object(self, context):
        if context.scene.character_ui_object:
            o = context.scene.character_ui_object
            CharacterUIMainUpdates.update_character_ui_object_collections(context, o)
            CharacterUIMainUpdates.update_character_ui_object_rig_layers(context, o)
            context.scene.character_ui_object_body = o.data["body_object"]
            context.scene.character_ui_custom_label = o.name
            if "cloud_rig" in o:
                context.scene.character_ui_object_id = "rig_id"
        else:
            context.scene.character_ui_object_body = None

    @staticmethod
    def update_character_ui_object_collections(context, o):
        outfits = None
        hair = None
        body = None
        physics = None

        if "hair_collection" in o.data:
            hair = o.data["hair_collection"]
        if "outfits_collection" in o.data:
            outfits = o.data["outfits_collection"]
        if "body_object" in o.data:
            body = o.data["body_object"]
        if "character_ui_cages" in o.data:
            if "collection" in o.data["character_ui_cages"]:
                physics = o.data["character_ui_cages"]["collection"]

        context.scene.character_ui_hair_collection = hair
        context.scene.character_ui_outfits_collection = outfits
        context.scene.character_ui_object_body = body
        context.scene.character_ui_physics_collection = physics

    @staticmethod
    def update_character_ui_object_rig_layers(context, o):
        key = context.scene.character_ui_rig_layers_key
        for i in range(31):
            visible = False
            name = ""
            row = i + 1
            if key in o:
                if len(o[key][i]["name"][:1]) > 0:
                    visible = not o[key][i]["name"][:1] == "$"
                    name = o[key][i]["name"] if visible else o[key][i]["name"][1:]
                    row = o[key][i]["row"] + 1

            context.scene["character_ui_row_visible_%i" % (i)] = visible
            context.scene["character_ui_row_name_%i" % (i)] = name
            context.scene["character_ui_row_index_%i" % (i)] = row

    @staticmethod
    def update_collections(self, context):
        if context.scene.character_ui_object:
            o = context.scene.character_ui_object
            o.data["outfits_collection"] = context.scene.character_ui_outfits_collection
            o.data["hair_collection"] = context.scene.character_ui_hair_collection

    @staticmethod
    def update_objects(self, context):
        if context.scene.character_ui_object:
            o = context.scene.character_ui_object
            o.data["body_object"] = context.scene.character_ui_object_body

    @staticmethod
    def update_physics_collection(self, context):
        ch = context.scene.character_ui_object
        if ch:
            if "character_ui_cages" not in ch.data:
                ch.data["character_ui_cages"] = {"collection": None}
            ch.data["character_ui_cages"]["collection"] = context.scene.character_ui_physics_collection


class VIEW3D_PT_character_ui_main(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Setup"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        o_row = box.row(align=True)
        o_row.prop(context.scene, "character_ui_object")
        o_row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "character_ui_object"
        ch = context.scene.character_ui_object
        if ch:
            if ch.type != "ARMATURE":
                box.label(text="Object is not an armature", icon="ERROR")
            if context.scene.character_ui_object_id in ch.data:
                collections = box.box()
                collections.label(text="Collections")
                collections.prop(
                    context.scene, "character_ui_outfits_collection")
                collections.prop(context.scene, "character_ui_hair_collection")
                collections.prop(
                    context.scene, "character_ui_physics_collection")
                objects = box.box()
                objects.label(text="Objects")
                objects.prop(context.scene, "character_ui_object_body")
            else:
                box.label(
                    text="You must generate the ID first before you can continue!", icon="ERROR")


def register():
    bpy.types.Scene.character_ui_object = PointerProperty(
        name="Character UI Object",
        description="Which object is going to be used as the main Character UI object",
        type=bpy.types.Object,
        update=CharacterUIMainUpdates.update_character_ui_object
    )
    bpy.types.Scene.character_ui_object_body = PointerProperty(
        name="Body",
        description="Which object is the Character body, leave blank if no body",
        type=bpy.types.Object,
        update=CharacterUIMainUpdates.update_objects
    )
    bpy.types.Scene.character_ui_outfits_collection = PointerProperty(
        name="Outfits",
        description="Collection holding all of the outfits, for consistency should have the charactes name in it as a prefix for example",
        type=bpy.types.Collection,
        update=CharacterUIMainUpdates.update_collections
    )
    bpy.types.Scene.character_ui_hair_collection = PointerProperty(
        name="Hair",
        description="Collection holding all of the hair styles, for consistency should have the charactes name in it as a prefix for example",
        type=bpy.types.Collection,
        update=CharacterUIMainUpdates.update_collections
    )
    bpy.types.Scene.character_ui_physics_collection = PointerProperty(
        name="Physics",
        description="Collection holding all of the mesh deform cages, for consistency should have the characters name in it as a prefix for example",
        type=bpy.types.Collection,
        update=CharacterUIMainUpdates.update_physics_collection
    )
    register_class(VIEW3D_PT_character_ui_main)


def unregister():
    del bpy.types.Scene.character_ui_object
    del bpy.types.Scene.character_ui_object_body
    del bpy.types.Scene.character_ui_outfits_collection
    del bpy.types.Scene.character_ui_hair_collection
    del bpy.types.Scene.character_ui_physics_collection

    unregister_class(VIEW3D_PT_character_ui_main)
