bl_info = {
    "name": "Nextr Rig UI",
    "description": "Script for creating Nextr Rig UI",
    "author": "Nextr3D",
    "version": (3, 2, 0),
    "blender": (2, 90, 1)
}
#adds credits to the Links panel
user_info = {
    "Hosting by Smutba.se":{
        "Twitter" : ('USER','twitter.com/Smutbase1'),
        "Patreon" : ('FUND', 'patreon.com/sfmlab'),
        "Website" : ('URL', 'smutba.se')
    },
    "Model by Nextr3D":{
        "Twitter" : ('USER','twitter.com/nextr3d'),
        "Patreon" : ('FUND', 'patreon.com/nextr3d')
    }
}
char_info = {
    "name" : "Lara"
}
import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )
from rna_prop_ui import rna_idprop_ui_prop_get
import webbrowser
import time
def get_objects_from_collection_recursive(collection):
    "goes through all of the collections in the hierarchy and returns it's children objects"
    new_objects = collection.objects
    for coll in collection.children:
        new_objects = [*new_objects, *get_objects_from_collection_recursive(coll)]
    return new_objects

class DepsGraphUpdates():
    def post_depsgraph_update(self, context):
        rig = Nextr_Rig.get_rig()
        if hasattr(rig, "data") and hasattr(rig.data, "nextrrig_properties"):
            o = DepsGraphUpdates()
            o.update_outfit_piece()
            # o.update_bone_layers() it probably doesn't have to be here, at least for this version
            o.update_hair()
    @classmethod
    def update_outfit_piece(self):
        c = Nextr_Rig.get_active_outfit()
        if c:
            nextr_props = Nextr_Rig.get_rig().data.nextrrig_properties 
            for o in c.objects:
                name = o.name_full.replace(" ","_")+"_outfit_toggle"
                if name in nextr_props:
                    if o.hide_render == nextr_props[name]:
                        o.hide_render = o.hide_viewport = not nextr_props[name]
                        Nextr_Rig.update_object_mask(o)
    @classmethod
    def update_bone_layers(self):
        rig = Nextr_Rig.get_rig()
        for index in range(32):
            if hasattr(rig.data.nextrrig_properties, str(index)+"_layer_toggle"):
                rig.data.nextrrig_properties[str(index)+"_layer_toggle"] = rig.data.layers[index]
    @classmethod
    def update_hair(self):
        rig = Nextr_Rig.get_rig()
        if hasattr(rig.data.nextrrig_properties, "hair_enum"):
            hair_collection = bpy.data.collections[rig.name+" Hair"]
            items = [*hair_collection.children, *hair_collection.objects]
            for item in items:
                if not item.hide_viewport:
                    item.hide_viewport = item.hide_render = True
            items[rig.data.nextrrig_properties['hair_enum']].hide_render = items[rig.data.nextrrig_properties['hair_enum']].hide_viewport = False
