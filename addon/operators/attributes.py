import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_AddNewAttribute(Operator):
    bl_idname = "character_ui.add_new_attribute"
    bl_label = "Select object to trigger shape key change for:"
    bl_description = "Sets the shape key to be toggled on/off based on an outfit piece"
    bl_options = {"INTERNAL"}

    panel_name: StringProperty()
    group_name: StringProperty()
    parent_path: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            try:
                bpy.ops.ui.copy_data_path_button(full_path=True)
            except:
                self.report(
                    {'WARNING'}, "Couldn't get path, invalid selection!")
                return {'CANCELLED'}

            path = context.window_manager.clipboard

            button_prop = context.button_prop
            name = False
            try:
                name = button_prop.name
            except:
                name = False
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)

            if self.parent_path not in ["", " "]:  # syncing attribtues
                driver_id = eval(
                    self.parent_path[:self.parent_path.index(']')+1])
                driver_id_path = self.parent_path[self.parent_path.index(
                    ']')+2:]
                driver_path = path[path.rindex('.')+1:]
                parent_prop = eval(
                    self.parent_path[:self.parent_path.rindex(".")])
                prop = eval(path[:path.rindex('.')])
                if parent_prop.bl_rna == prop.bl_rna:
                    err = CharacterUIAttributesOperatorsUtils.create_driver(
                        driver_id, prop, driver_path, "chui_value", [{"name": "chui_value", "path": driver_id_path}])
                    if err:
                        self.report(
                            {'ERROR'}, "Could not create driver and sync the attributes!")
                        return {"CANCELLED"}
                    name = "Default Value"
                    for g in ch[attributes_key][self.panel_name]:
                        if g["name"] == self.group_name:
                            for att in g["attributes"]:
                                if att["path"] == self.parent_path:
                                    if hasattr(att["synced"], "append"):
                                        synced = att["synced"]
                                        synced.append(path)
                                        att["synced"] = synced
                                    else:
                                        att["synced"] = [path]
                                    if att["name"]:
                                        name = att["name"]
                    self.report({"INFO"}, "Synced %s to %s" %
                                (prop.name, name))
                else:
                    self.report(
                        {"ERROR"}, "Attributes have different data types!")
                    return{"CANCELLED"}
            else:  # adding new attribute
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if hasattr(g["attributes"], "append"):
                            att = g["attributes"]
                            att.append(
                                {"name": name, "path": path, "synced": []})
                            g["attributes"] = att
                        else:
                            g["attributes"] = [
                                {"name": name, "path": path, "synced": []}]

        self.panel_name = ""
        self.parent_path = ""
        return {'FINISHED'}


class OPS_OT_RemoveAttribute(Operator):
    bl_idname = 'character_ui.remove_attribute'
    bl_label = 'Remove attribute from the UI'
    bl_description = "Removes attribute from the UI and other synced attributes too"
    bl_options = {"INTERNAL"}

    path: StringProperty()
    panel_name: StringProperty()
    group_name: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        att = g["attributes"]
                        new_att = []
                        for a in att:
                            if a['path'] != self.path:
                                new_att.append(a)
                        g["attributes"] = new_att
                        self.report({"INFO"}, 'Removed property')
        return {'FINISHED'}


class OPS_OT_AttributeChangePosition(Operator):
    bl_idname = 'character_ui.attribute_change_position'
    bl_label = "Change attributes position in the list"
    bl_description = "Changes position of the attribute in the current list"
    bl_options = {"INTERNAL"}

    path: StringProperty()
    panel_name: StringProperty()
    direction: BoolProperty()  # True moves up, False move down
    group_name: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        att = g["attributes"]
                        i = 0
                        for a in enumerate(att):
                            if a[1]['path'] == self.path:
                                i = a[0]
                        if self.direction and i-1 >= 0:  # move attribute up in the list
                            prev = att[i-1]
                            att[i-1] = att[i]
                            att[i] = prev
                            self.report(
                                {'INFO'}, "Moved attribute up in the list")
                        elif not self.direction and i+1 < len(att):
                            next = att[i+1]
                            att[i+1] = att[i]
                            att[i] = next
                            self.report(
                                {'INFO'}, "Moved attribute down in the list")
                        g["attributes"] = att
        return {'FINISHED'}


class CharacterUIAttributesOperatorsUtils():
    @staticmethod
    def create_driver(driver_id, driver_target, driver_path, driver_expression, variables):
        "TODO: same exact code is in the add-on, make it that it's only once in the whole codebase"

        try:
            driver_target.driver_remove(driver_path)
            driver = driver_target.driver_add(driver_path)
        except:
            return True

        def setup_driver(driver, addition_path=""):
            driver.type = "SCRIPTED"
            driver.expression = driver_expression
            for variable in variables:
                var = driver.variables.new()
                var.name = variable["name"]
                var.targets[0].id_type = driver_id.rna_type.name.upper()
                var.targets[0].id = variable["driver_id"] if "driver_id" in variable else driver_id
                var.targets[0].data_path = "%s%s" % (
                    variable["path"], addition_path)
        if type(driver) == list:
            for d in enumerate(driver):
                setup_driver(d[1].driver, "[%i]" % (d[0]))
        else:
            setup_driver(driver.driver)

    @staticmethod
    def sync_attribute_to_parent(attributes, parent_path, path, prop):
        "adds data path "
        for i in range(len(attributes)):
            if attributes[i]['path'] == parent_path:
                if 'synced' in attributes[i]:
                    # this thing is so unnecessary but I couldn't find a better solution, no matter what I did I couldn't add new attributes
                    syn = attributes[i]['synced']
                    if not syn:
                        syn = []
                    syn.append({"path": path, "prop": prop})
                    attributes[i]['synced'] = syn
                else:
                    syn = []  # here is it the same as few lines up
                    syn.append({"path": path, "prop": prop})
                    attributes[i]['synced'] = syn
        return attributes


