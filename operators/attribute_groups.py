import bpy
from bpy.types import (Operator)
from bpy.props import ( StringProperty, BoolProperty) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_AddNewAttributeGroup(Operator):
    bl_idname = "character_ui.add_new_attribute_group"
    bl_label = "Add new Attribute Group"
    bl_description = "Creates new attribute group"

    panel_name : StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if attributes_key not in ch:
                ch[attributes_key] = {}
            def add_group(att):
                att.append({"name":'Group_'+str(len(att)), "attributes":[], "expanded": True})
                return att
            if self.panel_name in ch[attributes_key] and len(ch[attributes_key][self.panel_name]):
                ch[attributes_key][self.panel_name] = add_group(ch[attributes_key][self.panel_name])
            else:
                ch[attributes_key][self.panel_name] = add_group([])
            self.report({'INFO'}, "Added new attribute group")
        return {"FINISHED"}

class OPS_OT_ExpandAttributeGroup(Operator):
    "Expands or contracts attribute group"
    bl_idname = "character_ui.expand_attribute_group"
    bl_label = "Expand/Contract"
    bl_description = "Expands or Contracts Attribute Group"

    panel_name : StringProperty()
    group_name : StringProperty()

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                for i in range(len(ch[attributes_key][self.panel_name])):
                    g = ch[attributes_key][self.panel_name][i] 
                    if g["name"] == self.group_name:
                        g["expanded"] = not g["expanded"]
                    ch[attributes_key][self.panel_name][i] = g

        return {'FINISHED'}
        
class OPS_OT_EditAttributeGroup(Operator):
    "Edits settings of attribute groups"
    bl_idname = "character_ui.edit_attribute_group"
    bl_label = "Edit attribute group"
    bl_description = "Edit attribute group"

    panel_name : StringProperty()
    group_name : StringProperty()
    new_group_name : StringProperty(name="Group Name")
    group_icon : StringProperty(name="Icon", description="Name of the Icon for the group. Enable the built-in addon Icon Viewer to see all of the available icons.")

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                for g in ch[attributes_key][self.panel_name]:
                    if g["name"] == self.group_name:
                        self.new_group_name = g["name"].replace("_", " ")
                        self.group_icon = g["icon"] if "icon" in g else ""
        
                return context.window_manager.invoke_props_dialog(self, width=350)
        return None

    def draw(self, context):
        self.layout.prop(self, "new_group_name")
        self.layout.prop(self, "group_icon")
        try:
            self.layout.label(text="-   Icon Preview", icon=self.group_icon)
        except:
            self.layout.label(text="This icon does not exist - Icon Preview")

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                index = -1
                for i in range(len(ch[attributes_key][self.panel_name])):
                    if self.group_name == self.new_group_name.replace(" ","_") and ch[attributes_key][self.panel_name][i]["name"] ==self.new_group_name.replace(" ","_"):
                        ch[attributes_key][self.panel_name][i]["icon"] = self.group_icon
                        self.report({'INFO'}, "Updated group's icon")
                        return {'FINISHED'}
                    if ch[attributes_key][self.panel_name][i]["name"] == self.new_group_name.replace(" ","_"):
                        self.report({'INFO'}, "No changes saved, duplicated name for one panel")
                        return {'CANCELLED'}
                    if ch[attributes_key][self.panel_name][i]["name"] == self.group_name:
                        index = i
                    
                ch[attributes_key][self.panel_name][index]["name"] = self.new_group_name.replace(" ","_")
                ch[attributes_key][self.panel_name][index]["icon"] = self.group_icon
                self.report({'INFO'}, "Updated Attribute Group")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}

class OPS_OT_RemoveAttributeGroup(Operator):
    "Removes attribute group from the UI"
    bl_idname = 'character_ui.remove_attribute_group'
    bl_label = 'Remove attribute group from the UI'
    bl_description = "Removes attribute group from the UI and all of the attributes inside and other synced attributes too"

    group_name : StringProperty()
    panel_name : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                att = ch[attributes_key][self.panel_name]
                new_groups = []
                for g in att:
                    if g["name"] != self.group_name:
                        new_groups.append(g)
                ch[attributes_key][self.panel_name] = new_groups
                self.report({"INFO"}, 'Removed Attribute Group')
        return {'FINISHED'}  

class OPS_OT_AttributeGroupChangePosition(Operator):
    bl_idname = 'character_ui.attribute_group_change_position'
    bl_label = "Change attribute group's position in the list"
    bl_description = "Changes position of the attribute group in the current list"

    group_name : StringProperty()
    panel_name : StringProperty()
    direction : BoolProperty() #True moves up, False move down
    
    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if self.panel_name in ch[attributes_key]:
                att = ch[attributes_key][self.panel_name]
                i = 0
                for a in enumerate(att):
                    if a[1]['name'] == self.group_name:
                        i = a[0]
                if self.direction and i-1 >= 0: #move attribute group up in the list
                    prev = att[i-1]
                    att[i-1] = att[i]
                    att[i] = prev
                    self.report({'INFO'}, "Moved attribute group up in the list")
                elif not self.direction and i+1 < len(att):
                    next = att[i+1]
                    att[i+1] = att[i]
                    att[i] = next
                    self.report({'INFO'}, "Moved attribute group down in the list")
                ch[attributes_key][self.panel_name] = att
        return {'FINISHED'}


classes = [
    OPS_OT_AddNewAttributeGroup,
    OPS_OT_ExpandAttributeGroup,
    OPS_OT_EditAttributeGroup,
    OPS_OT_RemoveAttributeGroup,
    OPS_OT_AttributeGroupChangePosition
]
def register():
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