class Nextr_Rig(bpy.types.PropertyGroup):
    """ class handling all of the UI creation """

    def select_nextrrig_armature(self):
        "selects first nextr rig aramture in the scene"
        rigs = self.get_rigs()
        if len(rigs):
            bpy.context.view_layer.objects.active = rigs[0]
            return True
        return False
        
    def get_rigs():
        "Find all nextr rigs in the current view layer"

        ret = []
        armatures = [o for o in bpy.context.view_layer.objects if o.type=='ARMATURE']
        for o in armatures:
            if "nextrrig_properties" in o.data:           
                ret.append(o)
        return ret
    @classmethod
    def get_rig(self):
        "returns currently selected rig"
        active_object = bpy.context.view_layer.objects.active
        if hasattr(active_object, 'type'):
            if active_object.type == 'ARMATURE' and 'nextrrig_properties' in active_object.data:
                return active_object
        return False
    @classmethod
    def get_body_object(self):
        # returns body object
        if bpy.data.objects[char_info['name']+" Body"]:
            return bpy.data.objects[char_info['name']+" Body"]
        return False
       
    @classmethod
    def __init__(self):
        "prepares data for the panel"
        start_time = time.time()
        selected_object =  bpy.context.view_layer.objects.active #save the selected object
         #select one of nextr rig aramtures
        if self.select_nextrrig_armature(self):
            rig = self.get_rig()
            if rig:
                rig.data['update'] = 0
                self.build_ui()
            bpy.context.view_layer.objects.active = selected_object #select the originaly selected object
            print('Building took:', time.time() - start_time,'seconds')
        else:
            print("No Nextr Rig character in the scene :(")
    @classmethod
    def build_ui(self):
        "executes all of the methods which build the UI"
        self.get_outfits()
        self.get_hair()
        self.get_all_attributes()
        self.get_bone_layers()
        self.get_physics()
    @classmethod
    def get_all_attributes(self):
        rig = self.get_rig()
        objects = get_objects_from_collection_recursive(bpy.data.collections[char_info['name']])
        for o in objects:
            previous_index = o.active_material_index
            o.active_material_index = index = 0
            while o.active_material:
                mat = o.active_material
                for node in mat.node_tree.nodes:
                    if char_info['name'] in node.name:
                        attribute_setting = node.name[len(char_info['name']):][1:-1].split(',')
                        default = node.outputs[0].default_value
                        if attribute_setting[2] == "t":
                            self.ui_setup_toggle(node.name, self.update_attributes, attribute_setting[1], "Update "+attribute_setting[1]+" attribute", default == 1.0)
                        elif attribute_setting[2] == "i":
                            self.ui_setup_int(node.name, self.update_attributes, attribute_setting[1], "Update "+attribute_setting[1]+" attribute", int(default), int(attribute_setting[3]), int(attribute_setting[4]))
                        else:
                            self.ui_setup_float(node.name, self.update_attributes, attribute_setting[1], "Update "+attribute_setting[1]+" attribute", default)
                o.active_material_index = index = index + 1
            o.active_material_index = previous_index
    @classmethod
    def get_hair(self):
        if char_info['name']+" Hair" in bpy.data.collections:
            rig = self.get_rig()
            default_value = 0
            if 'hair_lock' in rig.data.nextrrig_properties:
                default_value = rig.data.nextrrig_properties['hair_lock']
            self.ui_setup_toggle("hair_lock", None, "", "Locks hair so it's not changed by the outfit", default_value)
            hair_collection = bpy.data.collections[char_info['name']+" Hair"]
            items = [*hair_collection.children, *hair_collection.objects]
            names = [o.name for o in items]
            default = 0

            if hasattr(rig.data.nextrrig_properties, "hair_enum"):
                default = rig.data.nextrrig_properties["hair_enum"]
            self.ui_setup_enum('hair_enum', None, "Hairdos", "Switch between different hairdos", self.create_enum_options(names, "Enables: "), default)
    @classmethod
    def get_bone_layers(self):
        "creates buttons for switching bone layers"
        rig = self.get_rig()
        nextr_props = rig.data
        for index in range(32):
            if "rig_layers" in  nextr_props:
                layers =nextr_props["rig_layers"][1:-1].split(",")  
                if len(layers) > index and layers[index] != "False":
                    self.ui_setup_toggle(str(index)+"_layer_toggle", self.update_bone_layers, layers[index], "Enables/Disables bone layer", rig.data.layers[index])
            else:
                self.ui_setup_toggle(str(index)+"_layer_toggle", self.update_bone_layers, "Layer - "+str((index + 1)), "Enables/Disables bone layer", rig.data.layers[index])
    @classmethod
    def get_outfits(self):
        "gets all of the outfits, name of the collections not containing hidden"
        collections = bpy.data.collections
        rig = self.get_rig()
        for collection in collections:
            if rig.name_full in collection.objects:
                outfit_collection = collection.children[char_info['name'] + ' Outfits']
                outfits = outfit_collection.children.keys()
                available_outfits = []
                for item in outfits:
                    if "hidden" not in item:
                        available_outfits.append(item)
                default_value = 0
                if 'outfit_enum' in rig.data.nextrrig_properties:
                    default_value = rig.data.nextrrig_properties['outfit_enum']
                self.ui_setup_enum("outfit_enum", self.update_outfits, "Outfit", "Available outfits", self.create_enum_options(available_outfits), default_value)
                self.ui_setup_outfit_buttons(outfit_collection.children.keys())
    @classmethod
    def get_physics(self):
        rig = self.get_rig()
        nextrrig_properties = rig.data.nextrrig_properties
        if char_info['name']+" Body Physics" in bpy.data.collections:
            cages = bpy.data.collections[char_info['name']+" Body Physics"].objects
            for i in range(len(cages)):
                o = cages[i]
                "create slider for quality"
                default_quality = 5
                if o.name.replace(" ","_")+"_quality" in nextrrig_properties:
                    default_quality = nextrrig_properties[o.name.replace(" ","_")+"_quality"]
                self.ui_setup_int(o.name.replace(" ","_")+"_quality", self.update_physics, "Quality", "Sets the quality of the simulation for "+o.name, default_quality, 0, 200)
                "create slider for frame start"
                default_frame_start = bpy.data.scenes[bpy.context.scene.name].frame_start
                if o.name.replace(" ","_")+"_frame_start" in nextrrig_properties:
                    default_frame_start = nextrrig_properties[o.name.replace(" ","_")+"_frame_start"]
                self.ui_setup_int(o.name.replace(" ","_")+"_frame_start", self.update_physics, "Frame Start", "Sets the Starting Frame of the simulation for "+o.name, default_frame_start,0,1048573)
                "create slider for frame end"
                default_frame_end = bpy.data.scenes[bpy.context.scene.name].frame_end
                if o.name.replace(" ","_")+"_frame_end" in nextrrig_properties:
                    default_frame_end = nextrrig_properties[o.name.replace(" ","_")+"_frame_end"]
                self.ui_setup_int(o.name.replace(" ","_")+"_frame_end", self.update_physics, "Frame End", "Sets the Ending Frame of the simulation for "+o.name, default_frame_end,0,1048574)
                
    @classmethod
    def ui_setup_outfit_buttons(self, collections):
        rig = self.get_rig()
        for collection in collections:
            objects = bpy.data.collections[collection].objects
            for o in objects:
                default = False
                if o.name_full.replace(" ", "_")+"_outfit_toggle" in rig.data.nextrrig_properties:
                    default = rig.data['nextrrig_properties'][o.name_full.replace(" ", "_")+"_outfit_toggle"]
                self.ui_setup_toggle(o.name_full.replace(" ", "_")+"_outfit_toggle", None, o.name_full, "Toggles outfit piece on and off", default)

    "method for creating options for blender UI enums"
    @staticmethod
    def create_enum_options(array, description_prefix = "Empty description for:"):
        items = []
        for array_item in array:
            items.append(("OP"+str(array.index(array_item)), array_item, description_prefix+" "+array_item))
        return items

    @classmethod
    def ui_setup_enum(self, property_name, update_function, name = "Name", description = "Empty description", items = [], default = 0):
        "method for easier creation of enums (selects)"      
        rig_data = self.get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):
            rig_data['nextrrig_properties'][property_name] = default  
            prop =  EnumProperty(
                name = name,
                description = description,
                items = items,
                update = update_function,
                default = 'OP'+str(default)
            )
                
            setattr(self, property_name, prop) 
    @classmethod
    def ui_setup_toggle(self, property_name,update_function,name = 'Name', description = 'Empty description', default = False):           
        "method for easier creation of toggles (buttons)"
        rig_data = self.get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):    
            rig_data.nextrrig_properties[property_name] =  default
            prop =  BoolProperty(
                name = name,
                description = description,
                update = update_function,
                default =  default
            )
            setattr(self, property_name, prop) 

    @classmethod
    def ui_setup_int(self, property_name,update_function,name = 'Name', description = 'Empty description', default = 0, min = 0, max = 1):           
        "method for easier creation of ints (sliders)"
        rig_data = self.get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):    
            rig_data.nextrrig_properties[property_name] =  default
            prop =  IntProperty(
                name = name,
                description = description,
                update = update_function,
                default =  default,
                max = max,
                min = min
            )
            setattr(self, property_name, prop) 

    @classmethod
    def ui_setup_float(self, property_name, update_function, name = "Name", description = 'Empty description', default = 0.0):
        "method for easier creation of floats (sliders)"
        rig_data = self.get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):    
            rig_data.nextrrig_properties[property_name] =  default
            prop = FloatProperty(
                name = name,
                description = description,
                update = update_function,
                default = default
            )
            setattr(self, property_name, prop)

    @classmethod
    def get_active_outfit(self):
        "return name of the active outfit (collection name)"
        collections = bpy.data.collections
        rig = self.get_rig()
        data = rig.data
        nextr_props = data.nextrrig_properties
        for collection in collections:
            if rig.name_full in collection.objects:
                outfit_collection = collection.children[collection.name+" Outfits"].children
                if 'outfit_enum' in nextr_props:
                    index = nextr_props['outfit_enum']
                    outfits = collection.children[collection.name+" Outfits"].children
                    while "hidden" in outfits.values()[index].name_full:
                        index = index + 1
                            
                    return outfit_collection[index]
                return False
    @classmethod
    
    def render_attribute(self, item):
        attribute_setting = item[len(char_info['name']):][1:-1].split(',')
        rig = self.get_rig()
        if len(attribute_setting) == 7:
            if attribute_setting[5] == "Outfits":
                return attribute_setting[6] == bpy.data.collections[rig.name+" Outfits"].children[rig.data.nextrrig_properties["outfit_enum"]].name
        return True
    @classmethod
    def update_object_mask(self, clothing):
        "updates all of the masks on the body"        
        body = self.get_body_object()
        if clothing.name+" Mask" in body.modifiers:
            body.modifiers[clothing.name+" Mask"].show_render = body.modifiers[clothing.name+" Mask"].show_viewport = not clothing.hide_render
        elif clothing.name+"_mask" in body.modifiers:
            body.modifiers[clothing.name+"_mask"].show_render = body.modifiers[clothing.name+"_mask"].show_viewport = not clothing.hide_render
              
    def update_outfit_piece(self, context):
        c = self.get_active_outfit()
        if c:
            nextr_props = self.get_rig().data.nextrrig_properties 
            for o in c.objects:
                o.hide_render = o.hide_viewport = not nextr_props[o.name_full+"_outfit_toggle"]
                self.update_object_mask(o)
        
    def update_outfits(self, context):
        collections = bpy.data.collections
        data = context.object.data
        nextr_props = data.nextrrig_properties
        for collection in collections:
            if context.object.name_full in collection.objects:
                outfit_collection = collection.children[collection.name+" Outfits"].children
                for c in outfit_collection:
                    c.hide_viewport = c.hide_render = True
                index = nextr_props['outfit_enum']
                outfits = collection.children[collection.name+" Outfits"].children
                while "hidden" in outfits.values()[index].name_full:
                    index = index + 1
                visible_collection = outfit_collection[index]
                visible_collection.hide_render = visible_collection.hide_viewport = False
                if not nextr_props["hair_lock"]:
                    self.update_hair_by_outfit(self, context.object.name_full, visible_collection.name)
    def update_hair_by_outfit(self,context,name, outfit_name):
        "updates hairdos when hair_enum is not locked"
        hairdos = bpy.data.collections[name+" Hair"].objects
        for i in range(0,len(hairdos)):
            if "outfit" in hairdos[i]:
                if hairdos[i]["outfit"] == outfit_name:                 
                    self.get_rig().data.nextrrig_properties.hair_enum = "OP"+str(i)                                     
            else:
                if outfit_name in hairdos[i].name:
                    self.get_rig().data.nextrrig_properties.hair_enum = "OP"+str(i)

    def update_bone_layers(self, context):
        "updates bone layers"
        rig = self.get_rig()
        for index in range(32):
            if hasattr(rig.data.nextrrig_properties, str(index)+"_layer_toggle"):
                rig.data.layers[index] = rig.data.nextrrig_properties[str(index)+"_layer_toggle"]
            else:
                rig.data.layers[index] = False
    def update_hair(self, context):
        "updates hairdos"
        collections = bpy.data.collections
        data = context.object.data
        nextr_props = data.nextrrig_properties
        for collection in collections:
            if context.object.name_full in collection.objects:
                hair_collection = [*collection.children[collection.name+" Hair"].children, *collection.children[collection.name+" Hair"].objects]
                for c in hair_collection:
                    c.hide_viewport = c.hide_render = True
                index = nextr_props['hair_enum']
                hair_collection[index].hide_viewport = hair_collection[index].hide_render = False
    def update_attributes(self, context):
        "updates all of the attributes in the materials belonging to the rig"
        rig = self.get_rig()
        # path to attribute, holy shit! bpy.data.materials['body_arms'].node_tree.nodes['Ellie[UI_PT_BodyPanel,Tatto,toggle]'].outputs['Value'].default_value
        objects = get_objects_from_collection_recursive(bpy.data.collections[char_info['name']])
        attributes = {}
        for o in objects:
            previous_index = o.active_material_index
            o.active_material_index = index = 0
            while o.active_material:
                mat = o.active_material
                for node in mat.node_tree.nodes:
                    if node.name in rig.data.nextrrig_properties:
                        node.outputs[0].default_value = rig.data.nextrrig_properties[node.name]
                o.active_material_index = index = index + 1
            o.active_material_index = previous_index
    def update_physics(self, context):
        print(context.object.name)
        nextr_props = context.object.data.nextrrig_properties
        if context.object.name+" Body Physics" in bpy.data.collections:
            for o in bpy.data.collections[context.object.name+" Body Physics"].objects:
                for m in o.modifiers:
                    if m.type == "CLOTH":
                        m.settings.quality = nextr_props[o.name.replace(" ","_")+"_quality"]
                        m.point_cache.frame_start = nextr_props[o.name.replace(" ","_")+"_frame_start"]
                        m.point_cache.frame_end = nextr_props[o.name.replace(" ","_")+"_frame_end"]
        print("update physcis")
    def update_bake_physics(self, context):
        print(dir(context))