class OPS_OT_EditAttribute(Operator):
    bl_idname = "character_ui.edit_attribute"
    bl_label = 'Edit attribute'
    bl_description = 'Edit attribute'
    bl_options = {"INTERNAL"}

    path: StringProperty(name="Path", description="RNA path of the attribute")
    panel_name: StringProperty()
    group_name: StringProperty()
    attribute_name: StringProperty(name="Name")
    invert_checkbox: BoolProperty(description="Forces checkbox to be inverted")
    toggle: BoolProperty(description="Style checkbox as a toggle")
    slider: BoolProperty(description="Use slider widget for numeric values")
    emboss: BoolProperty(description="Draw the button itself, not just the icon/text")
    icon: StringProperty(description="Override automatic icon of the item")

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.path:
                                self.attribute_name = att["name"] if att["name"] else "Default Value"
                                self.invert_checkbox = att["invert_checkbox"] if "invert_checkbox" in att else False
                                self.toggle = att["toggle"] if "toggle" in att else False
                                self.slider = att["slider"] if "slider" in att else False
                                self.emboss = att["emboss"] if "emboss" in att else True
                                self.icon = ("" if att["icon"] == "NONE" else att["icon"]) if "icon" in att else ""
        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.path:
                                prop_exists = True
                                try:
                                    eval(att["path"])
                                except:
                                    prop_exists = False

                                if prop_exists:
                                    layout = self.layout
                                    layout.prop(self, "attribute_name")
                                    layout.label(text=self.path)
                                    style_box = layout.box()
                                    style_box.label(text="Style")
                                    row = style_box.row()

                                    row.prop(self, "invert_checkbox", text="Invert checkbox", toggle=True)
                                    row.prop(self, "toggle", text="Toggle", toggle=True)
                                    row.prop(self, "slider", text="Slider", toggle=True)
                                    row.prop(self, "emboss", text="Emboss", toggle=True)
                                    icon_row = style_box.row(align=True)
                                    icon_row.prop(self, "icon", text="Icon")
                                    icon_row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "icons"

                                    try:
                                        style_box.label(
                                            text="-   Icon Preview", icon=self.icon)
                                    except:
                                        style_box.label(
                                            text="This icon does not exist - Icon Preview")

                                    if "synced" in att and len(att["synced"]):
                                        synced_box = layout.box()
                                        synced_box.label(
                                            text="Synced attributes", icon="LINK_BLEND")
                                        for s in att["synced"]:
                                            synced_row = synced_box.row()
                                            synced_row.label(text=s)
                                            remove_op = synced_row.operator(
                                                OPS_OT_RemoveSyncedAttribute.bl_idname, icon="X")
                                            remove_op.path = s
                                            remove_op.parent_path = self.path
                                            remove_op.panel_name = self.panel_name
                                            remove_op.group_name = self.group_name
                                else:
                                    layout = self.layout
                                    layout.label(
                                        text="Invalid attribute", icon="ERROR")
                                    op = layout.operator(
                                        OPS_OT_RemoveAttribute.bl_idname, icon="X", text="Remove attribute")
                                    op.path = self.path
                                    op.panel_name = self.panel_name
                                    op.group_name = self.group_name

    def execute(self, context):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.path:
                                if self.attribute_name not in ["", " "]:
                                    att["name"] = self.attribute_name
                                    att["invert_checkbox"] = self.invert_checkbox
                                    att["toggle"] = self.toggle
                                    att["slider"] = self.slider
                                    if self.icon not in ["", " "]:
                                        att["icon"] = self.icon
                                    else:
                                        att["icon"] = "NONE"
                                    att["emboss"] = self.emboss

        return{"FINISHED"}


class OPS_OT_RemoveSyncedAttribute(Operator):
    bl_idname = "character_ui.remove_synced_attribute"
    bl_label = ""
    bl_description = "Removes synced attribute"
    bl_options = {"INTERNAL"}

    path: StringProperty()
    parent_path: StringProperty()
    panel_name: StringProperty()
    group_name: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.parent_path:
                                prop = eval(self.path[:self.path.rindex('.')])
                                driver_path = self.path[self.path.rindex('.')+1:]
                                prop.driver_remove(driver_path)
                                att["synced"] = [item for item in att["synced"] if item != self.path]
        return{"FINISHED"}


classes = [
    OPS_OT_AddNewAttribute,
    OPS_OT_RemoveAttribute,
    OPS_OT_AttributeChangePosition,
    OPS_OT_EditAttribute,
    OPS_OT_RemoveSyncedAttribute
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
