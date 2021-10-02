import bpy, time, re
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatVectorProperty

"""
available variables
character_id
character_id_key
rig_layers_key
links_key
"""
#script variables
custom_prefix = "CharacterUI_"


bl_info = {
    "name": "Character UI",
    "description": "Script rendering UI for your character",
    "author": "Nextr3D",
    "version": (5, 0, 0),
    "blender": (3, 0, 0)
}

class CharacterUI(PropertyGroup):
    @staticmethod
    def initialize():
        ch = CharacterUIUtils.get_character()
        key = "%s%s"%(custom_prefix, character_id)
        if ch:
            if key not in ch:
                ch[key] = {}
            if "hair_collection" in ch.data and ch.data["hair_collection"]:
                CharacterUI.build_hair(ch, key)
   
    @classmethod
    def build_hair(self, ch, key):
        data = getattr(ch ,key) 
        default_value = 0
        if 'hair_lock' in data:
            default_value = data['hair_lock']
        self.ui_setup_toggle("hair_lock", None, "", "Locks hair so it's not changed by the outfit", default_value)
        hair_collection = ch.data["hair_collection"]
        items = [*hair_collection.children, *hair_collection.objects]
        names = [o.name for o in items]

        def create_hair_drivers(target, index):
            CharacterUIUtils.create_driver(ch, target, 'hide_viewport', "characterui!=%i"%(index), "%s.hair_enum"%(key))
            CharacterUIUtils.create_driver(ch, target, 'hide_render', "characterui!=%i"%(index), "%s.hair_enum"%(key))
        
        def recursive_hair(hair_items, index = -1):
            for i in enumerate(hair_items):
                print(i)
                if hasattr(i[1], "type"):
                    create_hair_drivers(i[1], i[0] if index < 0 else index)
                else:
                    recursive_hair([*i[1].children, *i[1].objects], i[0])

        recursive_hair(items)
        default = 0
        if "hair_enum" in data:
            default = data["hair_enum"]
        try:
            self.ui_setup_enum('hair_enum', None, "Hairdos", "Switch between different hairdos", self.create_enum_options(names, "Enables: "), default)
        except:
            pass
        



    @classmethod
    def ui_setup_toggle(self, property_name, update_function, name='Name', description='Empty description', default=False):
        "method for easier creation of toggles (buttons)"
        print(property_name, default)
        prop = BoolProperty(
            name=name,
            description=description,
            update=update_function,
            default=default
        )
        setattr(self, property_name, prop)
    
    @classmethod   
    def ui_setup_enum(self, property_name, update_function, name="Name", description="Empty description", items=[], default=0):
        "method for easier creation of enums (selects)"
        prop = EnumProperty(
            name=name,
            description=description,
            items=items,
            update=update_function,
            default='OP'+str(default)
        )
        setattr(self, property_name, prop)

    @staticmethod
    def create_enum_options(array, description_prefix="Empty description for:"):
        "method for creating options for blender UI enums"
        items = []
        for array_item in array:
            items.append(("OP"+str(array.index(array_item)),array_item, description_prefix+" "+array_item))
        return items
class CharacterUIUtils:
    @staticmethod
    def get_character():
        for o in bpy.data.objects:
            if character_id_key in o.data:
                if o.data[character_id_key] == character_id:
                    return o
        return False
    @staticmethod
    def get_props_from_character():
        ch = CharacterUIUtils.get_character()
        return getattr(ch, "%s%s"%(custom_prefix, character_id))

    @staticmethod
    def create_driver(driver_id,driver_target, driver_path, driver_expression, prop_name):
       
        driver_target.driver_remove(driver_path)
        driver = driver_target.driver_add(driver_path)
        driver = driver.driver
        driver.type = "SCRIPTED"
        driver.expression = driver_expression
        var = driver.variables.new()
        var.name = 'characterui'
        var.targets[0].id = driver_id
        var.targets[0].data_path = prop_name
        
        return
    @staticmethod
    def safe_render(parent, data, prop, **kwargs):
        if hasattr(data, prop):
            parent.prop(data, prop, **kwargs)
