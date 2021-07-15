from bpy.utils import (register_class, unregister_class)
from bpy.types import (Panel, Operator, PropertyGroup, Menu)
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty
import bpy

bl_info = {
    "name": "Nextr Rig UI Debugger",
    "description": "Script helps you to create menus just by clicking",
    "author": "Nextr3D",
    "version": (1, 1, 1),
    "blender": (2, 92, 0)
}

def get_rig(name):
    if name in bpy.data.objects:
        if bpy.data.objects[name].type == 'ARMATURE':
            return bpy.data.objects[name]
    return False
def ui_setup_enum(update_function, name="Name", description="Empty description", items=[], default=0):
    "method for easier creation of enums (selects)"
    return EnumProperty(
        name=name,
        description=description,
        items=items,
        update=update_function,
        default='OP'+str(default)
    )
def ui_setup_toggle(update_function, name='Name', description='Empty description', default=False):
    "method for easier creation of toggles (buttons)"
    return BoolProperty(
        name=name,
        description=description,
        update=update_function,
        default=default
    )
def ui_setup_int(update_function, name='Name', description='Empty description', default=0, min=0, max=1):
    "method for easier creation of toggles (buttons)"
    return IntProperty(
        name=name,
        description=description,
        update=update_function,
        default=default,
        min = min,
        max= max
    )
def ui_setup_string(update_function, name='Name', description='Empty description', default=""):
    "method for easier creation of toggles (buttons)"
    return StringProperty(
        name=name,
        description=description,
        update=update_function,
        default=default
    )

def get_edited_object(context):
    "return object which is currently being edited"
    if 'active_object' in context.scene:
        if context.scene['active_object']:
            return context.scene['active_object']
    return context.active_object

class VIEW3D_PT_nextr_rig_debug(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Main"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            o = get_edited_object(context)
            pinned = False
            if 'active_object' in context.scene:
                if context.scene['active_object']:
                    pinned = True 
            layout.operator('nextr_debug.pin_active_object', text="Unpin "+o.name if pinned else "Pin "+o.name, depress=pinned, icon="PINNED" if pinned else "UNPINNED")
            layout.prop(context.scene, 'nextr_rig_properties_key')
            layout.prop(context.scene, 'nextr_rig_attributes_key')
            if o.type != 'ARMATURE':
                layout.operator('nextr.empty', text="Warning, object is not an Armature", depress=True, emboss=False)
            if context.scene["nextr_rig_properties_key"] not in o.data or context.scene["nextr_rig_attributes_key"] not in o.data:
                layout.operator('nextr_debug.enable_rig').object_name = o.name
            else:
                layout.operator('nextr.empty', text="Object is UI enabled", depress=True, emboss=False)
                has_outfits = o.name+" Outfits" in bpy.data.collections
                has_hair = o.name+" Hair" in bpy.data.collections
                has_body = o.name+" Body" in bpy.data.collections
                box = self.layout.box()
                box.label(text="Main Collections")
                if has_outfits:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Outfits exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for outfits')
                    op.collection_name = o.name+ " Outfits"
                    op.collection_parent_name = o.name
                if has_hair:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Hair exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for hair')
                    op.collection_name = o.name+ " Hair"
                    op.collection_parent_name = o.name
                if has_body:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Body exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for body')
                    op.collection_name = o.name+ " Body"
                    op.collection_parent_name = o.name

class VIEW3D_PT_nextr_rig_debug_rig_layers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Rig Layers"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Rig Layers")
        box.operator('nextr_debug.generate_rig_layers')
        for i in range(31):
            icon = "HIDE_OFF"
            if 'nextr_rig_layers_visibility_'+str(i) in context.scene:
                icon = "HIDE_OFF" if context.scene['nextr_rig_layers_visibility_'+str(i)] else "HIDE_ON"
            row = box.row(align=True)
            name = "Layer "+str(i+1)
            if 'nextr_rig_layers_name_'+str(i) in context.scene:
                name = context.scene['nextr_rig_layers_name_'+str(i)]
            row_box = row.box()
            row_box.label(text=name)
            row_box_row_name = row_box.row(align=True)
            row_box_row_name.prop(context.scene, 'nextr_rig_layers_visibility_'+str(i), icon=icon)
            row_box_row_name.prop(context.scene, 'nextr_rig_layers_name_'+str(i))
            row_box.label(text="Index of the rig layer")
            row_box_row_layers = row_box.row(align=True)
            row_box_row_layers.prop(context.scene, 'nextr_rig_layers_index_'+str(i))
            row_box.label(text="Row in the UI")
            row_box_row_row = row_box.row(align=True)
            row_box_row_row.prop(context.scene, 'nextr_rig_layers_row_'+str(i))

        box.operator('nextr_debug.generate_rig_layers')
