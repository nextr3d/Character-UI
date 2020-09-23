"""
# How to #
    # Naming

        Set the name in the char_info, this name represents name of the master Collection and name of the rig and name of the body object(it also has to have _body suffix), it's case sensitive

        For example:
            char_info = {
                "name": "Ellie"
            }
            collection name : Ellie
            rig name : Ellie
            body name: Ellie_body

    # Outfits
        Outfits are located in the '[char_info["name"]] Outifts' collection ie 'Ellie Outfits'
        Each outfit is also located in its own collection which can be named however you want but keep in mind that this name is also going to be used in the UI
    # Rig layers
        to use named rig layers you have to add custom prop to the armature.
        Select aramture -> click Object Data Properties (the one with the stickman icon) -> scroll down to Custom Properties sub menu -> click Add 
        -> name the prop 'rig_layers' and insert this pattern: [Face,False,Arms]
        This pattern results in a creation of two buttons. Keyword False skips one layer.
        Layers are from 0 - 31, first row is 0 - 15.
        Those two buttons are going to be toggling only the first (0) and the third (2) layer

"""
bl_info = {
    "name": "Nextr Rig UI",
    "description": "Script for creating Nextr Rig UI",
    "author": "Nextr3D",
    "version": (3, 0, 0),
    "blender": (2, 90, 0)
}
#adds credits to the Links panel
user_info = {
    "Hosting by Smutba.se":{
        "Twitter" : ('USER','twitter.com/Smutbase1'),
        "Patreon" : ('FUND', 'patreon.com/sfmlab')
    },
    "Model by Nextr3D":{
        "Twitter" : ('USER','twitter.com/nextr3d'),
        "Patreon" : ('FUND', 'patreon.com/nextr3d')
    },
  
}
char_info = {
    "name" : "Ellie",
    "outfits" : [],
    "layer_list": [],
    "visible_hair":''
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

class DepsGraphUpdates():
    def post_depsgraph_update(self, context):
        DepsGraphUpdates.update_bone_layers(context)

    @classmethod
    def update_bone_layers(self, context):
        rig = Nextr_Rig.get_rig()
        for index in range(32):
            if hasattr(rig.data.nextrrig_properties, str(index)+"_layer_toggle"):
                rig.data.nextrrig_properties[str(index)+"_layer_toggle"] = rig.data.layers[index]

class Nextr_Rig(bpy.types.PropertyGroup):
    
    """ class handling all of the UI creation """

    def select_nextrrig_armature(self):
        "selects first nextr rig aramture in the scene"
        rigs = self.get_rigs()
        bpy.context.view_layer.objects.active = rigs[0]
        
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
        if active_object.type == 'ARMATURE' and 'nextrrig_properties' in active_object.data:
            return active_object
        return False
    
    def test_update_func(self, context):
        rig = self.get_rig()
        rig.data['update'] = 1
        # rig.data['nextrrig_properties']['test_bool'] = not rig.data['nextrrig_properties']['test_bool']
       
    @classmethod
    def __init__(self):
        "prepares data for the panel"
        print("----------------------------------------------------------------------")
        start_time = time.time()
        print('Building rig.')
        selected_object =  bpy.context.view_layer.objects.active #save the selected object
        self.select_nextrrig_armature(self) #select one of nextr rig aramtures
        rig = self.get_rig()
        if rig:
            rig.data['update'] = 0
            self.build_ui()
        
        bpy.context.view_layer.objects.active = selected_object #select the originaly selected object
        print('Building took:', time.time() - start_time,'seconds')
    @classmethod
    def build_ui(self):
        "executes all of the methods which build the UI"
        self.get_outfits()
        self.get_bone_layers()
    @classmethod
    def get_bone_layers(self):
        "creates buttons for switching bone layers"
        rig = self.get_rig()
        nextr_props = rig.data
        print(nextr_props['rig_layers'], hasattr(nextr_props, "rig_layers"))
        for index in range(32):
            if  nextr_props['rig_layers']:
                layers =nextr_props["rig_layers"][1:-1].split(",")  
                if len(layers) > index and layers[index] != "False":
                    self.ui_setup_toggle(str(index)+"_layer_toggle", self.update_bone_layers, layers[index], "Enables/Disables bone layer", rig.data.layers[index])
            else:
                self.ui_setup_toggle(str(index)+"_layer_toggle", self.update_bone_layers, "Layer - "+str((index + 1)), "Enables/Disables bone layer", rig.data.layers[index])
    @classmethod
    def get_outfits(self):
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
                print("Available outfits:", available_outfits)
                self.ui_setup_enum("outfit_enum", self.update_outfits, "Outfit", "Available outfits", self.create_enum_options(available_outfits))
                self.ui_setup_outfit_buttons(outfit_collection.children.keys())
    @classmethod
    def ui_setup_outfit_buttons(self, collections):
        rig = self.get_rig()
        for collection in collections:
            objects = bpy.data.collections[collection].objects
            for o in objects:
                default = False
#                if hasattr(rig.data['nextrrig_properties'], o.name_full.replace(" ", "_")+"_outfit_toggle"):
                default = rig.data['nextrrig_properties'][o.name_full.replace(" ", "_")+"_outfit_toggle"]
                print(o.name_full.replace(" ", "_")+"_outfit_toggle" ,default)
                self.ui_setup_toggle(o.name_full.replace(" ", "_")+"_outfit_toggle", self.update_outfit_piece, o.name_full, "Toggles outfit piece on and off", default)

    "method for creating options for blender UI enums"
    @staticmethod
    def create_enum_options(array, description_prefix = "Empty description for:"):
        items = []
        for array_item in array:
            items.append(("OP"+str(array.index(array_item)), array_item, description_prefix+" "+array_item))
        return items

    @classmethod
    def ui_setup_enum(self, property_name, update_function, name = "Name", description = "Empty description", items = [], default = 0):
                
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
        """method for easier creation of toggles (buttons)

        Keyword arguments:

        property_name -- name of the toggle 

        update_function -- function executed on click

        name -- name of the toggle visible in the UI (default Name)

        description -- description what does the toggle toggles (default Empty description)

        default -- default state of the toggle (default False)
        """
        rig_data = self.get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):    
            print(property_name, default)
            rig_data.nextrrig_properties[property_name] =  default
            prop =  BoolProperty(
                name = name,
                description = description,
                update = update_function,
                default =  default
            )
            setattr(self, property_name, prop) 
    @classmethod
    def get_active_outfit(self):
        collections = bpy.data.collections
        rig = self.get_rig()
        data = rig.data
        nextr_props = data.nextrrig_properties
        for collection in collections:
            if rig.name_full in collection.objects:
                outfit_collection = collection.children[collection.name+" Outfits"].children
                index = nextr_props['outfit_enum']
                outfits = collection.children[collection.name+" Outfits"].children
                while "hidden" in outfits.values()[index].name_full:
                    index = index + 1
                        
                return outfit_collection[index]
                
    def update_outfit_piece(self, context):
        print(self.get_active_outfit().name_full)
        c = self.get_active_outfit()
        nextr_props = self.get_rig().data.nextrrig_properties 
        for o in c.objects:
            o.hide_render = o.hide_viewport = not nextr_props[o.name_full+"_outfit_toggle"]
        
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
        return None
    def update_bone_layers(self, context):
        rig = self.get_rig()
        for index in range(32):
            if hasattr(rig.data.nextrrig_properties, str(index)+"_layer_toggle"):
                rig.data.layers[index] = rig.data.nextrrig_properties[str(index)+"_layer_toggle"]
            else:
                rig.data.layers[index] = False
        print("update")
