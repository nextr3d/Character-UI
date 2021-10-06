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
            if "body_object" in ch.data and ch.data["body_object"]:
                CharacterUI.remove_body_modifiers_drivers(ch)
                CharacterUI.remove_body_shape_keys_drivers(ch)
            if "hair_collection" in ch.data and ch.data["hair_collection"]:
                CharacterUI.build_hair(ch, key)
            if "outfits_collection" in ch.data and ch.data["outfits_collection"]:
                CharacterUI.build_outfits(ch, key)
   
    @classmethod
    def build_outfits(self, ch, key):
        "Builds outfit selector for the UI"
        data = getattr(ch ,key)

        outfits = ch.data["outfits_collection"].children.keys()
        options = self.create_enum_options(outfits, "Show outfit: ")
        default = 0 
        if "outfits_enum" in data:
            default = data["outfits_enum"]
        try:
            self.ui_setup_enum("outfits_enum", CharacterUI.update_hair_by_outfit, "Outfits", "Changes outfits", options, default)
        except:
            pass
        self.ui_build_outfit_buttons(ch, key)
    @classmethod
    def remove_body_modifiers_drivers(self, ch):
        "removes drivers from modifiers"
        if "character_ui_masks" in ch.data:
            for m in ch.data["character_ui_masks"]:
                if m["modifier"] in ch.data["body_object"].modifiers:
                    ch.data["body_object"].modifiers[m["modifier"]].driver_remove("show_viewport")
                    ch.data["body_object"].modifiers[m["modifier"]].driver_remove("show_render")
    
    @classmethod
    def remove_body_shape_keys_drivers(self, ch):
        "removes drivers from shape keys"
        if "character_ui_shape_keys" in ch.data:
            for s in ch.data["character_ui_shape_keys"]:
                if s["shape_key"] in ch.data["body_object"].data.shape_keys.key_blocks:
                    ch.data["body_object"].data.shape_keys.key_blocks[s["shape_key"]].driver_remove("value")

    @classmethod
    def ui_build_outfit_buttons(self, ch, key):
        "Builds individual button for outfit pieces, their locks and creates drivers"
        data = getattr(ch ,key)
        index = 0
        for collection in ch.data["outfits_collection"].children:
            objects = collection.objects
            for o in objects:
                default = False
                default_lock = False
                name = o.name_full.replace(" ", "_")+"_outfit_toggle"
                if name in data and name+"_lock" in data:
                    default = data[name]
                    default_lock = data[name+"_lock"]
                    
                        
                self.ui_setup_toggle(name, None, o.name_full, "Toggles outfit piece on and off", default)
                self.ui_setup_toggle(name+"_lock", None, "", "Locks the outfit piece to be visible even when changing outfits", default_lock)
                variables = [{"name": "chui_outfit", "path": "%s.outfits_enum"%(key)},{"name": "chui_object", "path": "%s.%s"%(key,name)}]
                lock_expression = "chui_lock==1"
                expression = "not (chui_object == 1 and (chui_outfit ==%i or chui_lock==1))"%(index)
                if o.parent:
                    expression = "not (chui_object == 1 and chui_parent == 0)"
                    variables.append({"name": "chui_parent", "path": "hide_viewport", "driver_id": o.parent})
                else:
                    variables.append({"name": "chui_lock", "path": "%s.%s_lock"%(key,name)})
                CharacterUIUtils.create_driver(ch, o, 'hide_viewport', expression, variables)
                CharacterUIUtils.create_driver(ch, o, 'hide_render', expression, variables)
                if "character_ui_masks" in ch.data and "body_object" in ch.data:
                    if ch.data["body_object"]:
                        body = ch.data["body_object"]
                        for mask in ch.data["character_ui_masks"]:
                            if mask["driver_id"] == o and mask["modifier"] in body.modifiers:
                                CharacterUIUtils.create_driver(o, body.modifiers[mask["modifier"]], "show_viewport", "chui_object==0", [{"name": "chui_object", "path":"hide_viewport" }])
                                CharacterUIUtils.create_driver(o, body.modifiers[mask["modifier"]], "show_render", "chui_object==0", [{"name": "chui_object", "path":"hide_render" }])
                if "character_ui_shape_keys" in ch.data and "body_object" in ch.data:
                    if ch.data["body_object"]:
                        body = ch.data["body_object"]
                        for shape_key in ch.data["character_ui_shape_keys"]:
                            if shape_key["driver_id"] == o and shape_key["shape_key"] in body.data.shape_keys.key_blocks:
                                CharacterUIUtils.create_driver(o, body.data.shape_keys.key_blocks[shape_key["shape_key"]], "value", "chui_object==0", [{"name": "chui_object", "path":"hide_render" }] )

            index += 1

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
            CharacterUIUtils.create_driver(ch, target, 'hide_viewport', "characterui_hair!=%i"%(index), [{"name": "characterui_hair", "path": "%s.hair_enum"%(key)}])
            CharacterUIUtils.create_driver(ch, target, 'hide_render', "characterui_hair!=%i"%(index), [{"name": "characterui_hair", "path": "%s.hair_enum"%(key)}])
        
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
            self.ui_setup_enum('hair_enum', None, "Hairstyle", "Switch between different hairdos", self.create_enum_options(names, "Enables: "), default)
        except:
            pass

    @classmethod
    def ui_setup_toggle(self, property_name, update_function, name='Name', description='Empty description', default=False):
        "method for easier creation of toggles (buttons)"
        
        props = CharacterUIUtils.get_props_from_character()
        props[property_name] = default

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
        props = CharacterUIUtils.get_props_from_character()
        props[property_name] = default

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

    @staticmethod
    def update_hair_by_outfit(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            props = CharacterUIUtils.get_props_from_character()
            outfit_name = ch.data["outfits_collection"].children[props["outfits_enum"]].name
            if "hair_collection" in ch.data and ch.data["hair_collection"]:
                if not props["hair_lock"]:
                    hairstyles = [*ch.data["hair_collection"].children, *ch.data["hair_collection"].objects]
                    for hairstyle in enumerate(hairstyles):
                        if outfit_name in hairstyle[1].name:
                            props["hair_enum"] = hairstyle[0]
                
        
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
    def create_driver(driver_id,driver_target, driver_path, driver_expression, variables):
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
    def safe_render(parent, data, prop, **kwargs):
        if hasattr(data, prop):
            parent.prop(data, prop, **kwargs)
    @staticmethod
    def render_outfit_piece(o, element, props, is_child = False):
        "recursively render outfit piece buttons"
        row = element.row(align=True)
        name = o.name.replace(" ", "_")+"_outfit_toggle"
        if o.data:
            CharacterUIUtils.safe_render(row, props, name, toggle=True, icon="TRIA_DOWN" if (props[name] and ("settings" in o.data or len(o.children))) else ("TRIA_RIGHT" if not props[name] and ("settings" in o.data or len(o.children)) else "NONE" ))
        else:
            CharacterUIUtils.safe_render(row, props, name, toggle=True, icon="TRIA_DOWN" if (props[name] and (len(o.children))) else ("TRIA_RIGHT" if not props[name] and (len(o.children)) else "NONE" ))
        
        if not is_child:
            CharacterUIUtils.safe_render(row, props, name+"_lock",icon="LOCKED" if props[name+"_lock"] else "UNLOCKED")

        if not o.data:
            if len(o.children) and props[name]:
                settings_box = element.box()
                settings_box.label(text="Items", icon="MOD_CLOTH")
                for child in o.children:
                    child_name = child.name.replace(" ", "_")+"_outfit_toggle"
                    if hasattr(props, child_name):
                        CharacterUIUtils.render_outfit_piece(child, settings_box, props, True)

            return

        if (len(o.children) or "settings" in o.data) and props[name]:
            if len(o.children):
                settings_box = element.box()
                settings_box.label(text="Items", icon="MOD_CLOTH")
                for child in o.children:
                    child_name = child.name.replace(" ", "_")+"_outfit_toggle"
                    if hasattr(props, child_name):
                        CharacterUIUtils.render_outfit_piece(child, settings_box, props, True)
class VIEW3D_PT_characterUI(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character UI"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        return ch and ch == context.object

class VIEW3D_PT_outfits(VIEW3D_PT_characterUI):
    bl_label = "Outfits"
    """no idea if this is the correct way but classes with identical ids get destroyed 
    so this way multiple classes with same(or at least similar) functionality can exist at the same time"""
    bl_idname = "VIEW3D_PT_outfits"

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        props = CharacterUIUtils.get_props_from_character()
        if ch and props:
            if ch.data["outfits_collection"]:
                outfits = ch.data["outfits_collection"]
                if len(outfits.children) > 1:
                    CharacterUIUtils.safe_render(layout, props, "outfits_enum")
                box = layout.box()
                for o in outfits.children[props['outfits_enum']].objects:
                    is_top_child = True #True because if no parent than it's the top child
                    if not o.parent == None:
                        is_top_child = not o.users_collection[0] == o.parent.users_collection[0] #parent is in different collection so it has to 
                    if is_top_child:
                        CharacterUIUtils.render_outfit_piece(o,box, props)
                    
                    locked_pieces = {}
                    
                    for i, c in enumerate(outfits.children):
                        pieces = []
                        for o in c.objects:
                            if i != props["outfits_enum"]:
                                name = o.name.replace(" ", "_")+"_outfit_toggle"
                                if props[name+"_lock"]:
                                    pieces.append(o)
                        if len(pieces):
                            locked_pieces[c.name] = pieces

                    for n,pcs in locked_pieces.items():
                        box.label(text=n)
                        for p in  pcs:
                            CharacterUIUtils.render_outfit_piece(p, box, props)

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
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if rig_layers_key not in ch.data:
            return False
        return ch and ch.type == "ARMATURE" and len(ch.data[rig_layers_key])

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
