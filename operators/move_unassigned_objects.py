import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_MoveLooseObjects(Operator):
    bl_idname = "character_ui.move_unassigned_objects"
    bl_label = "Move unassigned objects"
    bl_description = "Moves objects from the main outfits collection to outfit collection"
    bl_options = {"INTERNAL"}

    outfit_name : StringProperty(name="New Outfit Name", description="Name of the outfit")
    existing_new : BoolProperty(name="New Outfit", description="Create new collection with the set name", default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "existing_new", toggle=True)
        if self.existing_new:
            layout.prop(self, "outfit_name")
        else:
            layout.prop(context.scene, "character_ui_unassigned_objects_outfit")



    def execute(self, context):
        outfits_collection = context.scene.character_ui_outfits_collection
        if self.outfit_name not in ["", " "] or context.scene.character_ui_unassigned_objects_outfit:
            coll = None
            if self.existing_new:
                coll = bpy.data.collections.new(self.outfit_name)
                context.scene.character_ui_outfits_collection.children.link(coll)
            else:
                coll = context.scene.character_ui_unassigned_objects_outfit
            loose_objects = outfits_collection.objects
            for o in loose_objects:
                outfits_collection.objects.unlink(o)
                coll.objects.link(o)
            self.report({"INFO"}, "Created %s and moved loose objects"%(coll.name))
        return {"FINISHED"}

def poll(self, obj):
    return obj.name in self.character_ui_outfits_collection.children
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
