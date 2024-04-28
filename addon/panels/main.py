import bpy
from bpy.props import PointerProperty, StringProperty
from bpy.types import Collection, Context, Object, Operator, Panel
from bpy.utils import register_class, unregister_class

from ..constants import CharacterProperties, SceneProperties


COLLECTIONS = {
    CharacterProperties.BODY_COLLECTION.value : "Body",
    CharacterProperties.OUTFITS_COLLECTION.value : "Outfits",
    CharacterProperties.HAIR_COLLECTION.value : "Hair",
    CharacterProperties.PHYSICS_COLLECTION.value : "Physics"
}


class OPS_OT_AddCollection(Operator):
    bl_idname = "character_ui.add_object_collection"
    bl_label = ""
    bl_description = ""
    bl_options = {"INTERNAL"}
    collection_type: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context: Context):
        self.layout.prop(context.scene, SceneProperties.COLLECTION.value)
      

    def execute(self, context):
        o:Object | None = context.scene[SceneProperties.OBJECT.value]
        coll = context.scene[SceneProperties.COLLECTION.value]
        if not o or not coll: 
            self.report({"ERROR"}, 'You must select a collection')
            return {'CANCELLED'}
        o[self.collection_type] = coll
        context.scene[SceneProperties.COLLECTION.value] = None
        return {'FINISHED'}


class OPS_OT_RemoveCollection(Operator):
    bl_idname = "character_ui.remove_object_collection"
    bl_label = "Remove collection"
    bl_description = "Remove collection"
    bl_options = {"INTERNAL"}
    collection_type: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context):
        key = self.collection_type
        o:Object | None = context.scene[SceneProperties.OBJECT.value]
        
        if not key or not o: return {'CANCELLED'}
        
        del o[key]

        return {'FINISHED'}



class VIEW3D_PT_character_ui_main(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Setup"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        row = box.row(align=True)
        row.prop(context.scene, SceneProperties.OBJECT.value)
        row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "character_ui_object"
        
        o: Object | None = context.scene[SceneProperties.OBJECT.value]
        if(not o): return

        collections = box.box()
        collections.label(text="Collections")
        
        if CharacterProperties.CHARACTER_ID.value not in o: 
            return collections.label(
                    text="You must generate the ID first before you can continue!", icon="ERROR")

        for key, value in COLLECTIONS.items():
            if key not in o:
                collections.operator(OPS_OT_AddCollection.bl_idname, text="Add %s collection"%(value)).collection_type = key
            else:
                row = collections.row(align=True)
                row.prop(o, "[\"%s\"]"%(key), text=value)
                row.operator(OPS_OT_RemoveCollection.bl_idname, icon="X", text="").collection_type = key

modules = [
    OPS_OT_AddCollection,
    OPS_OT_RemoveCollection,
    VIEW3D_PT_character_ui_main
]


def register():
    setattr(bpy.types.Scene, SceneProperties.OBJECT.value, PointerProperty(
        name="Character UI Object",
        description="Which object is going to be used as the main Character UI object",
        type=Object,
    ))
    setattr(bpy.types.Scene, SceneProperties.COLLECTION.value, PointerProperty(
        name="Collection",
        type=Collection
    ))
   
    for m in modules:
        register_class(m)


def unregister():
    delattr(bpy.types.Scene, SceneProperties.OBJECT.value)
    delattr(bpy.types.Scene, SceneProperties.COLLECTION.value)
   
    for m in reversed(modules):
        unregister_class(m)

