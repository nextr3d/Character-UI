import bpy, time, re
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatVectorProperty

"""
available variables
character_id
character_id_key
"""
custom_prefix = "CharacterUI_"
#script variables


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
        for i in enumerate(items):
            print(i)
            if hasattr(i[1], "type"):
                CharacterUIUtils.create_driver(ch, i[1], 'hide_viewport', "characterui!=%i"%(i[0]), "%s.hair_enum"%(key))
                CharacterUIUtils.create_driver(ch, i[1], 'hide_render', "characterui!=%i"%(i[0]), "%s.hair_enum"%(key))

            else:
                for c in i[1].objects:
                    CharacterUIUtils.create_driver(ch, c, 'hide_viewport', "characterui!=%i"%(i[0]), "%s.hair_enum"%(key))
                    CharacterUIUtils.create_driver(ch, c, 'hide_render', "characterui!=%i"%(i[0]), "%s.hair_enum"%(key))

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
    def create_driver(driver_id,driver_target, driver_path, driver_expression, prop_name):
       
        driver_target.driver_remove(driver_path)
        driver = driver_target.driver_add(driver_path)
        driver = driver.driver
        driver.type = "SCRIPTED"
        driver.expression = driver_expression
        var = driver.variables.new()
        var.name                 = 'characterui'
        var.targets[0].id        = driver_id
        var.targets[0].data_path = prop_name
        
        return

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
            ch = CharacterUIUtils.get_character()
            props = getattr(ch, "%s%s"%(custom_prefix, character_id))
            hair_row = box.row(align=True)
            hair_row.prop(props, "hair_enum")
            hair_row.prop(props, "hair_lock", icon="LOCKED" if props["hair_lock"] else "UNLOCKED", toggle=True )

        
        
class VIEW3D_PT_physics_panel(VIEW3D_PT_characterUI):
    "Physics Sub-Panel"
    bl_label = "Physics (Experimental)"
    bl_idname = "VIEW3D_PT_physics_panel"
    bl_parent_id = "VIEW3D_PT_body"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="physics")


class VIEW3D_PT_rig_layers(VIEW3D_PT_characterUI):
    bl_label = "Rig"
    bl_idname = "VIEW3D_PT_rig_layers_"

    def draw(self, context):
        box = self.layout.column().box()

classes = (
    VIEW3D_PT_outfits,
    VIEW3D_PT_rig_layers,
    VIEW3D_PT_body,
    VIEW3D_PT_physics_panel,
    VIEW3D_PT_links,
    CharacterUI
)

def register():
    for c in classes:
        register_class(c)

    setattr(bpy.types.Object, "%s%s"%(custom_prefix, character_id), bpy.props.PointerProperty(type=CharacterUI))

    CharacterUI.initialize()

def unregister():
   pass

if __name__ in ['__main__', 'builtins']:
    # __main__ when executed through the editor
    #builtins when executed after generation of the script
    register()