#  Panels
class UI_PT_NextrRigPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = char_info["name"]
   
    @classmethod
    def poll(cls, context):
        if(context.object != None and context.object in Nextr_Rig.get_rigs()):
            return True

class UI_PT_OutfitsPanel(UI_PT_NextrRigPanel):
    "Outfits panel"
    bl_label = "Outfits"
    bl_idname = "UI_PT_OutfitsPanel"
    
    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        # Outfit box
        box = layout.box()
        box.label(text="Outfit", icon="MATCLOTH")
        box.prop(nextr_props, "outfit_enum")
        if hasattr(nextr_props,"outfit_enum"):
            index = nextr_props['outfit_enum']
            outfits = bpy.data.collections[char_info['name']+" Outfits"].children
            while "hidden" in outfits.values()[index].name_full:
                index = index + 1
            
            column = box.column()
            outfit_collection = outfits[index]
            for item in outfit_collection.objects:
                name = item.name_full.replace(" ", "_")+"_outfit_toggle"
                if hasattr(nextr_props, name):
                    column.prop(nextr_props, name, toggle=True)
        # Hair box, renders only if hair enum exists
        if hasattr(nextr_props, "hair_enum"):
            box = layout.box()
            box.label(text="Hair", icon="HAIR")
            row = box.row(align=True)
            row.prop(nextr_props, "hair_enum")

            icon = "UNLOCKED"
            if nextr_props["hair_lock"]:
                icon = "LOCKED"
            row.prop(nextr_props,"hair_lock", toggle=True, icon=icon)
        
        items = []
        for item in nextr_props.keys():
            if item in nextr_props and self.bl_idname[6:] in item :
                items.append(item)
        if len(items):
            box = layout.box()
            box.label(text="Attributes", icon="PRESET")
            for item in items:
                
                if hasattr(nextr_props, item) and Nextr_Rig.render_attribute(item):
                    box.prop(nextr_props, item, toggle=True)
