import bpy
from bpy.types import (Panel, PropertyGroup, Operator, Menu)
from bpy.props import (PointerProperty, StringProperty,
                       BoolProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)


class VIEW3D_PT_character_ui_attributes(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Character-UI"
    bl_label = "Character UI Attributes"

    @classmethod
    def poll(self, context):
        ch = context.scene.character_ui_object
        if not ch:
            return False
        rig_id_key = context.scene.character_ui_object_id
        return rig_id_key and rig_id_key in ch.data

    def draw(self, context):
        pass


class VIEW3D_PT_character_ui_attributes_body(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Body Panel"
    bl_idname = "VIEW3D_PT_character_ui_attributes_body"
    bl_parent_id = "VIEW3D_PT_character_ui_attributes"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_body_attributes_panels(context)

    def draw(self, context):
        CharacterUIAttributesUtils.render_attributes_group_panel(
            context, "body", self.layout)


class VIEW3D_PT_character_ui_attributes_outfits(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Outfits Panel"
    bl_idname = "VIEW3D_PT_character_ui_attributes_outfits"
    bl_parent_id = "VIEW3D_PT_character_ui_attributes"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_outfits_attributes_panels(context)

    def draw(self, context):
        CharacterUIAttributesUtils.render_attributes_group_panel(
            context, "outfits", self.layout)


class VIEW3D_PT_character_ui_attributes_rig(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Rig Panel"
    bl_idname = "VIEW3D_PT_character_ui_attributes_rig"
    bl_parent_id = "VIEW3D_PT_character_ui_attributes"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_rig_attributes_panels(context)

    def draw(self, context):
        CharacterUIAttributesUtils.render_attributes_group_panel(
            context, "rig", self.layout)


class VIEW3D_PT_character_ui_attributes_miscellaneous(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Miscellaneous Panel"
    bl_idname = "VIEW3D_PT_character_ui_attributes_miscellaneous"
    bl_parent_id = "VIEW3D_PT_character_ui_attributes"

    def draw(self, context):
        CharacterUIAttributesUtils.render_attributes_group_panel(
            context, "misc", self.layout)


class CharacterUIAttributesUtils:
    @staticmethod
    def render_right_click_menu_operators(self, context):
        ch = context.scene.character_ui_object
        if ch:
            layout = self.layout
            layout.separator()
            layout.label(text="Character-UI Attributes")
            layout.menu(WM_MT_add_new_attribute.bl_idname)
            layout.menu(WM_MT_sync_attribute_panel.bl_idname)

    @staticmethod
    def render_attributes_group_panel(context, panel_name, layout):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (rig_id)
        layout.operator(
            "character_ui.add_new_attribute_group").panel_name = panel_name
        if attributes_key in ch:
            if panel_name in ch[attributes_key]:
                for g in ch[attributes_key][panel_name]:
                    box = layout.box()
                    header_row = box.row(align=True)
                    expand_op = header_row.operator(
                        "character_ui.expand_attribute_group", text="", icon="DOWNARROW_HLT" if g["expanded"] else "RIGHTARROW", emboss=False)
                    expand_op.panel_name = panel_name
                    expand_op.group_name = g["name"]
                    try:
                        header_row.label(text=g["name"].replace(
                            "_", " "), icon=g["icon"])
                    except:
                        header_row.label(text=g["name"].replace("_", " "))
                    # edit group operator
                    edit_op = header_row.operator(
                        "character_ui.edit_attribute_group", text="", icon="PREFERENCES")
                    edit_op.panel_name = panel_name
                    edit_op.group_name = g["name"]
                    # edit group operator
                    # visibility operator
                    visibility_op = header_row.operator(
                        "character_ui.edit_visibility_variables", text="", icon="HIDE_OFF")
                    visibility_op.panel_name = panel_name
                    visibility_op.group_name = g["name"]
                    # visibility operator
                    # move up group operator
                    move_up_op = header_row.operator(
                        "character_ui.attribute_group_change_position", text="", icon="TRIA_UP")
                    move_up_op.panel_name = panel_name
                    move_up_op.group_name = g["name"]
                    move_up_op.direction = True
                    # move up group operator
                    # move down group operator
                    move_up_op = header_row.operator(
                        "character_ui.attribute_group_change_position", text="", icon="TRIA_DOWN")
                    move_up_op.panel_name = panel_name
                    move_up_op.group_name = g["name"]
                    move_up_op.direction = False
                    # move down group operator
                    # delete group operator
                    delete_op = header_row.operator(
                        "character_ui.remove_attribute_group", text="", icon="X")
                    delete_op.panel_name = panel_name
                    delete_op.group_name = g["name"]
                    # delete group operator

                    if g["expanded"]:
                        for p in g["attributes"]:
                            row = box.row(align=True)
                            delimiter = "][" if "][" in p["path"] else "."
                            offset = 1 if "][" in p["path"] else 0
                            prop = p["path"][p["path"].rindex(delimiter)+1:]
                            path = p["path"][:p["path"].rindex(
                                delimiter)+offset]
                            prop_exists = True
                            toggle = p["toggle"] if "invert_checkbox" in p else False
                            invert_checkbox = p["invert_checkbox"] if "invert_checkbox" in p else False
                            slider = p["slider"] if "slider" in p else False
                            emboss = p["emboss"] if "emboss" in p else True
                            icon = p["icon"] if "icon" in p else "NONE"
                            try:
                                eval(p["path"])
                            except:
                                prop_exists = False
                            if p["name"]:
                                try:
                                    row.prop(eval(
                                        path), prop, text=p["name"], invert_checkbox=invert_checkbox, toggle=toggle, slider=slider, icon=icon, emboss=emboss)
                                except:
                                    continue

                            else:
                                try:
                                    row.prop(eval(path), prop, invert_checkbox=invert_checkbox,
                                             toggle=toggle, slider=slider, icon=icon, emboss=emboss)
                                except:
                                    continue

                            if not prop_exists:
                                row.label(text="Invalid attribute",
                                          icon="ERROR")

                            op_edit = row.operator(
                                "character_ui.edit_attribute", icon="PREFERENCES", text="")
                            op_edit.path = p["path"]
                            op_edit.panel_name = panel_name
                            op_edit.group_name = g["name"]

                            a_visibility_op = row.operator(
                                "character_ui.edit_visibility_variables", text="", icon="HIDE_OFF")
                            a_visibility_op.panel_name = panel_name
                            a_visibility_op.group_name = g["name"]
                            a_visibility_op.path = p["path"]

                            op_up = row.operator(
                                "character_ui.attribute_change_position", icon="TRIA_UP", text="")
                            op_up.direction = True
                            op_up.path = p["path"]
                            op_up.panel_name = panel_name
                            op_up.group_name = g["name"]

                            op_down = row.operator(
                                "character_ui.attribute_change_position", icon="TRIA_DOWN", text="")
                            op_down.direction = False
                            op_down.path = p["path"]
                            op_down.panel_name = panel_name
                            op_down.group_name = g["name"]

                            op = row.operator(
                                "character_ui.remove_attribute", icon="X", text="")
                            op.path = p["path"]
                            op.panel_name = panel_name
                            op.group_name = g["name"]

    @staticmethod
    def render_attribute_groups_menu(layout, context, panel_name):
        ch = context.scene.character_ui_object
        ch_id = ch.data[context.scene.character_ui_object_id]
        key = "CharacterUI_att_%s" % (ch_id)
        if key in ch:
            if panel_name in ch[key]:
                for g in ch[key][panel_name]:
                    op = layout.operator(
                        "character_ui.add_new_attribute", text=g["name"].replace("_", " "))
                    op.panel_name = panel_name
                    op.group_name = g["name"]
                    op.parent_path = ""

    @staticmethod
    def render_attributes_in_menu(layout, context, panel_name):
        ch = context.scene.character_ui_object
        ch_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s" % (ch_id)
        if attributes_key in ch:
            if panel_name in ch[attributes_key]:
                for g in ch[attributes_key][panel_name]:
                    layout.separator()
                    layout.label(text=g["name"].replace("_", " "))
                    layout.separator()
                    for p in g["attributes"]:
                        name = "Default Value"
                        if p["name"]:
                            name = p["name"]
                        op = layout.operator(
                            "character_ui.add_new_attribute", text=name)
                        op.parent_path = p["path"]
                        op.panel_name = panel_name
                        op.group_name = g["name"]
        return layout

    @staticmethod
    def render_rig_attributes_panels(context):
        ch = context.scene.character_ui_object
        if ch:
            return ch.type == "ARMATURE"
        return False

    @staticmethod
    def render_outfits_attributes_panels(context):
        ch = context.scene.character_ui_object
        if ch:
            if context.scene.character_ui_object_id in ch.data:
                if ch.data["outfits_collection"]:
                    return True
        return False

    @staticmethod
    def render_body_attributes_panels(context):
        ch = context.scene.character_ui_object
        if ch:
            if ch.data["body_object"] or ch.data["hair_collection"]:
                return True
        return False


class WM_MT_button_context(Menu):
    bl_label = "Add to UI"

    def draw(self, context):
        pass


class WM_MT_add_new_attribute(Menu):
    bl_label = "Add New Attribute"
    bl_idname = "WM_MT_add_new_attribute_menu"

    def draw(self, context):
        layout = self.layout
        layout.menu(WM_MT_add_new_attribute_outfits_menu.bl_idname,
                    text="Outfits Panel")
        layout.menu(WM_MT_add_new_attribute_body_menu.bl_idname,
                    text="Body Panel")
        layout.menu(WM_MT_add_new_attribute_rig_menu.bl_idname,
                    text="Rig Panel")
        layout.menu(WM_MT_add_new_attribute_miscellaneous_menu.bl_idname,
                    text="Miscellaneous Panel")


class WM_MT_add_new_attribute_outfits_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_add_new_attribute_outfits_menu"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_outfits_attributes_panels(context)

    def draw(self, context):
        self.layout.label(text="Attribute Groups for Outfits Panel")
        CharacterUIAttributesUtils.render_attribute_groups_menu(
            self.layout, context, "outfits")


class WM_MT_add_new_attribute_body_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_add_new_attribute_body_menu"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_body_attributes_panels(context)

    def draw(self, context):
        self.layout.label(text="Attribute Groups for Body Panel")
        CharacterUIAttributesUtils.render_attribute_groups_menu(
            self.layout, context, "body")


class WM_MT_add_new_attribute_rig_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_add_new_attribute_rig_menu"

    @classmethod
    def poll(self, context):
        return CharacterUIAttributesUtils.render_rig_attributes_panels(context)

    def draw(self, context):
        self.layout.label(text="Attribute Groups for Body Panel")
        CharacterUIAttributesUtils.render_attribute_groups_menu(
            self.layout, context, "rig")


class WM_MT_add_new_attribute_miscellaneous_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_add_new_attribute_miscellaneous_menu"

    def draw(self, context):
        self.layout.label(text="Attribute Groups for Body Panel")
        CharacterUIAttributesUtils.render_attribute_groups_menu(
            self.layout, context, "misc")


class WM_MT_sync_attribute_panel(Menu):
    bl_label = "Sync To Attribute"
    bl_idname = "WM_MT_sync_attribute_panel"

    def draw(self, context):
        layout = self.layout
        layout.menu(WM_MT_sync_attribute_outfits_menu.bl_idname,
                    text="Outfits Panel")
        layout.menu(WM_MT_sync_attribute_body_menu.bl_idname,
                    text="Body Panel")
        layout.menu(WM_MT_sync_attribute_rig_menu.bl_idname, text="Rig Panel")
        layout.menu(WM_MT_sync_attribute_miscellaneous_menu.bl_idname,
                    text="Miscellaneous Panel")


class WM_MT_sync_attribute_outfits_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_sync_attribute_outfits_menu"

    def draw(self, context):
        self.layout.label(text="Attributes for Rig Layers Panel")
        CharacterUIAttributesUtils.render_attributes_in_menu(
            self.layout, context, "outfits")


class WM_MT_sync_attribute_body_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_sync_attribute_body_menu"

    def draw(self, context):
        self.layout.label(text="Attributes for Rig Layers Panel")
        CharacterUIAttributesUtils.render_attributes_in_menu(
            self.layout, context, "body")


class WM_MT_sync_attribute_rig_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_sync_attribute_rig_menu"

    def draw(self, context):
        self.layout.label(text="Attributes for Rig Layers Panel")
        CharacterUIAttributesUtils.render_attributes_in_menu(
            self.layout, context, "rig")


class WM_MT_sync_attribute_miscellaneous_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = "WM_MT_sync_attribute_miscellaneous_menu"

    def draw(self, context):
        self.layout.label(text="Attributes for Rig Layers Panel")
        CharacterUIAttributesUtils.render_attributes_in_menu(
            self.layout, context, "misc")


classes = [
    WM_MT_button_context,
    WM_MT_add_new_attribute,
    WM_MT_add_new_attribute_outfits_menu,
    WM_MT_add_new_attribute_body_menu,
    WM_MT_add_new_attribute_rig_menu,
    WM_MT_add_new_attribute_miscellaneous_menu,
    VIEW3D_PT_character_ui_attributes,
    VIEW3D_PT_character_ui_attributes_outfits,
    VIEW3D_PT_character_ui_attributes_body,
    VIEW3D_PT_character_ui_attributes_rig,
    VIEW3D_PT_character_ui_attributes_miscellaneous,
    WM_MT_sync_attribute_panel,
    WM_MT_sync_attribute_outfits_menu,
    WM_MT_sync_attribute_body_menu,
    WM_MT_sync_attribute_rig_menu,
    WM_MT_sync_attribute_miscellaneous_menu

]


def register():
    for c in classes:
        register_class(c)

    bpy.types.WM_MT_button_context.append(
        CharacterUIAttributesUtils.render_right_click_menu_operators)


def unregister():
    bpy.types.WM_MT_button_context.remove(
        CharacterUIAttributesUtils.render_right_click_menu_operators)

    for c in reversed(classes):
        unregister_class(c)
