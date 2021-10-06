import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_AddNewAttribute(Operator):
    bl_idname = "character_ui.add_new_attribute"
    bl_label = "Select object to trigger shape key change for:"
    bl_description = "Sets the shape key to be toggled on/off based on an outfit piece"

    panel_name : StringProperty()
    group_name : StringProperty()
    parent_path : StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            try:
                bpy.ops.ui.copy_data_path_button(full_path=True)
            except:
                self.report({'WARNING'}, "Couldn't get path, invalid selection!")
                return {'FINISHED'}

            path = context.window_manager.clipboard
            
            name=path[:path.rindex('.')]+".name"
            try:
                name=eval(name)
            except:
                name = False
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.parent_path not in ["", " "]: #syncing attribtues
                driver_id = eval(self.parent_path[:self.parent_path.index(']')+1])
                driver_id_path = self.parent_path[self.parent_path.index(']')+2:]
                driver_path = path[path.rindex('.')+1:]
                prop = eval(path[:path.rindex('.')])
                parent_prop = eval(self.parent_path[:self.parent_path.rindex(".")])

                print(parent_prop.bl_rna, prop.bl_rna)
                if parent_prop.bl_rna == prop.bl_rna:
                    CharacterUIAttributesOperatorsUtils.create_driver(driver_id, prop, driver_path, "chui_value", [{"name": "chui_value", "path":driver_id_path}])
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
                    self.report({"INFO"}, "Synced %s to %s"%(prop.name, name))
                else:
                    self.report({"ERROR"}, "Attributes have different data types!")
                    return{"CANCELLED"}
            else: #adding new attribute
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        if hasattr(g["attributes"], "append"):
                            att = g["attributes"]
                            att.append({"name": name, "path": path, "synced": []})
                            g["attributes"] = att
                        else:
                            g["attributes"] = [{"name": name, "path": path, "synced": []}]

        self.panel_name = ""
        self.parent_path = ""
        return {'FINISHED'}

class OPS_OT_RemoveAttribute(Operator):
    bl_idname = 'character_ui.remove_attribute'
    bl_label = 'Remove attribute from the UI'
    bl_description = "Removes attribute from the UI and other synced attributes too"
    path : StringProperty()
    panel_name : StringProperty()
    group_name : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
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
    path : StringProperty()
    panel_name : StringProperty()
    direction : BoolProperty() #True moves up, False move down
    group_name : StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        att = g["attributes"]
                        i = 0
                        for a in enumerate(att):
                            if a[1]['path'] == self.path:
                                i = a[0]
                        if self.direction and i-1 >= 0: #move attribute up in the list
                            prev = att[i-1]
                            att[i-1] = att[i]
                            att[i] = prev
                            self.report({'INFO'}, "Moved attribute up in the list")
                        elif not self.direction and i+1 < len(att):
                            next = att[i+1]
                            att[i+1] = att[i]
                            att[i] = next
                            self.report({'INFO'}, "Moved attribute down in the list")
                        g["attributes"] = att
        return {'FINISHED'}

class CharacterUIAttributesOperatorsUtils():
    @staticmethod
    def create_driver(driver_id, driver_target, driver_path, driver_expression, variables):
        "TODO: same exact code is in the add-on, make it that it's only once in the whole codebase"
        driver_target.driver_remove(driver_path)
        driver = driver_target.driver_add(driver_path)

        def setup_driver(driver, addition_path = ""):
            driver.type = "SCRIPTED"
            driver.expression = driver_expression
            for variable in variables:
                var = driver.variables.new()
                var.name = variable["name"]
                var.targets[0].id_type = driver_id.rna_type.name.upper()
                var.targets[0].id = variable["driver_id"] if "driver_id" in variable else driver_id
                var.targets[0].data_path = "%s%s"%(variable["path"], addition_path)
        print(type(driver))
        if type(driver) == list:
            for d in enumerate(driver):
                setup_driver(d[1].driver,"[%i]"%(d[0]))
        else:
            setup_driver(driver.driver)
    @staticmethod
    def sync_attribute_to_parent(attributes, parent_path, path, prop):
        "adds data path "
        for i in range(len(attributes)):
            if attributes[i]['path'] == parent_path:
                if 'synced' in attributes[i]:
                    syn = attributes[i]['synced'] #this thing is so unnecessary but I couldn't find a better solution, no matter what I did I couldn't add new attributes
                    if not syn:
                        syn = []
                    syn.append({"path": path, "prop": prop})
                    attributes[i]['synced'] = syn
                else:
                    syn = [] #here is it the same as few lines up
                    syn.append({"path": path, "prop": prop})
                    attributes[i]['synced'] = syn
        return attributes

class OPS_OT_EditAttribute(Operator):
    bl_idname = "character_ui.edit_attribute"
    bl_label = 'Edit attribute'
    bl_description = 'Edit attribute' 

    path : StringProperty(name="Path", description="RNA path of the attribute")
    panel_name : StringProperty()
    group_name : StringProperty()
    attribute_name : StringProperty(name="Name")

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s"%(rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.path:
                               self.attribute_name = att["name"] if att["name"] else "Default Value"
                                  
        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "attribute_name")
    def execute(self, context):
        ch = context.scene.character_ui_object
        rig_id = ch.data[context.scene.character_ui_object_id]
        attributes_key = "CharacterUI_att_%s"%(rig_id)
        if attributes_key in ch:
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if self.group_name == g["name"]:
                        for att in g["attributes"]:
                            if att["path"] == self.path:
                                if self.attribute_name not in ["", " "]:
                                    att["name"] = self.attribute_name
        return{"FINISHED"}
classes = [
    OPS_OT_AddNewAttribute,
    OPS_OT_RemoveAttribute,
    OPS_OT_AttributeChangePosition,
    OPS_OT_EditAttribute
]
def register():
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