class UI_PT_RigLayers(UI_PT_NextrRigPanel):
    "Rig layers panel"
    bl_label = "Rig Layers"
    bl_idname = "UI_PT_RigLayers"

    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        box = layout.box()
        box.label(text='Rig Layers', icon='ARMATURE_DATA')
        column = box.column()
        for index in range(32):
            if hasattr(nextr_props, str(index)+"_layer_toggle"):
                column.prop(nextr_props, str(index)+"_layer_toggle", toggle=True)
       
class UI_PT_InfoPanel(UI_PT_NextrRigPanel):
    "Links panel"
    bl_label = "Info"
    bl_idname = "UI_PT_InfoPanel"
             
    def draw(self, context):
        layout = self.layout
        scene = context.scene  
        layout.separator()
        layout.operator('nextr.empty', text='Nextr Rig UI v'+str(bl_info['version'][0])+'.'+str(bl_info['version'][1])+'.'+str(bl_info['version'][2]), icon='SETTINGS', emboss=False,depress=True)
        col = layout.column()
        for user in user_info:
            box = col.box()
            box.operator('nextr.empty', text=user,  emboss=False,depress=True)  
            column = box.column(align=True)
            for link in user_info[user]:
                column.operator("wm.url_open", text=link, icon=user_info[user][link][0]).url = user_info[user][link][1]        

