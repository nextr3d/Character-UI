import bpy
from bpy.types import (Operator, PropertyGroup)
from bpy.props import (PointerProperty, StringProperty,
                       BoolProperty, CollectionProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)


class VisibilityVariableItem(PropertyGroup):
    variable: StringProperty(name="Variable")
    data_path: StringProperty(name="Data Path")


class OPS_OT_EditVisibilityVariables(Operator):
    bl_idname = "character_ui.edit_visibility_variables"
    bl_label = ""
    bl_description = "Edits visibility"
    bl_options = {"INTERNAL"}

    path: StringProperty(name="Path", description="RNA path of the attribute")
    panel_name: StringProperty()
    group_name: StringProperty()
    variables: CollectionProperty(type=VisibilityVariableItem)
    expression: StringProperty(name="Expression")

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if self.path == "":
                            if "visibility" in g:
                                if self.expression not in ["", " "]:
                                    g["visibility"]["expression"] = self.expression
                                    new_vars = []
                                    for var in context.scene.character_ui_variables:
                                        if var.variable not in ["", " "] and var.data_path not in ["", " "]:
                                            new_vars.append({"variable": var.variable, "data_path": var.data_path})
                                    g["visibility"]["variables"] = new_vars
                                else:
                                    del g["visibility"]
                        else:
                            for att in g["attributes"]:
                                if self.path == att["path"]:
                                    if "visibility" in att:
                                        if self.expression not in ["", " "]:
                                            att["visibility"]["expression"] = self.expression
                                            new_vars = []
                                            for var in context.scene.character_ui_variables:
                                                if var.variable not in ["", " "] and var.data_path not in ["", " "]:
                                                    new_vars.append({"variable": var.variable, "data_path": var.data_path})
                                            att["visibility"]["variables"] = new_vars
                                        else:
                                            del att["visibility"]
        return {"FINISHED"}
    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        context.scene.character_ui_variables.clear()
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            self.expression = ""
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if self.path == "":
                            if "visibility" in g:
                                self.expression = g["visibility"]["expression"]
                                for var in g["visibility"]["variables"]:
                                    collection_var = context.scene.character_ui_variables.add()
                                    collection_var.variable = var["variable"]
                                    collection_var.data_path = var["data_path"]
                        else:
                            for att in g["attributes"]:
                                if self.path == att["path"]:
                                    if "visibility" in att:
                                        if "expression" in att["visibility"]:
                                            self.expression = att["visibility"]["expression"]
                                            for var in att["visibility"]["variables"]:
                                                collection_var = context.scene.character_ui_variables.add()
                                                collection_var.variable = var["variable"]
                                                collection_var.data_path = var["data_path"]

        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        expression_row = layout.row(align=True)
        expression_row.prop(self, "expression")
        expression_row.operator("character_ui.tooltip", text="", icon="QUESTION").tooltip_id = "character_ui_expression"
        for var in enumerate(context.scene.character_ui_variables):
            box = layout.box()
            box.prop(var[1], "variable")
            box.prop(var[1], "data_path")
            remove_op = box.operator(OPS_OT_RemoveVariable.bl_idname, icon="X")
            remove_op.panel_name = self.panel_name
            remove_op.group_name = self.group_name
            remove_op.path = self.path
            remove_op.var_id = var[0]

        add_var = layout.operator(OPS_OT_AddNewVariable.bl_idname)
        add_var.panel_name = self.panel_name
        add_var.group_name = self.group_name
        add_var.path = self.path


class OPS_OT_AddNewVariable(Operator):
    bl_idname = "character_ui.add_new_variable"
    bl_label = "Add new variable"
    bl_description = "Adds new variable"
    bl_options = {"INTERNAL"}

    path: StringProperty(name="Path", description="RNA path of the attribute")
    panel_name: StringProperty()
    group_name: StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if self.path == "":
                            if "visibility" in g:
                                variables = g["visibility"]["variables"]
                                try:
                                    variables.append(
                                        {"variable": "var", "data_path": ""})
                                except:
                                    variables.to_list().append(
                                        {"variable": "var", "data_path": ""})
                                g["visibility"]["variables"] = variables
                            else:
                                g["visibility"] = {"expression": "", "variables": [
                                    {"variable": "var", "data_path": ""}]}
                            new_var = context.scene.character_ui_variables.add()
                            new_var.variable = "var"
                            new_var.data_path = ""
                        else:
                            for att in g["attributes"]:
                                if self.path == att["path"]:
                                    if "visibility" in att:
                                        variables = []
                                        if "variables" in att["visibility"]:
                                            variables = att["visibility"]["variables"]
                                            try:
                                                variables.append(
                                                    {"variable": "var", "data_path": ""})
                                            except:
                                                variables.to_list().append(
                                                    {"variable": "var", "data_path": ""})
                                        else:
                                            variables.append({"variable": "var", "data_path": ""})
                                        att["visibility"]["variables"] = variables
                                    else:
                                        att["visibility"] = {"expression": "", "variables": [
                                            {"variable": "var", "data_path": ""}]}
                                    new_var = context.scene.character_ui_variables.add()
                                    new_var.variable = "var"
                                    new_var.data_path = ""

        return {"FINISHED"}


class OPS_OT_RemoveVariable(Operator):
    bl_idname = "character_ui.remove_variable"
    bl_label = "Remove variable"
    bl_description = "Removes variable"
    bl_options = {"INTERNAL"}

    path: StringProperty(name="Path", description="RNA path of the attribute")
    panel_name: StringProperty()
    group_name: StringProperty()
    var_id: IntProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s" % (rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if self.path == "":
                            if "visibility" in g:
                                context.scene.character_ui_variables.remove(
                                    self.var_id)
                                new_vars = g["visibility"]["variables"]
                                if self.var_id < len(new_vars):
                                    del new_vars[self.var_id]
                                    g["visibility"]["variables"] = new_vars
                        else:
                            for att in g["attributes"]:
                                if self.path == att["path"]:
                                    if "visibility" in att:
                                        context.scene.character_ui_variables.remove(
                                            self.var_id)
                                        new_vars = att["visibility"]["variables"]
                                        if self.var_id < len(new_vars):
                                            del new_vars[self.var_id]
                                            att["visibility"]["variables"] = new_vars
        return {"FINISHED"}

classes = [
    VisibilityVariableItem,
    OPS_OT_AddNewVariable,
    OPS_OT_EditVisibilityVariables,
    OPS_OT_RemoveVariable
]


def register():
    for c in classes:
        register_class(c)
    bpy.types.Scene.character_ui_variables = CollectionProperty(
        type=VisibilityVariableItem)


def unregister():
    del bpy.types.Scene.character_ui_variables
    for c in reversed(classes):
        unregister_class(c)
