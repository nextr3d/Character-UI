import bpy
from bpy.types import (Collection, Operator, Object, Scene)
from bpy.props import (PointerProperty, StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)
from ..constants import  SceneProperties, CharacterProperties


class OPS_OT_MoveLooseObjects(Operator):
    bl_idname = "character_ui.move_unassigned_objects"
    bl_label = "Move unassigned objects"
    bl_description = "Moves objects from the main outfits collection to outfit collection"
    bl_options = {"INTERNAL"}

    outfit_name : StringProperty(name="New Outfit Name", description="Name of the outfit")
    existing_new : BoolProperty(name="New Outfit", description="Create new collection with the set name", default=False)

    def invoke(self, context, event):
        if not hasattr(context.scene, SceneProperties.OBJECT.value): return False

        o: Object | None = context.scene[SceneProperties.OBJECT.value]
        wm = context.window_manager
        
        return wm.invoke_props_dialog(self, width=450) if o and CharacterProperties.OUTFITS_COLLECTION.value in o else False

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "existing_new", toggle=True)
        if self.existing_new:
            layout.prop(self, "outfit_name")
        else:
            layout.prop(context.scene, "character_ui_unassigned_objects_outfit")



    def execute(self, context):
        o: Object = context.scene[SceneProperties.OBJECT.value]
        outfits_collection: Collection = o[CharacterProperties.OUTFITS_COLLECTION.value]

        if self.outfit_name not in ["", " "] or context.scene.character_ui_unassigned_objects_outfit:
            coll = None
            if self.existing_new:
                coll = bpy.data.collections.new(self.outfit_name)
                outfits_collection.children.link(coll)
            else:
                coll = context.scene.character_ui_unassigned_objects_outfit
            loose_objects = outfits_collection.objects
            for loose_object in loose_objects:
                outfits_collection.objects.unlink(loose_object)
                coll.objects.link(loose_object)
            self.report({"INFO"}, "Created %s and moved loose objects"%(coll.name))
        return {"FINISHED"}

def poll(self: Scene, coll: Collection):
    """Check if collection is a child of Character UI Outfits Collection"""
    
    if not hasattr(self, SceneProperties.OBJECT.value): return False

    o: Object | None = self[SceneProperties.OBJECT.value]
    outfits_key = CharacterProperties.OUTFITS_COLLECTION.value

    return o and outfits_key in o and coll.name in o[outfits_key].children

classes = [
    OPS_OT_MoveLooseObjects
]


def register():
    bpy.types.Scene.character_ui_unassigned_objects_outfit = PointerProperty(
        name="Outfit",
        description="Select existing outfit which will receive unassigned objects",
        type=bpy.types.Collection,
        poll=poll
    )
    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_unassigned_objects_outfit
    for c in reversed(classes):
        unregister_class(c)