class UI_PT_BodyPanel(UI_PT_NextrRigPanel):
    "Body panel"
    bl_label = "Body"
    bl_idname = "UI_PT_BodyPanel"
             
    def draw(self, context):
        
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties

        items = []
        for item in nextr_props.keys():
            if item in nextr_props and self.bl_idname[6:] in item :
                items.append(item)
        if len(items):
            box = layout.box()
            box.label(text="Attributes", icon="PRESET")
            for item in items:
                if hasattr(nextr_props, item):
                    box.prop(nextr_props, item, toggle=True)
        
class UI_PT_BodyPhysicsPanel(UI_PT_NextrRigPanel):
    "Physics Sub-Panel"
    bl_label = "Physics"
    bl_idname = "UI_PT_BodyPhysicsPanel"
    bl_parent_id = "UI_PT_BodyPanel"

    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        if context.object.name+" Body Physics" in bpy.data.collections:
            for o in bpy.data.collections[context.object.name+" Body Physics"].objects:
                box = layout.box()
                baked = False
                info = ""
                for m in o.modifiers:
                    if m.type == "CLOTH":
                        baked = m.point_cache.is_baked
                        info = m.point_cache.info
                box.label(text=o.name.replace("Cage","").replace(".L", "Left").replace(".R","Right"), icon="PREFERENCES")
                column = box.column(align=True)
                column.active = not baked
                column.enabled = not baked
                column.prop(nextr_props, o.name.replace(" ","_")+"_quality")
                column.prop(nextr_props, o.name.replace(" ","_")+"_frame_start")
                column.prop(nextr_props, o.name.replace(" ","_")+"_frame_end")
                box.operator('nextr.bake', text="Delete Bake" if baked else "Bake").object_name = o.name
                box.operator('nextr.empty', text=info, icon="INFO", depress=True, emboss=False)

                