class VIEW3D_PT_characterUI(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character UI"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch and ch == context.object:
            return True
        return False

class VIEW3D_PT_outfits(VIEW3D_PT_characterUI):
    bl_label = "Outfits"
    """no idea if this is the correct way but classes with identical ids get destroyed 
    so this way multiple classes with same(or at least similar) functionality can exist at the same time"""
    bl_idname = "VIEW3D_PT_outfits"

    def draw(self, context):
        layout = self.layout

class VIEW3D_PT_links(VIEW3D_PT_characterUI):
    bl_label = "Links"
    bl_idname = "VIEW3D_PT_links_"

    def draw(self, context):
        layout = self.layout
        layout.separator()


class VIEW3D_PT_body(VIEW3D_PT_characterUI):
    "Body panel"
    bl_label = "Body"
    bl_idname = "VIEW3D_PT_body"

    def draw(self, context):
        layout = self.layout
        if CharacterUIUtils.get_character():
            box = layout.box()
            props = CharacterUIUtils.get_props_from_character()
            hair_row = box.row(align=True)
            CharacterUIUtils.safe_render(hair_row, props, "hair_enum")
            if hasattr(props, "hair_lock"):
                CharacterUIUtils.safe_render(hair_row, props, "hair_lock", icon="LOCKED" if props.hair_lock else "UNLOCKED", toggle=True )

        
class VIEW3D_PT_physics_panel(VIEW3D_PT_characterUI):
    "Physics Sub-Panel"
    bl_label = "Physics (Experimental)"
    bl_idname = "VIEW3D_PT_physics_panel"
    bl_parent_id = "VIEW3D_PT_body"
    
    @classmethod
    def poll(self, context):
        return False
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="physics")
        

class VIEW3D_PT_rig_layers(VIEW3D_PT_characterUI):
    bl_label = "Rig"
    bl_idname = "VIEW3D_PT_rig_layers_"
    
    @classmethod
    def poll(slef, context):
        ch = CharacterUIUtils.get_character()
        return ch and ch.type == "ARMATURE"

    def draw(self, context):
        box = self.layout.column().box()
        box.label(text="Layers")
        ch = CharacterUIUtils.get_character() 
        if ch:
            if rig_layers_key in ch.data:
                #sorting "stolen" from CloudRig https://gitlab.com/blender/CloudRig/-/blob/a16df00d5da51d19f720f3e5fe917a84a85883a0/generation/cloudrig.py
                layer_data = ch.data[rig_layers_key]
                rig_layers = [dict(l) for l in layer_data]

                for i, l in enumerate(rig_layers):
                    # When the Rigify addon is not enabled, finding the original index after sorting is impossible, so just store it.
                    l['index'] = i
                    if 'row' not in l:
                        l['row'] = 1

                sorted_layers = sorted(rig_layers, key=lambda l: l['row'])
                sorted_layers = [l for l in sorted_layers if 'name' in l and l['name']!=" "]
                current_row_index = -1
                row = box.row()
                for rig_layer in sorted_layers:
                    if rig_layer['name'] in ["", " "]: continue
                    if rig_layer['name'].startswith("$"): continue
                    
                    if rig_layer['row'] > current_row_index:
                        current_row_index = rig_layer['row']
                        row = box.row()
                    row.prop(ch.data, "layers", index=rig_layer['index'], toggle=True, text=rig_layer['name'])

class VIEW3D_PT_links(VIEW3D_PT_characterUI):
    bl_label = "Links"
    bl_idname = "VIEW3D_PT_links"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.label(text='Nextr Rig UI v'+str(bl_info['version'][0])+'.'+str(
            bl_info['version'][1])+'.'+str(bl_info['version'][2]), icon='SETTINGS')
        col = layout.column()
        data = CharacterUIUtils.get_character().data
        if links_key in data:
            for section in data[links_key].to_dict():
                box = col.box()
                box.label(text=section)
                column = box.column(align=True)
                for link in data[links_key][section].to_dict():
                    try:
                        column.operator("wm.url_open", text=link, icon=data[links_key][section][link][0]).url = data[links_key][section][link][1]
                    except:
                        column.operator("wm.url_open", text=link).url = data[links_key][section][link][1]


classes = [
    VIEW3D_PT_outfits,
    VIEW3D_PT_rig_layers,
    VIEW3D_PT_body,
    VIEW3D_PT_physics_panel,
    VIEW3D_PT_links,
    CharacterUI
]

def register():
    for c in classes:
        register_class(c)

    setattr(bpy.types.Object, "%s%s"%(custom_prefix, character_id), bpy.props.PointerProperty(type=CharacterUI))

    CharacterUI.initialize()

def unregister():
    for c in reversed(classes):
        unregister_class(c)
    
    delattr(bpy.types.Object, "%s%s"%(custom_prefix, character_id))
if __name__ in ['__main__', 'builtins']:
    # __main__ when executed through the editor
    #builtins when executed after generation of the script
    register()
