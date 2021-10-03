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
            prop = context.button_prop
            
            name=path[:path.rindex('.')]+".name"
            try:
                name=eval(name)
            except:
                name = False
            rig_id = ch.data[context.scene.character_ui_object_id]
            attributes_key = "CharacterUI_att_%s"%(rig_id)
            if attributes_key in ch:
                arr = []
                if self.parent_path:
                    for g in ch[attributes_key][self.panel_name]:
                        if g["name"] == self.group_name:
                            arr = g["attributes"]
                            if self.parent_path:
                                arr = sync_attribute_to_parent(arr, self.parent_path, path)
                            else:
                                try:
                                    arr.append({'path': path, 'name':name})
                                except:
                                    arr = []
                                    arr.append({'path': path, 'name':name})
                            g["attributes"] = arr
                else:
                    for g in ch[attributes_key][self.panel_name]:
                        if g["name"] == self.group_name:
                            try:
                                att = g["attributes"].to_list()
                                att.append({'path': path, 'name':name})
                                g["attributes"] = att
                            except:
                                att = g["attributes"]
                                att.append({'path': path, 'name':name})
                                g["attributes"] = att
                
                if name:
                    self.report({'INFO'}, 'Added attribute '+ name +' to '+ch.name)
                else:
                    self.report({'INFO'}, 'Added attribute to '+ch.name)
            else:
                self.report({'WARNING'}, ch.name + ' is not UI enabled! You must enable it first.')
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
classes = [
    OPS_OT_AddNewAttribute,
    OPS_OT_RemoveAttribute,
    OPS_OT_AttributeChangePosition
]
def register():
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