class OPS_PT_Empty(bpy.types.Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'

class OPS_PT_BakePhysics(bpy.types.Operator):
    bl_idname = "nextr.bake"
    bl_description = "Bake Physics"
    bl_label = "Bake"

    object_name: bpy.props.StringProperty()
    def execute(self, context ):
        for m in bpy.data.objects[self.object_name].modifiers:
            if m.type == "CLOTH" and not m.point_cache.is_baked:
                if not m.show_viewport:
                    self.report({'WARNING'}, "Modifier is not visible in the viewport, baking will have no effect!")
                else:
                    override = {'scene': context.scene, 'active_object': bpy.data.objects[self.object_name], 'point_cache': m.point_cache}
                    bpy.ops.ptcache.bake(override, bake=True)
                    self.report({'INFO'}, "Done baking physics for: "+self.object_name)
            elif m.type == "CLOTH" and m.point_cache.is_baked:
                override = {'scene': context.scene, 'active_object': bpy.data.objects[self.object_name], 'point_cache': m.point_cache}
                bpy.ops.ptcache.free_bake(override)
                self.report({'INFO'}, "Removed physics cache for: "+self.object_name)
        return {'FINISHED'}
class OPS_PT_HideModifier(bpy.types.Operator):
    bl_idname = "nextr.hide_modifier"
    bl_description = "Hides modifier"
    

# ----------------
#    Registration
# ----------------

classes = (
    Nextr_Rig,
    UI_PT_OutfitsPanel,
    UI_PT_BodyPanel,
    UI_PT_RigLayers,
    UI_PT_InfoPanel,
    OPS_PT_Empty,
    UI_PT_BodyPhysicsPanel,
    OPS_PT_BakePhysics
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Armature.nextrrig_properties = bpy.props.PointerProperty(type=Nextr_Rig)
    
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

register()
Nextr_Rig.__init__()
bpy.app.handlers.depsgraph_update_post.append(DepsGraphUpdates.post_depsgraph_update)