class VIEW3D_PT_nextr_rig_debug_attributes(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Attributes"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            o = get_edited_object(context)
            attributes_key = context.scene['nextr_rig_attributes_key']
            if attributes_key in o.data:
                box_outfits = layout.box()

                box_outfits.label(text="Attributes for Outfits Panel")
                render_attributes(box_outfits, 'outfits', o.data[attributes_key])
                box_body = layout.box()
                box_body.label(text="Attributes for Body Panel")
                render_attributes(box_body, 'body', o.data[attributes_key])
                box_rig_layers = layout.box()
                box_rig_layers.label(text="Attributes for Rig Layers Panel")
                render_attributes(box_rig_layers, 'rig', o.data[attributes_key])
            else:
                layout.operator('nextr.empty', text="Object needs to be UI enabled to add custom attributes to it!", depress=True, emboss=False)
class OPS_OT_EnableNextrRig(Operator):
    bl_idname = 'nextr_debug.enable_rig'
    bl_label = 'Enable Nextrrig on object'
    bl_description = 'Adds necessary props to the object'

    object_name : StringProperty()
    def execute(self, context):
        if self.object_name in bpy.data.objects:
            o = get_edited_object(context)
            master_collection = None
            if self.object_name not in bpy.data.collections:
                master_collection = bpy.data.collections.new(name=self.object_name)
                context.scene.collection.children.link(master_collection)
            else:
                master_collection = bpy.data.collections[self.object_name]
            for c in o.users_collection:
                c.objects.unlink(o)
            master_collection.objects.link(o)
            o.data[context.scene["nextr_rig_properties_key"]] = {}
            o.data[context.scene["nextr_rig_attributes_key"]] = {}
            bpy.context.scene.object.active = o
        return {'FINISHED'}

class OPS_OT_AddCollection(Operator):
    bl_idname = 'nextr_debug.add_collection'
    bl_label = 'Adds collection'
    bl_description = 'Adds collection to another colection'

    collection_name: StringProperty()
    collection_parent_name: StringProperty()

    def execute(self, context):
        if self.collection_parent_name in bpy.data.collections:
            bpy.data.collections[self.collection_parent_name].children.link(bpy.data.collections.new(name=self.collection_name))
        else:
            bpy.ops.nextr_debug.add_collection(collection_name=self.collection_parent_name, collection_parent_name=bpy.data.collections[0].name)
        return {'FINISHED'}

class OPS_OT_Empty(Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'
    def execute(self, context):
        return {'FINISHED'}

class OPS_OT_AddAttribute(Operator):
    bl_idname = 'nextr_debug.add_attribute'
    bl_label = 'Text'
    bl_description = 'Adds the attribute to the UI or synces it to another attribute'
    
    panel_name : StringProperty()
    parent_path :  StringProperty()

    def execute(self, context):
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
        if context.active_object:
            o = get_edited_object(context)
            attributes_key = context.scene["nextr_rig_attributes_key"]
            if attributes_key in o.data:
                arr = []
                if self.panel_name in o.data[attributes_key]:
                    arr = o.data[attributes_key][self.panel_name]
                    if self.parent_path:
                        arr = sync_attribute_to_parent(arr, self.parent_path, path)
                    else:
                        try:
                            arr.append({'path': path, 'name':name})
                        except:
                            arr = []
                            arr.append({'path': path, 'name':name})
                    o.data[attributes_key][self.panel_name] = arr
                else:
                    arr.append({'path': path, 'name':name})
                    o.data[attributes_key][self.panel_name] = arr
                
                if name:
                    self.report({'INFO'}, 'Added attribute '+ name +' to '+o.name)
                else:
                    self.report({'INFO'}, 'Added attribute to '+o.name)
            else:
                self.report({'WARNING'}, o.name + ' is not UI enabled! You must enable it first.')
        self.panel_name = ""
        self.parent_path = ""
        return {'FINISHED'}

class OPS_OT_PinActiveObject(Operator):
    bl_idname = 'nextr_debug.pin_active_object'
    bl_label = 'Pin active object'
    bl_label = 'Pins active object'
    
    def execute(self, context):
        if context.active_object:
            if 'active_object' in context.scene:
                if context.scene['active_object']:
                    context.scene['active_object'] = None
                    self.report({'INFO'}, "Unpinned "+context.active_object.name)
                else:
                    context.scene['active_object'] = context.active_object
                    self.report({'INFO'}, "Pinned "+context.active_object.name)
                    context.scene['nextr_rig_properties_key'] = context.active_object.name+"_properties"
                    context.scene['nextr_rig_attributes_key'] = context.active_object.name+"_attributes"
            else:
                context.scene['active_object'] = context.active_object
                self.report({'INFO'}, "Pinned "+context.active_object.name)
        return {'FINISHED'}

class OPS_OT_GenerateRigLayers(Operator):
    bl_idname = 'nextr_debug.generate_rig_layers'
    bl_label = 'Generate rig layers'
    bl_description = 'Generates rig layers for the selected object'

    def execute(self, context):
        if context.active_object:
            o = get_edited_object(context)
            o.data['nextrrig_rig_layers'] = {}
            nextrrig_rig_layers = []
            for i in range(31):
                nextrrig_rig_layers.append([])

            for i in range(31):
                if 'nextr_rig_layers_visibility_'+str(i) in context.scene:
                    if context.scene['nextr_rig_layers_visibility_'+str(i)]:
                        row = i
                        if 'nextr_rig_layers_row_'+str(i) in context.scene:
                            row = context.scene['nextr_rig_layers_row_'+str(i)] - 1
                        
                        name = "Layer "+str(i+1)
                        if 'nextr_rig_layers_name_'+str(i) in context.scene:
                            name = context.scene['nextr_rig_layers_name_'+str(i)]
                        
                        layer_index = i
                        if 'nextr_rig_layers_index_'+str(i) in context.scene:
                            layer_index = context.scene['nextr_rig_layers_index_'+str(i)]
                        
                        nextrrig_rig_layers[row].append({'name':name, 'index':int(layer_index)})
            o.data['nextrrig_rig_layers']['nextrrig_rig_layers'] = nextrrig_rig_layers
            self.report({'INFO'}, "Added rig layers to "+o.name)
        else:
            self.report({'ERROR'}, "No active object!")
        return {'FINISHED'}

class OPS_OT_EditAttribute(Operator):
    bl_idname = 'nextr_debug.edit_attribute'
    bl_label = 'Edit attribute'
    bl_description = 'Edit attribute' 
    
    path : StringProperty(name="Path", description="RNA path of the attribute")
    panel_name : StringProperty()
    panels : EnumProperty(name="Panel", items=[('outfits','Outfits','Outfits panel',0),('body','Body','Body Panel',1),('rig','Rig Layers','Rig Layers Panel',2)])
    name : StringProperty(default='Default Value', name="Attribute's Name")
    attribute : {}
    visibility_data_path_expression: StringProperty(name="Expression", description="Expression used for data path evaluation. For example \"==2\" will show the attribute only when the data from the data path equal to 2")
    visibility_data_path : StringProperty(name='Data Path', description="Data path to the value you want to use as a driver for the visibility")
    variable_type : EnumProperty(name="Drive Visibility By", items=[('active_bone','Active Bone','Attribute depends on certain object',0),('data_path','Data Path','Attribute depends on certain the data path value ',1)])
    bone_pointer : StringProperty(name="Bone")
    visible_pointer : BoolProperty(name="Visible", default=True)
    data_path_block_pointer : StringProperty(name="Prop")
    
    def execute(self, context):
        o = get_edited_object(context)
        a = get_attribute_by_path(context,self.panel_name, self.path)
        
        if a:
            a['visibility'] = {}
            a['visibility']['variable'] = self.variable_type
            if self.variable_type == "active_bone":
                if hasattr(context.scene, 'nextr_rig_object_pointer') and hasattr(context.scene.nextr_rig_object_pointer, 'name'):
                    if context.scene.nextr_rig_object_pointer.name:
                        if context.scene.nextr_rig_object_pointer.type == "ARMATURE":
                            if not self.bone_pointer:
                                self.report({'WARNING'}, "You need to set the bone! Did not save!")
                                return {'CANCELLED'}
                            a['visibility']['object'] = context.scene.nextr_rig_object_pointer.name
                            a['visibility']['bone'] = self.bone_pointer
                        a['visibility']['value'] = self.visible_pointer
            else:
                prop_type = "objects"
                try:
                    prop_type = get_types()[context.scene['nextr_rig_visibility_prop_type']].lower()
                except:
                    pass
                new_data_path = 'bpy.data.'+prop_type+'["'+self.data_path_block_pointer+'"].'+self.visibility_data_path
                try: 
                    valid_path = eval(new_data_path) 
                except:
                   self.report({'ERROR'}, "Invalid Data Path!")
                   return {'CANCELLED'}
                a['visibility']['data_path'] = new_data_path
                a['visibility']['expression'] = self.visibility_data_path_expression
            a['name'] = self.name
            a['path'] = self.path
            
            new_attributes = []
            attributes_key = context.scene['nextr_rig_attributes_key']
            for attribute in o.data[attributes_key][self.panel_name]:
                if attribute['path'] == self.path:
                    if self.panels == self.panel_name:
                        new_attributes.append(a)
                    else:
                        different_panel_attributes = []
                        if self.panels in o.data[attributes_key]:
                            try:
                                different_panel_attributes = o.data[attributes_key][self.panels].to_list()
                                different_panel_attributes.append(a)
                            except:
                                different_panel_attributes = o.data[attributes_key][self.panels]
                                different_panel_attributes.append(a)    
                        else:
                            different_panel_attributes.append(a)
                        o.data[attributes_key][self.panels] = different_panel_attributes
                else:
                    new_attributes.append(attribute)
            o.data[attributes_key][self.panel_name] = new_attributes
        
        self.report({'INFO'}, "Successfully updated attribute")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.attribute = get_attribute_by_path(context, self.panel_name, self.path)   
        self.variable_type = "active_bone"     
        if not self.attribute:
            return {"CANCELED"}
        if 'visibility' in self.attribute:
            if self.attribute['visibility']['variable'] == "active_bone":
                try:
                    self.visible_pointer =  self.attribute['visibility']['value']
                    self.bone_pointer = self.attribute['visibility']['bone']
                    context.scene.nextr_rig_object_pointer = bpy.data.objects[self.attribute['visibility']['object']]
                except:
                    pass
            else:
                self.variable_type = "data_path"
                def get_data_from_string_data_path(context, data_path):
                    "sets all of the values to the correct value from the data path in string format"
                    data_path = data_path[9:]
                    prop_type = data_path[:data_path.find("[")]
                    prop_name = data_path[len(prop_type)+2:data_path.find('"]')]
                    data_path = data_path[len(prop_type+'["'+prop_name+'"].'):]
                    context.scene.nextr_rig_visibility_prop_type = "OP"+str(get_types().index(prop_type.upper()))
                    self.data_path_block_pointer = prop_name
                    self.visibility_data_path = data_path
                    
                try:
                    get_data_from_string_data_path(context,self.attribute['visibility']['data_path'])
                    self.visibility_data_path_expression = self.attribute['visibility']['expression']
                except:
                    pass
        else:
            self.visibility_data_path_expression = ""
            self.visibility_data_path = ""
            self.bone_pointer = ""
            context.scene.nextr_rig_object_pointer = None
        self.panels = self.panel_name
        self.name = self.attribute['name'] if self.attribute['name'] else "Default Value" 

        return context.window_manager.invoke_props_dialog(self, width=750)

    def draw(self, context):
        box = self.layout.box()
        box.label(text=self.name, icon="PREFERENCES")
        box.prop(self, "name", emboss=True)
        box.prop(self, "path", text="Path", icon="RNA")
        box.prop(self, 'panels')
        box_visibility = box.box()
        box_visibility.label(text="Visibility")
        box_visibility.prop(self, "variable_type")
        
        if self.variable_type == 'active_bone':
            box_visibility.prop(context.scene, 'nextr_rig_object_pointer')
            if hasattr(context.scene, 'nextr_rig_object_pointer') and hasattr(context.scene.nextr_rig_object_pointer,'type'):
                if context.scene.nextr_rig_object_pointer.type == "ARMATURE":
                    box_visibility.prop_search(self, 'bone_pointer', context.scene.nextr_rig_object_pointer.data, 'bones')
            box_visibility.prop(self, "visible_pointer", icon="RESTRICT_VIEW_OFF" if self.visible_pointer else "RESTRICT_VIEW_ON", text="Show when selected" if self.visible_pointer else "Show when NOT selected")
        elif self.variable_type == 'data_path':
            visibility_row = box_visibility.row(align=True)
            visibility_row.prop(context.scene, 'nextr_rig_visibility_prop_type', icon_only=True)
            prop_type = "objects"
            try:
                prop_type = get_types()[context.scene['nextr_rig_visibility_prop_type']].lower()
            except:
                pass
            visibility_row.prop_search(self, 'data_path_block_pointer', bpy.data, prop_type, text="")
            valid_path = True
            try: 
                valid_path = eval('bpy.data.'+prop_type+'["'+self.data_path_block_pointer+'"].'+self.visibility_data_path) 
            except:
                valid_path = False
            box_visibility.prop(self, "visibility_data_path", icon="CHECKMARK" if valid_path else "ERROR")
            box_visibility.prop(self, 'visibility_data_path_expression')
        if 'synced' in self.attribute:
            if self.attribute['synced']:
                box_synced = box.box()
                box_synced.label(text="Synced attributes")
                for synced in self.attribute['synced']:
                    row = box_synced.row(align=True)
                    row.label(text=synced)
                    op = row.operator(OPS_OT_RemoveSyncedAttribute.bl_idname, text="", icon="TRASH")
                    op.path = self.path
                    op.panel_name = self.panel_name
                    op.attribute_path = synced

class OPS_OT_RemoveSyncedAttribute(Operator):
    bl_idname = 'nextr_debug.remove_synced_attribute'
    bl_label = 'Remove synced attribute from the UI'
    bl_description = "Removes synced attribute from the UI and other synced attributes too"

    path : StringProperty()
    panel_name : StringProperty()
    attribute_path : StringProperty()

    def execute(self, context):
        a = get_attribute_by_path(context, self.panel_name, self.path)
        
        if a:
            synced = []
            synced = a['synced']
            a['synced'] = synced.remove(self.attribute_path)
            o = get_edited_object(context)
            new_attributes = []
            attributes_key = context.scene['nextr_rig_attributes_key']
            if attributes_key in o:
                for attribute in o[attributes_key][self.panel_name]:
                    if attribute['path'] == self.attribute_path:
                        new_attributes.append(a)
                    else:
                        new_attributes.append(attribute)
                o[attributes_key][self.panel_name] = new_attributes
            self.report({'INFO'}, 'Removed synced attribute')
            return {'FINISHED'}
            
        self.report({'INFO'}, "Couldn't find attribute with the path"+self.path)
        return {'CANCELED'}
class OPS_OT_RemoveAttribute(Operator):
    bl_idname = 'nextr_debug.remove_attribute'
    bl_label = 'Remove attribute from the UI'
    bl_description = "Removes attribute from the UI and other synced attributes too"
    path : StringProperty()
    panel_name : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        if context.active_object:
            o = get_edited_object(context)
            attributes_key = context.scene['nextr_rig_attributes_key']
            if attributes_key in o.data:
                if self.panel_name in o.data[attributes_key]:
                    att = o.data[attributes_key][self.panel_name]
                    new_att = []
                    for a in att:
                        if a['path'] != self.path:
                            new_att.append(a)
                    o.data[attributes_key][self.panel_name] = new_att
                    self.report({"INFO"}, 'Removed property')
        return {'FINISHED'}
class OPS_OT_AttributeChangePosition(Operator):
    bl_idname = 'nextr_debug.attribute_change_position'
    bl_label = "Change attributes position in the list"
    bl_description = "Changes position of the attribute in the current list"
    path : StringProperty()
    panel_name : StringProperty()
    direction : BoolProperty() #True moves up, False move down
    
    def execute(self, context):
        if context.active_object:
            o = get_edited_object(context)
            attributes_key = context.scene['nextr_rig_attributes_key']
            if attributes_key in o.data:
                if self.panel_name in o.data[attributes_key]:
                    att = o.data[attributes_key][self.panel_name]
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
                    o.data[attributes_key][self.panel_name] = att
        return {'FINISHED'}

class WM_MT_button_context(Menu):
    bl_label = "Add to UI"

    def draw(self, context):
        pass

class WM_MT_add_new_attribute(Menu):
    bl_label = "Add New Attribute"
    bl_idname = 'WM_MT_add_new_attribute_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Outfits Panel").panel_name = 'outfits'
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Body Panel").panel_name = 'body'
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Rig Layers Panel").panel_name = 'rig'

class WM_MT_sync_attribute_panel(Menu):
    bl_label = "Sync To Attribute"
    bl_idname = 'WM_MT_sync_attribute_panel'

    def draw(self, context):
        layout = self.layout
        layout.menu(WM_MT_sync_attribute_outfits_menu.bl_idname, text="Outfits Panel")
        layout.menu(WM_MT_sync_attribute_body_menu.bl_idname, text="Body Panel")
        layout.menu(WM_MT_sync_attribute_rig_menu.bl_idname, text="Rig Layers Panel")

class WM_MT_sync_attribute_outfits_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute_outfits_menu'
    
    def draw(self, context):
        self.layout.label(text='Attributes for Outfits Panel')
        render_attributes_in_menu(self.layout, context, 'outfits')

class WM_MT_sync_attribute_body_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute_body_menu'
    
    def draw(self, context):
        self.layout.label(text='Attributes for Body Panel')
        render_attributes_in_menu(self.layout, context, 'body')

class WM_MT_sync_attribute_rig_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute_rig_menu'
    
    def draw(self, context):
        self.layout.label(text='Attributes for Rig Layers Panel')
        render_attributes_in_menu(self.layout, context, 'rig')

def render_attributes(element, panel_name, attributes):
    "renders attributes to the UI based on the panels name"
    if panel_name in attributes:
        for p in attributes[panel_name]:
            row = element.row(align=True)
            delimiter = '][' if '][' in p['path'] else '.'
            offset = 1 if '][' in p['path'] else 0
            prop = p['path'][p['path'].rindex(delimiter)+1:]
            path = p['path'][:p['path'].rindex(delimiter)+offset]
            if p['name']:
                try:
                    row.prop(eval(path), prop, text=p['name'])
                except:
                    continue
            else:
                try:
                    row.prop(eval(path), prop)
                except:
                    continue
            op_edit = row.operator(OPS_OT_EditAttribute.bl_idname, icon="PREFERENCES", text="")
            op_edit.path = p['path']
            op_edit.panel_name = panel_name

            op_up = row.operator(OPS_OT_AttributeChangePosition.bl_idname, icon="TRIA_UP", text="")
            op_up.direction = True
            op_up.path = p['path']
            op_up.panel_name = panel_name

            op_down = row.operator(OPS_OT_AttributeChangePosition.bl_idname, icon="TRIA_DOWN", text="")
            op_down.direction = False
            op_down.path = p['path']
            op_down.panel_name = panel_name

            op = row.operator(OPS_OT_RemoveAttribute.bl_idname, icon="TRASH", text="")
            op.path = p['path']
            op.panel_name = panel_name
           

def render_attributes_in_menu(layout, context, panel):
    if context.active_object:
        o = get_edited_object(context)
        attributes_key = context.scene['nextr_rig_attributes_key']
        if panel in o.data[attributes_key]:
            for p in o.data[attributes_key][panel]:
                name = "Default Value"
                
                if p['name']:
                    name= p['name']
                op = layout.operator(OPS_OT_AddAttribute.bl_idname, text=name)
                op.parent_path = p['path']
                op.panel_name = panel
    return layout

def render_copy_data_path(self, context):
    attributes_key = context.scene['nextr_rig_attributes_key']
    if attributes_key in get_edited_object(context).data:
        layout = self.layout
        layout.separator()
        layout.label(text='Nextr Rig Debugger')
        layout.menu(WM_MT_add_new_attribute.bl_idname)
        layout.menu(WM_MT_sync_attribute_panel.bl_idname)

def sync_attribute_to_parent(attributes, parent_path, path):
   
    for i in range(len(attributes)):
        if attributes[i]['path'] == parent_path:
            if 'synced' in attributes[i]:
                syn = attributes[i]['synced'] #this thing is so unnecessary but I couldn't find a better solution, no matter what I did I couldn't add new attributes
                if not syn:
                    syn = []
                syn.append(path)
                attributes[i]['synced'] = syn
            else:
                syn = [] #here is it the same as few lines up
                syn.append(path)
                attributes[i]['synced'] = syn
    return attributes

def get_attribute_by_path(context, panel_name, path):
    if context.active_object:
        o = get_edited_object(context)
        attributes_key = context.scene['nextr_rig_attributes_key']
        if attributes_key in o.data:
            if panel_name in o.data[attributes_key]:
                for a in o.data[attributes_key][panel_name]:
                    if path == a['path']:
                        return a
    return False
   


classes = (VIEW3D_PT_nextr_rig_debug,
OPS_OT_PinActiveObject,
OPS_OT_Empty,
OPS_OT_EnableNextrRig,
OPS_OT_AddCollection,
VIEW3D_PT_nextr_rig_debug_rig_layers,
OPS_OT_GenerateRigLayers,
OPS_OT_AddAttribute,
WM_MT_button_context,
VIEW3D_PT_nextr_rig_debug_attributes,
WM_MT_add_new_attribute,
WM_MT_sync_attribute_panel,
WM_MT_sync_attribute_outfits_menu,
WM_MT_sync_attribute_body_menu,
WM_MT_sync_attribute_rig_menu,
OPS_OT_RemoveAttribute,
OPS_OT_EditAttribute,
OPS_OT_RemoveSyncedAttribute,
OPS_OT_AttributeChangePosition)
def setup_custom_keys():
    setattr(bpy.types.Scene, 'nextr_rig_properties_key', ui_setup_string(None, "Custom name for the properties key", "if you in the ui script changed what the key's value is", get_edited_object(bpy.context).name+'_properties'))
    setattr(bpy.types.Scene, 'nextr_rig_attributes_key', ui_setup_string(None, "Custom name for the attributes key", "if you in the ui script changed what the key's value is", get_edited_object(bpy.context).name+'_attributes'))

def setup_rig_layers():
    for i in range(31):
        setattr(bpy.types.Scene, 'nextr_rig_layers_visibility_'+str(i), ui_setup_toggle(None, "","If layers is visible in the UI",False))
        setattr(bpy.types.Scene, 'nextr_rig_layers_name_'+str(i), ui_setup_string(None, "","Name of the layer in the UI","Layer "+str(i+1)))
        setattr(bpy.types.Scene, 'nextr_rig_layers_row_'+str(i), ui_setup_int(None, "","On which row is the layer going to be in the UI",i,1,32))
        setattr(bpy.types.Scene, 'nextr_rig_layers_index_'+str(i), ui_setup_int(None, "","Which rig layers is going to be affected by this toggle",i,0,31))

def ui_setup_enum_options(array, description_prefix,icons=[]):
    "helper function used to setup enum options with icons"
    options = []
    for i in range(len(array)):
        icon = ""
        if i < len(icons):
            icon = icons[i]
        options.append(("OP"+str(i), array[i], description_prefix+": "+ array[i], icon,i))
    return options

def get_types():
    "return all of the types we want to support"
    return ["ACTIONS", "ARMATURES", "BRUSHES", "CAMERAS", "CACHE_FILES", "CURVES", "FONTS", "GREASE_PENCILS", "COLLECTIONS", "IMAGES", "SHAPE_KEYS", "LIGHTS", "LIBRARIES", "LINESTYLES", "LATTICES", "MASKS", "MATERIALS", "METABALLS", "MESHES", "MOVIECLIPS", "NODE_GROUPS", "OBJECTS", "PAINT_CURVES", "PALETTES", "PARTICLES", "LIGHTPROBES", "SCENES", "SOUNDS", "SPEAKERS", "TEXTS", "TEXTURES", "HAIR", "POINTCLOUD", "VOLUMES", "WINDOW_MANAGERS", "WORLDS", "WORKSPACES"]
     
def setup_visibility_driver_prop():
    "set ups enum used to determine ID-Blocks type with icons"
    icons = ["ACTION", "ARMATURE_DATA", "BRUSH_DATA", "CAMERA_DATA", "FILE_CACHE", "CURVE_DATA", "FONT_DATA", "GREASEPENCIL", "OUTLINER_COLLECTION", "IMAGE_DATA", "SHAPEKEY_DATA", "LIGHT", "LIBRARY_DATA_DIRECT", "LINE_DATA", "LATTICE_DATA", "MOD_MASK", "MATERIAL", "META_DATA", "MESH_DATA", "TRACKER", "NODETREE", "OBJECT_DATA", "CURVE_BEZCURVE", "COLOR", "PARTICLE_DATA", "OUTLINER_OB_LIGHTPROBE", "SCENE", "SOUND", "SPEAKER", "TEXT", "TEXTURE", "HAIR", "POINTCLOUD_DATA", "VOLUME_DATA", "WINDOW", "WORLD", "WORKSPACE"]
    setattr(bpy.types.Scene, 'nextr_rig_visibility_prop_type', ui_setup_enum(None,"","Type of ID-Block which will  be used", ui_setup_enum_options(get_types(), "Data ID-Block which will be used", icons),21))

def register():
    setup_custom_keys()
    setup_rig_layers()
    setup_visibility_driver_prop()
    for c in classes:
        register_class(c)
    bpy.types.WM_MT_button_context.append(render_copy_data_path)
    bpy.types.Scene.nextr_rig_object_pointer = PointerProperty(type=bpy.types.Object,name="Object", description="Select an object or an Armature to use it as a driver for visibility of the attribute.")

def unregister():
    bpy.types.WM_MT_button_context.remove(render_copy_data_path)
    for c in classes:
        unregister_class(c)
    


if __name__ == "__main__":
    register()
