import bpy
from bpy.types import (Operator, Object)
from bpy.props import (PointerProperty, StringProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_AddObjectAsMask(Operator):
    bl_idname = "character_ui.add_object_as_mask"
    bl_label = "Add object"
    bl_description = "Adds selected object to the mask modifer"

    modifier: StringProperty()

    @classmethod
    def poll(self, context):
        return context.scene.character_ui_mask_outfit_piece != None

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            found = False
            outfit_piece = context.scene.character_ui_mask_outfit_piece
            if "character_ui_masks" not in ch.data:
                ch.data["character_ui_masks"] = []
            for item in ch.data["character_ui_masks"]:
                if item["modifier"] == self.modifier:
                    if type(item["driver_id"]) == Object:
                        o = item["driver_id"]
                        item["driver_id"] = [o, outfit_piece]
                    else:
                        try:
                            new_items = item["driver_id"]
                            new_items.append(outfit_piece)
                            item["driver_id"] = new_items
                        except:
                            new_items = item["driver_id"].to_list()
                            new_items.append(outfit_piece)
                            item["driver_id"] = new_items
                    found = True

            if not found:
                masks = []
                try:
                    masks = ch.data["character_ui_masks"].to_list()
                except:
                    masks = ch.data["character_ui_masks"]
                masks.append({"modifier": self.modifier,
                             "driver_id": [outfit_piece]})
                ch.data["character_ui_masks"] = masks
            self.report({'INFO'}, "Added %s to %s" % (outfit_piece.name, self.modifier))
        context.scene.character_ui_mask_outfit_piece = None

        return {'FINISHED'}


class OPS_OT_RemoveObjectAsMask(Operator):
    bl_idname = "character_ui.remove_object_as_mask"
    bl_label = "Remove object"
    bl_description = "Removes object from the mask modifier"

    modifier: StringProperty()
    removed_object: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            found = False
            outfit_piece = context.scene.character_ui_mask_outfit_piece
            for item in ch.data["character_ui_masks"]:
                if item["modifier"] == self.modifier:
                    if type(item["driver_id"]) == Object:
                        item["driver_id"] = []
                    else:
                        new_drivers = []
                        for o in item["driver_id"]:
                            if o.name != self.removed_object:
                                new_drivers.append(o)
                        item["driver_id"] = new_drivers
        self.report({'INFO'}, "Removed %s from %s" % (self.removed_object, self.modifier))

        return {'FINISHED'}


class OPS_OT_UseAsMask(Operator):
    bl_idname = "character_ui.use_as_mask"
    bl_label = "Select object to trigger mask change for:"
    bl_description = "Sets the modifier to be toggled on/off based on an outfit piece"

    modifier: StringProperty()

    def invoke(self, context, event):
        context.scene.character_ui_mask_outfit_piece = None
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        self.layout.label(text=self.modifier)
        box = self.layout.box()
        box.label(text="Objects", icon="OUTLINER_OB_MESH")
        ch = context.scene.character_ui_object
        if ch:
            found = False
            outfit_piece = context.scene.character_ui_mask_outfit_piece
            if "character_ui_masks" in ch.data:
                for item in ch.data["character_ui_masks"]:
                    if item["modifier"] == self.modifier:
                        if type(item["driver_id"]) == Object:
                            row = box.row(align=True)
                            row.label(text=item["driver_id"].name)
                            rem = row.operator(OPS_OT_RemoveObjectAsMask.bl_idname, icon="X")
                            rem.modifier = self.modifier
                            rem.removed_object = item["driver_id"].name
                        else:
                            for o in item["driver_id"]:
                                row = box.row()
                                row.label(text=o.name)
                                rem = row.operator(OPS_OT_RemoveObjectAsMask.bl_idname, icon="X")
                                rem.modifier = self.modifier
                                rem.removed_object = o.name

        row = self.layout.row(align=True)
        row.prop(context.scene, 'character_ui_mask_outfit_piece')
        row.operator(OPS_OT_AddObjectAsMask.bl_idname, text="", icon="ADD").modifier = self.modifier

    def execute(self, context):
        return {"FINISHED"}


classes = [
    OPS_OT_UseAsMask,
    OPS_OT_AddObjectAsMask,
    OPS_OT_RemoveObjectAsMask
]


def register():
    bpy.types.Scene.character_ui_mask_outfit_piece = PointerProperty(type=Object, name="Outfit piece")

    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_mask_outfit_piece
    for c in reversed(classes):
        unregister_class(c)
