import bpy
from bpy.types import (Operator, Object)
from bpy.props import (PointerProperty, StringProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_AddObjectAsDriver(Operator):
    bl_idname = "character_ui.add_object_as_driver"
    bl_label = "Add object"
    bl_description = "Adds selected object to the mask modifer"
    bl_options = {"INTERNAL"}

    modifier: StringProperty()
    shape_key: StringProperty()

    @classmethod
    def poll(self, context):
        return context.scene.character_ui_driver_object != None

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            found = False
            key = ""
            name = ""
            if self.modifier:
                key = "character_ui_masks"
                name = self.modifier
            if self.shape_key:
                key = "character_ui_shape_keys"
                name = self.shape_key
            driver = context.scene.character_ui_driver_object
            if key not in ch.data:
                ch.data[key] = []
            for item in ch.data[key]:
                if "name" in item and item["name"] == name:
                    new_items = []
                    try:
                        new_items = item["driver_id"]
                    except:
                        new_items = item["driver_id"].to_list()
                    if driver not in new_items:
                        new_items.append(driver)
                        item["driver_id"] = new_items
                    else:
                        self.report({"WARNING"}, "This object has already been added.")
                        return {"CANCELLED"}
                    found = True
                elif "modifier" in item and item["modifier"] == name:
                    old_item = item["driver_id"]
                    item["driver_id"] = [old_item]
                    item["name"] = name
                    del item["modifier"]

                elif "shape_key" in item and item["shape_key"] == name:
                    old_item = item["driver_id"]
                    item["driver_id"] = [old_item]
                    item["name"] = name
                    del item["shape_key"]

            if not found:
                items = []
                try:
                    items = ch.data[key].to_list()
                except:
                    items = ch.data[key]
                items.append({"name": name,
                             "driver_id": [driver]})
                ch.data[key] = items
            self.report({'INFO'}, "Added %s to %s" % (driver.name, name))
        context.scene.character_ui_driver_object = None

        return {'FINISHED'}


class OPS_OT_RemoveObjectAsDriver(Operator):
    bl_idname = "character_ui.remove_object_as_driver"
    bl_label = "Remove object"
    bl_description = "Removes object from the mask modifier"
    bl_options = {"INTERNAL"}

    modifier: StringProperty()
    shape_key: StringProperty()
    removed_object: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            key = ""
            name = ""
            if self.modifier:
                key = "character_ui_masks"
                name = self.modifier
            if self.shape_key:
                key = "character_ui_shape_keys"
                name = self.shape_key
            for item in ch.data[key]:
                if item["name"] == name:
                    if type(item["driver_id"]) == Object:
                        item["driver_id"] = []
                    else:
                        new_drivers = []
                        for o in item["driver_id"]:
                            if o.name != self.removed_object:
                                new_drivers.append(o)
                        item["driver_id"] = new_drivers
        self.report({'INFO'}, "Removed %s from %s" % (self.removed_object, name))

        return {'FINISHED'}


class OPS_OT_UseAsDriver(Operator):
    bl_idname = "character_ui.use_as_driver"
    bl_label = "Select object to trigger visibility change for:"
    bl_description = ""
    bl_options = {"INTERNAL"}

    modifier: StringProperty()
    shape_key: StringProperty()

    def invoke(self, context, event):
        context.scene.character_ui_driver_object = None
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        self.layout.label(text=self.modifier)
        box = self.layout.box()
        box.label(text="Objects", icon="OUTLINER_OB_MESH")
        ch = context.scene.character_ui_object
        if ch:
            key = ""
            name = ""
            driver_object = context.scene.character_ui_driver_object
            if self.modifier:
                key = "character_ui_masks"
                name = self.modifier
            if self.shape_key:
                key = "character_ui_shape_keys"
                name = self.shape_key

            if key in ch.data:
                for item in ch.data[key]:
                    if "name" in item:
                        if item["name"] == name:
                            for o in item["driver_id"]:
                                row = box.row()
                                row.label(text=o.name)
                                rem = row.operator(OPS_OT_RemoveObjectAsDriver.bl_idname, icon="X")
                                if self.modifier:
                                    rem.modifier = self.modifier
                                if self.shape_key:
                                    rem.shape_key = self.shape_key
                                rem.removed_object = o.name
                    if "modifier" in item or "shape_key" in item:
                        # for legacy reasons so it doesn't break compatibility with older versions
                        alert = box.row()
                        alert.alert = True
                        alert.label(text="Found old storing of data! Data will be updated to match current version", icon="ERROR")
            row = self.layout.row(align=True)
            row.prop(context.scene, 'character_ui_driver_object')
            remove_op = row.operator(OPS_OT_AddObjectAsDriver.bl_idname, text="", icon="ADD")
            if self.modifier:
                remove_op.modifier = self.modifier
            if self.shape_key:
                remove_op.shape_key = self.shape_key

    def execute(self, context):
        return {"FINISHED"}


classes = [
    OPS_OT_UseAsDriver,
    OPS_OT_AddObjectAsDriver,
    OPS_OT_RemoveObjectAsDriver
]


def register():
    bpy.types.Scene.character_ui_driver_object = PointerProperty(type=Object, name="Outfit piece")
    for c in classes:
        register_class(c)


def unregister():
    del bpy.types.Scene.character_ui_driver_object
    for c in reversed(classes):
        unregister_class(c)
