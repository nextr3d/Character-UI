import bpy
import time
import re
from bpy.types import Operator, Panel, PropertyGroup, Object
from bpy.utils import register_class, unregister_class
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatVectorProperty

"""
available variables
character_id
character_id_key
rig_layers_key
links_key
custom_label
"""
# script variables
custom_prefix = "CharacterUI_"
attributes_key = "%satt_%s" % (custom_prefix, character_id)

bl_info = {
    "name": "Character UI Script",
    "description": "Script rendering UI for your character",
    "author": "nextr",
    "version": (5, 3, 0),
    "blender": (3, 0, 0),
    "branch": "outfits"
}


class CharacterUI(PropertyGroup):
    @staticmethod
    def initialize():
        t = time.time()
        ch = CharacterUIUtils.get_character()
        key = "%s%s" % (custom_prefix, character_id)
        if ch:
            print("Building UI for %s" % (ch.name))
            if key not in ch:
                ch[key] = {}
            if "body_object" in ch.data and ch.data["body_object"]:
                CharacterUI.remove_visibility_drivers_drivers(ch)
                print("Removed drivers")
                CharacterUI.setup_visibility_drivers(ch)
            if "hair_collection" in ch.data and ch.data["hair_collection"]:
                CharacterUI.build_hair(ch, key)
            if "outfits_collection" in ch.data and ch.data["outfits_collection"]:
                CharacterUI.build_outfits(ch, key)
            print("Finished building UI in %s" % (time.time()-t))

    @classmethod
    def build_outfits(self, ch, key):
        "Builds outfit selector for the UI"
        data = getattr(ch, key)

        outfits = ch.data["outfits_collection"].children.keys()
        options = self.create_enum_options(outfits, "Show outfit: ")
        default = 0
        if "outfits_enum" in data:
            default = data["outfits_enum"]
        try:
            self.ui_setup_enum("outfits_enum", CharacterUI.update_hair_by_outfit,
                               "Outfits", "Changes outfits", options, default)
        except:
            pass
        self.ui_build_outfit_buttons(ch, key)
        print("Finished building outfits")

    @classmethod
    def remove_visibility_drivers_drivers(self, ch):
        "removes drivers from modifiers"
        for key in ["character_ui_masks", "character_ui_shape_keys"]:
            if key in ch.data:
                for item in ch.data[key]:
                    if "name" not in item:
                        name = item["modifier"] if "modifier" in item else item["shape_key"]
                        item["name"] = name
                        if "modifier" in item:
                            del item["modifier"]
                        elif "shape_key" in item:
                            del item["shape_key"]
                    if item["name"] in ch.data["body_object"].modifiers:
                        if key == "character_ui_masks":
                            ch.data["body_object"].modifiers[item["name"]
                                                             ].driver_remove("show_viewport")
                            ch.data["body_object"].modifiers[item["name"]
                                                             ].driver_remove("show_render")
                        else:
                            ch.data["body_object"].data.shape_keys.key_blocks[item["name"]].driver_remove(
                                "value")

    @classmethod
    def ui_build_outfit_buttons(self, ch, key):
        "Builds individual button for outfit pieces, their locks and creates drivers"
        data = getattr(ch, key)
        index = 0
        for collection in ch.data["outfits_collection"].children:
            objects = collection.objects
            for o in objects:
                default = False
                default_lock = False
                name = o.name_full.replace(
                    '.', "-").replace(" ", "_")+"_outfit_toggle"
                if name in data and name+"_lock" in data:
                    default = data[name]
                    default_lock = data[name+"_lock"]

                toggle_label = o.name_full

                if "chui_outfit_piece_settings" in o:
                    if "prefix" in o["chui_outfit_piece_settings"]:
                        prefix = o["chui_outfit_piece_settings"]["prefix"]
                        if prefix != "" and prefix in toggle_label and toggle_label.index(prefix) == 0:
                            toggle_label = toggle_label[len(prefix):]

                self.ui_setup_toggle(
                    name, None, toggle_label, "Toggles outfit piece on and off", default)
                self.ui_setup_toggle(
                    name+"_lock", None, "", "Locks the outfit piece to be visible even when changing outfits", default_lock)
                variables = [{"name": "chui_outfit", "path": "%s.outfits_enum" % (
                    key)}, {"name": "chui_object", "path": "%s.%s" % (key, name)}]
                lock_expression = "chui_lock==1"
                expression = "not (chui_object == 1 and (chui_outfit ==%i or chui_lock==1))" % (
                    index)

                is_top_child = False
                if o.parent:
                    # parent is in different collection so it has to
                    if not o.users_collection[0] == o.parent.users_collection[0]:
                        is_top_child = True
                else:
                    is_top_child = True

                if is_top_child:
                    variables.append(
                        {"name": "chui_lock", "path": "%s.%s_lock" % (key, name)})
                else:
                    expression = "not (chui_object == 1 and chui_parent == 0)"
                    variables.append(
                        {"name": "chui_parent", "path": "hide_viewport", "driver_id": o.parent})

                CharacterUIUtils.create_driver(
                    ch, o, 'hide_viewport', expression, variables)
                CharacterUIUtils.create_driver(
                    ch, o, 'hide_render', expression, variables)

            index += 1

    @classmethod
    def setup_visibility_drivers(self, ch):
        for key in ["character_ui_masks", "character_ui_shape_keys"]:
            if key in ch.data and "body_object" in ch.data:
                if ch.data["body_object"]:
                    body = ch.data["body_object"]
                    for item in ch.data[key]:
                        expression = ""
                        variables_viewport = []
                        variables_render = []
                        if type(item["driver_id"]) == Object:
                            new_items = [item["driver_id"]]
                            item["driver_id"] = new_items

                        for (i, o) in enumerate(item["driver_id"]):
                            expression = "%schui_object_%i==0%s" % (
                                expression, i, " or " if i < len(item["driver_id"]) - 1 else "")
                            variables_viewport.append({"name":  "chui_object_%i" % (
                                i), "path": "hide_viewport", "driver_id": o})
                            variables_render.append({"name":  "chui_object_%i" % (
                                i), "path": "hide_render", "driver_id": o})

                        if key == "character_ui_masks":
                            if "name" not in item:
                                name = item["modifier"]
                                item["name"] = name
                                del item["modifier"]
                            CharacterUIUtils.create_driver(
                                None, body.modifiers[item["name"]], "show_viewport", expression, variables_viewport)
                            CharacterUIUtils.create_driver(
                                None, body.modifiers[item["name"]], "show_render", expression, variables_render)
                        else:
                            if "name" not in item:
                                name = item["shape_key"]
                                item["name"] = name
                                del item["shape_key"]
                            CharacterUIUtils.create_driver(
                                None, body.data.shape_keys.key_blocks[item["name"]], "value", expression, variables_render)

    @classmethod
    def build_hair(self, ch, key):
        data = getattr(ch, key)
        default_value = 0
        if 'hair_lock' in data:
            default_value = data['hair_lock']
        self.ui_setup_toggle(
            "hair_lock", None, "", "Locks hair so it's not changed by the outfit", default_value)
        hair_collection = ch.data["hair_collection"]
        items = [*hair_collection.children, *hair_collection.objects]
        names = [o.name for o in items]

        def create_hair_drivers(target, index):
            CharacterUIUtils.create_driver(ch, target, 'hide_viewport', "characterui_hair!=%i" % (
                index), [{"name": "characterui_hair", "path": "%s.hair_enum" % (key)}])
            CharacterUIUtils.create_driver(ch, target, 'hide_render', "characterui_hair!=%i" % (
                index), [{"name": "characterui_hair", "path": "%s.hair_enum" % (key)}])

        def recursive_hair(hair_items, index=-1):
            for i in enumerate(hair_items):
                if hasattr(i[1], "type"):
                    create_hair_drivers(i[1], i[0] if index < 0 else index)
                else:
                    recursive_hair([*i[1].children, *i[1].objects], i[0])

        recursive_hair(items)
        default = 0
        if "hair_enum" in data:
            default = data["hair_enum"]
        try:
            self.ui_setup_enum('hair_enum', None, "Hairstyle", "Switch between different hairdos",
                               self.create_enum_options(names, "Enables: "), default)
        except:
            pass
        print("Finished building hair")

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
            items.append(("OP"+str(array.index(array_item)),
                         array_item, description_prefix+" "+array_item))
        return items

    @staticmethod
    def update_hair_by_outfit(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            props = CharacterUIUtils.get_props_from_character()
            outfit_name = ch.data["outfits_collection"].children[props["outfits_enum"]].name
            if "hair_collection" in ch.data and ch.data["hair_collection"]:
                if not props["hair_lock"]:
                    hairstyles = [*ch.data["hair_collection"].children,
                                  *ch.data["hair_collection"].objects]
                    for hairstyle in enumerate(hairstyles):
                        if outfit_name in hairstyle[1].name:
                            props["hair_enum"] = hairstyle[0]


class CharacterUIUtils:
    @staticmethod
    def get_character():
        for o in bpy.data.objects:
            if str(type(o.data)) != "<class 'NoneType'>":  # empties...
                if character_id_key in o.data:
                    if o.data[character_id_key] == character_id:
                        return o
        return False

    @staticmethod
    def get_props_from_character():
        ch = CharacterUIUtils.get_character()
        return getattr(ch, "%s%s" % (custom_prefix, character_id))

    @staticmethod
    def create_driver(driver_id, driver_target, driver_path, driver_expression, variables):
        "TODO: same exact code is in the add-on, make it that it's only once in the whole codebase"
        driver_target.driver_remove(driver_path)
        driver = driver_target.driver_add(driver_path)

        def setup_driver(driver, addition_path=""):
            driver.type = "SCRIPTED"
            driver.expression = driver_expression
            for variable in variables:
                local_driver_id = variable["driver_id"] if "driver_id" in variable else driver_id
                var = driver.variables.new()
                var.name = variable["name"]
                var.targets[0].id_type = local_driver_id.rna_type.name.upper()
                var.targets[0].id = local_driver_id
                var.targets[0].data_path = "%s%s" % (
                    variable["path"], addition_path)
        if type(driver) == list:
            for d in enumerate(driver):
                setup_driver(d[1].driver, "[%i]" % (d[0]))
        else:
            setup_driver(driver.driver)

    @staticmethod
    def safe_render(parent, data, prop, **kwargs):
        if hasattr(data, prop):
            parent.prop(data, prop, **kwargs)

    @staticmethod
    def render_outfit_piece(o, element, props, is_child=False):
        "recursively render outfit piece buttons"
        row = element.row(align=True)
        name = o.name.replace(".", "-").replace(" ", "_")+"_outfit_toggle"
        if o.data:
            CharacterUIUtils.safe_render(row, props, name, toggle=True, icon="DOWNARROW_HLT" if (props[name] and ("settings" in o.data or len(
                o.children))) else ("RIGHTARROW" if not props[name] and ("settings" in o.data or len(o.children)) else "NONE"))
        else:
            CharacterUIUtils.safe_render(row, props, name, toggle=True, icon="DOWNARROW_HLT" if (props[name] and (
                len(o.children))) else ("RIGHTARROW" if not props[name] and (len(o.children)) else "NONE"))

        if not is_child:
            CharacterUIUtils.safe_render(
                row, props, name+"_lock", icon="LOCKED" if props[name+"_lock"] else "UNLOCKED")

        if not o.data:
            if len(o.children) and props[name]:
                settings_box = element.box()
                settings_box.label(text="Items", icon="MOD_CLOTH")
                for child in o.children:
                    child_name = child.name.replace(" ", "_")+"_outfit_toggle"
                    if hasattr(props, child_name):
                        CharacterUIUtils.render_outfit_piece(
                            child, settings_box, props, True)

            return

        if (len(o.children) or "settings" in o.data) and props[name]:
            if len(o.children):
                settings_box = element.box()
                settings_box.label(text="Items", icon="MOD_CLOTH")
                for child in o.children:
                    child_name = child.name.replace(" ", "_")+"_outfit_toggle"
                    if hasattr(props, child_name):
                        CharacterUIUtils.render_outfit_piece(
                            child, settings_box, props, True)

    @staticmethod
    def render_attributes(layout, groups, panel_name):
        for g in groups:
            render = True
            if "visibility" in g:
                expression = g["visibility"]["expression"]
                for var in g["visibility"]["variables"]:
                    expression = expression.replace(
                        str(var["variable"]), str(var["data_path"]))
                render = eval(expression)
            if render:
                box = layout.box()
                header_row = box.row(align=True)
                expanded_op = header_row.operator("character_ui_script.expand_attribute_group_%s" % (
                    character_id.lower()), emboss=False, text="", icon="DOWNARROW_HLT" if g["expanded"] else "RIGHTARROW")
                expanded_op.panel_name = panel_name
                expanded_op.group_name = g["name"]
                try:
                    header_row.label(text=g["name"].replace(
                        "_", " "), icon=g["icon"])
                except:
                    header_row.label(text=g["name"].replace("_", " "))

                if g["expanded"]:
                    for a in g["attributes"]:
                        render_attribute = True
                        if "visibility" in a:
                            if "expression" in a["visibility"]:
                                expression_a = a["visibility"]["expression"]
                                for var in a["visibility"]["variables"]:
                                    expression_a = expression_a.replace(
                                        var["variable"], var["data_path"])
                                try:
                                    render_attribute = eval(expression_a)
                                except:
                                    render_attribute = True
                        if render_attribute:
                            row = box.row(align=True)
                            delimiter = '][' if '][' in a['path'] else '.'
                            offset = 1 if '][' in a['path'] else 0
                            prop = a['path'][a['path'].rindex(delimiter)+1:]
                            path = a['path'][:a['path'].rindex(
                                delimiter)+offset]

                            toggle = a["toggle"] if "invert_checkbox" in a else False
                            invert_checkbox = a["invert_checkbox"] if "invert_checkbox" in a else False
                            slider = a["slider"] if "slider" in a else False
                            icon = a["icon"] if "icon" in a else "NONE"
                            if a['name']:
                                try:
                                    row.prop(eval(
                                        path), prop, text=a['name'], invert_checkbox=invert_checkbox, toggle=toggle, slider=slider, icon=icon)
                                except:
                                    print("couldn't render ", path, " prop")
                            else:
                                try:
                                    row.prop(eval(
                                        path), prop, invert_checkbox=invert_checkbox, toggle=toggle, slider=slider, icon=icon)
                                except:
                                    print("couldn't render %s prop"(path))

    @staticmethod
    def create_unique_ids(panels, operators):
        for p in panels:
            unique_panel = type(
                "%s_%s" % (p.bl_idname, character_id), (p,), {'bl_idname': "%s_%s" % (
                    p.bl_idname, character_id), 'bl_label': p.bl_label, 'bl_parent_id': "%s_%s" % (p.bl_parent_id, character_id) if hasattr(p, "bl_parent_id") else ""}
            )
            register_class(unique_panel)
        for o in operators:
            name = "%s_%s" % (o.bl_idname, character_id.lower())
            unique_operator = type(name, (o,), {"bl_idname": name})
            register_class(unique_operator)

    @staticmethod
    def render_cages(layout, cages, panel=1):
        for c in cages:
            if c[1] == "OP%i" % (panel):
                _addName = ""
                for m in c[0].modifiers:
                    if (m.type == "CLOTH" or m.type == "SOFT_BODY"):
                        box = layout.box()
                        if m.type == "CLOTH" : _addName = "cloth"
                        else: _addName = "soft body"
                        box.label(text=c[0].name + " - " + _addName + " modifier")
                        row = box.row(align=True)
                        row.prop(m, "show_viewport")
                        row.prop(m, "show_render")
                        box.prop(m.point_cache, "frame_start")
                        box.prop(m.point_cache, "frame_end")
                        icon = "TRASH"
                        text = "Delete Bake"
                        if not m.point_cache.is_baked:
                            icon = "PHYSICS"
                            text = "Bake"
                        box.operator("character_ui.bake_%s" % (
                            character_id.lower()), text=text, icon=icon).object_name = c[0].name


class VIEW3D_PT_characterUI(Panel):
    "Main panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = custom_label

    @classmethod
    def poll(self, context):
        if always_show:
            return True

        ch = CharacterUIUtils.get_character()
        if ch:
            return ch == context.object
        return False


class VIEW3D_PT_outfits(VIEW3D_PT_characterUI):
    "Panel for outfits, settings and attributes regarding the outfits of the character"
    bl_label = "Outfits"
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
                    is_top_child = True  # True because if no parent then it's the top child
                    if not o.parent == None and not o.parent == ch:
                        # parent is in different collection so it has to
                        is_top_child = not o.users_collection[0] == o.parent.users_collection[0]
                    if is_top_child:
                        CharacterUIUtils.render_outfit_piece(o, box, props)

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

                for n, pcs in locked_pieces.items():
                    box.label(text=n)
                    for p in pcs:
                        CharacterUIUtils.render_outfit_piece(p, box, props)
            if attributes_key in ch:
                if "outfits" in ch[attributes_key]:
                    attributes_box = layout.box()
                    attributes_box.label(text="Attributes")
                    CharacterUIUtils.render_attributes(
                        attributes_box, ch[attributes_key]["outfits"], "outfits")


class VIEW3D_PT_body(VIEW3D_PT_characterUI):
    "Body panel"
    bl_label = "Body"
    bl_idname = "VIEW3D_PT_body"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            render = False
            if attributes_key in ch:
                if "body" in ch[attributes_key]:
                    render = len(ch[attributes_key]["body"]) > 0
            if ch.data["hair_collection"] and not render:
                if (len(ch.data["hair_collection"].children) + len(ch.data["hair_collection"].objects)) > 1:
                    render = True
            if "character_ui_cages" in ch.data and not render:
                if "cages" in ch.data["character_ui_cages"]:
                    out = list(filter(lambda x: "OP2" in x,
                               ch.data["character_ui_cages"]["cages"]))
                    render = len(out) > 0
            return render and (ch == context.object or always_show)
        return False

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        if ch:
            props = CharacterUIUtils.get_props_from_character()
            if ch.data["hair_collection"]:
                if (len(ch.data["hair_collection"].children) + len(ch.data["hair_collection"].objects)) > 1:
                    hair_row = layout.row(align=True)
                    CharacterUIUtils.safe_render(hair_row, props, "hair_enum")
                    if hasattr(props, "hair_lock") and hasattr(props, "hair_enum"):
                        CharacterUIUtils.safe_render(
                            hair_row, props, "hair_lock", icon="LOCKED" if props.hair_lock else "UNLOCKED", toggle=True)
            if attributes_key in ch:
                if "body" in ch[attributes_key]:
                    if len(ch[attributes_key]["body"]):
                        attributes_box = layout.box()
                        attributes_box.label(text="Attributes")
                        CharacterUIUtils.render_attributes(
                            attributes_box, ch[attributes_key]["body"], "body")


class VIEW3D_PT_physics_body_panel(VIEW3D_PT_characterUI):
    "Physics Sub-Panel"
    bl_label = "Physics"
    bl_idname = "VIEW3D_PT_physics_body_panel"
    bl_parent_id = "VIEW3D_PT_body"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if "character_ui_cages" in ch.data:
                if "cages" in ch.data["character_ui_cages"]:
                    out = list(filter(lambda x: "OP2" in x,
                               ch.data["character_ui_cages"]["cages"]))
                    return len(out) > 0

        return False

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        CharacterUIUtils.render_cages(
            layout, ch.data["character_ui_cages"]["cages"], 2)


class VIEW3D_PT_physics_outfits_panel(VIEW3D_PT_characterUI):
    "Physics Sub-Panel"
    bl_label = "Physics"
    bl_idname = "VIEW3D_PT_physics_outfits_panel"
    bl_parent_id = "VIEW3D_PT_outfits"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if "character_ui_cages" in ch.data:
                if "cages" in ch.data["character_ui_cages"]:
                    out = list(filter(lambda x: "OP1" in x,
                               ch.data["character_ui_cages"]["cages"]))
                    return len(out) > 0
        return False

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        CharacterUIUtils.render_cages(
            layout, ch.data["character_ui_cages"]["cages"], 1)


class VIEW3D_PT_physics_misc_panel(VIEW3D_PT_characterUI):
    "Physics Sub-Panel"
    bl_label = "Physics"
    bl_idname = "VIEW3D_PT_physics_misc_panel"
    bl_parent_id = "VIEW3D_PT_miscellaneous"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if "character_ui_cages" in ch.data:
                if "cages" in ch.data["character_ui_cages"]:
                    out = list(filter(lambda x: "OP3" in x,
                               ch.data["character_ui_cages"]["cages"]))
                    return len(out) > 0
        return False

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        CharacterUIUtils.render_cages(
            layout, ch.data["character_ui_cages"]["cages"], 3)


class VIEW3D_PT_rig_layers(VIEW3D_PT_characterUI):
    "Panel for rig layers, settings and attributes regarding the rig"
    bl_label = "Rig"
    bl_idname = "VIEW3D_PT_rig_layers"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if ch == context.active_object or always_show:
                if attributes_key in ch:
                    if "rig" in ch[attributes_key]:
                        if len(ch[attributes_key]["rig"]):
                            return True

                if rig_layers_key in ch.data:
                    if type(ch.data[rig_layers_key]) == list:
                        return len(ch.data[rig_layers_key])

        return False

    def draw(self, context):
        box = self.layout.column().box()
        ch = CharacterUIUtils.get_character()
        if ch:
            if rig_layers_key in ch.data:
                # sorting "stolen" from CloudRig https://gitlab.com/blender/CloudRig/-/blob/a16df00d5da51d19f720f3e5fe917a84a85883a0/generation/cloudrig.py
                layer_data = ch.data[rig_layers_key]
                if type(layer_data) == list:
                    box.label(text="Layers")
                    rig_layers = [dict(l) for l in layer_data]

                    for i, l in enumerate(rig_layers):
                        # When the Rigify addon is not enabled, finding the original index after sorting is impossible, so just store it.
                        l['index'] = i
                        if 'row' not in l:
                            l['row'] = 1

                    sorted_layers = sorted(rig_layers, key=lambda l: l['row'])
                    sorted_layers = [
                        l for l in sorted_layers if 'name' in l and l['name'] != " "]
                    current_row_index = -1
                    row = box.row()
                    for rig_layer in sorted_layers:
                        if rig_layer['name'] in ["", " "]:
                            continue
                        if rig_layer['name'].startswith("$"):
                            continue

                        if rig_layer['row'] > current_row_index:
                            current_row_index = rig_layer['row']
                            row = box.row()
                        row.prop(
                            ch.data, "layers", index=rig_layer['index'], toggle=True, text=rig_layer['name'])
            if attributes_key in ch:
                if "rig" in ch[attributes_key]:
                    attributes_box = self.layout.box()
                    attributes_box.label(text="Attributes")
                    CharacterUIUtils.render_attributes(
                        attributes_box, ch[attributes_key]["rig"], "rig")


class VIEW3D_PT_miscellaneous(VIEW3D_PT_characterUI):
    "Panel for things which don't belong anywhere"
    bl_label = "Miscellaneous"
    bl_idname = "VIEW3D_PT_miscellaneous"

    @classmethod
    def poll(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if ch == context.active_object or always_show:
                if attributes_key in ch:
                    if "misc" in ch[attributes_key]:
                        if len(ch[attributes_key]["misc"]):
                            return True
                if "character_ui_cages" in ch.data:
                    if "cages" in ch.data["character_ui_cages"]:
                        out = list(filter(lambda x: "OP3" in x,
                                   ch.data["character_ui_cages"]["cages"]))
                        return len(out) > 0

        return False

    def draw(self, context):
        layout = self.layout
        ch = CharacterUIUtils.get_character()
        if attributes_key in ch:
            if "misc" in ch[attributes_key]:
                attributes_box = self.layout.box()
                attributes_box.label(text="Attributes")
                CharacterUIUtils.render_attributes(
                    attributes_box, ch[attributes_key]["misc"], "misc")


class VIEW3D_PT_links(VIEW3D_PT_characterUI):
    "Panel containing links and build info of the UI"
    bl_label = "Info"
    bl_idname = "VIEW3D_PT_links"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        col = layout.column()
        data = CharacterUIUtils.get_character().data
        if links_key in data:
            for section in data[links_key].to_dict():
                box = col.box()
                box.label(text=section)
                column = box.column(align=True)
                for link in data[links_key][section].to_dict():
                    try:
                        column.operator(
                            "wm.url_open", text=link, icon=data[links_key][section][link][0]).url = data[links_key][section][link][1]
                    except:
                        column.operator(
                            "wm.url_open", text=link).url = data[links_key][section][link][1]
        box_model_info = layout.box()
        box_model_info.label(text=custom_label, icon="ARMATURE_DATA")
        if "character_ui_generation_date" in data:
            box_model_info.label(text="UI Generation date: %s" % (
                data["character_ui_generation_date"]), icon="TIME")
        if "character_ui_char_version" in data:
            if len(data["character_ui_char_version"]):
                box_model_info.label(text="Version: %s" % (
                    data["character_ui_char_version"]), icon="BLENDER")

        box_ui_info = layout.box()
        box_ui_info.label(text="UI", icon="MENU_PANEL")
        box_ui_info.label(text='Character-UI v%s%s' % (".".join(str(i)
                                                                for i in bl_info["version"]), '-%s' % (bl_info["branch"]) if "branch" in bl_info else ""), icon='SETTINGS')
        box_ui_info.operator(
            "wm.url_open", text="UI bugs/suggestions").url = "https://github.com/nextr3d/Character-UI/issues/new/choose"
        box_ui_info.operator(
            "wm.url_open", text="Download Character-UI add-on").url = "https://github.com/nextr3d/Character-UI"


class OPS_OT_ExpandAttributeGroup(Operator):
    "Expands or Contracts attribute group"
    bl_idname = "character_ui_script.expand_attribute_group"
    bl_label = "Expand/Contract"
    bl_description = "Expands or Contracts Attribute Group"

    panel_name: StringProperty()
    group_name: StringProperty()

    def execute(self, context):
        ch = CharacterUIUtils.get_character()
        if ch:
            if attributes_key in ch:
                if self.panel_name in ch[attributes_key]:
                    for i in range(len(ch[attributes_key][self.panel_name])):
                        g = ch[attributes_key][self.panel_name][i]
                        if g["name"] == self.group_name:
                            g["expanded"] = not g["expanded"]
                        ch[attributes_key][self.panel_name][i] = g

        return {'FINISHED'}


class OPS_PT_BakePhysics(bpy.types.Operator):
    bl_idname = "character_ui.bake"
    bl_description = "Bake Physics"
    bl_label = "Bake"

    object_name: bpy.props.StringProperty()

    def execute(self, context):
        for m in bpy.data.objects[self.object_name].modifiers:
            if (m.type == "CLOTH" or m.type == "SOFT_BODY") and not m.point_cache.is_baked:
                if not m.show_viewport:
                    self.report(
                        {'WARNING'}, "Modifier is not visible in the viewport, baking will have no effect!")
                else:
                    override = {
                        'scene': context.scene, 'active_object': bpy.data.objects[self.object_name], 'point_cache': m.point_cache}
                    bpy.ops.ptcache.bake(override, bake=True)
                    self.report(
                        {'INFO'}, "Done baking physics for: "+self.object_name)
            elif (m.type == "CLOTH" or m.type == "SOFT_BODY") and m.point_cache.is_baked:
                override = {'scene': context.scene,
                            'active_object': bpy.data.objects[self.object_name], 'point_cache': m.point_cache}
                bpy.ops.ptcache.free_bake(override)
                self.report(
                    {'INFO'}, "Removed physics cache for: "+self.object_name)
        return {'FINISHED'}


classes = [
    CharacterUI
]
panels = [
    VIEW3D_PT_outfits,
    VIEW3D_PT_rig_layers,
    VIEW3D_PT_body,
    VIEW3D_PT_physics_body_panel,
    VIEW3D_PT_physics_outfits_panel,
    VIEW3D_PT_miscellaneous,
    VIEW3D_PT_physics_misc_panel,
    VIEW3D_PT_links
]
operators = [
    OPS_OT_ExpandAttributeGroup,
    OPS_PT_BakePhysics
]


def register():
    for c in classes:
        register_class(c)

    bpy.app.handlers.load_post.append(
        CharacterUIUtils.create_unique_ids(panels, operators))
    setattr(bpy.types.Object, "%s%s" % (custom_prefix, character_id),
            bpy.props.PointerProperty(type=CharacterUI))

    CharacterUI.initialize()


def unregister():
    for c in reversed(classes):
        unregister_class(c)
    delattr(bpy.types.Object, "%s%s" % (custom_prefix, character_id))


if __name__ in ['__main__', 'builtins']:
    # __main__ when executed through the editor
    # builtins when executed after generation of the script
    register()