# -------
#  Panels
# -------
class UI_PT_NextrRigPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = char_info["name"]
   
    @classmethod
    def poll(cls, context):
        #return True
        if(context.object != None and context.object in Nextr_Rig.get_rigs()):
            return True

class UI_PT_OutiftsPanel(UI_PT_NextrRigPanel):
    "Outfits panel"
    bl_label = "Outfits"
    bl_idname = "UI_PT_OutiftsPanel"
    
    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        # draws enum to the ui
        layout.prop(nextr_props, "outfit_enum")

        collections = bpy.data.collections
        for collection in collections:
            if context.object.name_full in collection.objects:
                
                index = nextr_props['outfit_enum']
                outfits = collection.children[collection.name+" Outfits"].children
                while "hidden" in outfits.values()[index].name_full:
                    index = index + 1
                
                outfit_collection = outfits[index]
                for item in outfit_collection.objects:
                    layout.prop(nextr_props, item.name_full.replace(" ", "_")+"_outfit_toggle", toggle=True)
class UI_PT_RigLayers(UI_PT_NextrRigPanel):
    "Rig layers panel"
    bl_label = "Rig Layers"
    bl_idname = "UI_PT_RigLayers"

    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        for index in range(32):
            if hasattr(nextr_props, str(index)+"_layer_toggle"):
                layout.prop(nextr_props, str(index)+"_layer_toggle", toggle=True)
       
class UI_PT_InfoPanel(UI_PT_NextrRigPanel):
    "Links panel"
    bl_label = "Info"
    bl_idname = "UI_PT_InfoPanel"
             
    def draw(self, context):
        layout = self.layout
        scene = context.scene  
        layout.separator()
        layout.operator('scene.empty', text='Nextr Rig UI v'+str(bl_info['version'][0])+'.'+str(bl_info['version'][1])+'.'+str(bl_info['version'][2]), icon='SETTINGS', emboss=False,depress=True)
        
        for user in user_info:
            layout.separator()
            layout.operator('scene.empty', text=user,  emboss=False,depress=True)  
            for link in user_info[user]:
                layout.operator("wm.url_open", text=link, icon=user_info[user][link][0]).url = user_info[user][link][1]        
class OPS_PT_Empty(bpy.types.Operator):
    "for empty operator used only as text"
    bl_idname = 'scene.empty'
    bl_label = 'Text'
    bl_description = 'Header'
# ----------------
#    Registration
# ----------------

classes = (
    Nextr_Rig,
    UI_PT_OutiftsPanel,
    UI_PT_RigLayers,
    UI_PT_InfoPanel,
    OPS_PT_Empty
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

if __name__ == "__main__":
    register()
    Nextr_Rig.__init__()

# bpy.app.handlers.depsgraph_update_pre.append(Nextr_Rig.pre_depsgraph_update)
bpy.app.handlers.depsgraph_update_post.append(DepsGraphUpdates.post_depsgraph_update)