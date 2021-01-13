import bpy, time, re
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import EnumProperty, BoolProperty

character_name = "Ellie"
bl_info = {
    "name": "Nextr Rig UI",
    "description": "Script for creating Nextr Rig UI",
    "author": "Nextr3D",
    "version": (4, 0, 0),
    "blender": (2, 91, 0)
}

links = {
    "Link 1 Header": {
        "sub link 1": ("USER", "test.com"),
        "sub link 2": ("FUND", "test.com"),
        "sub link 3": ("URL", "test.com")
    }
}


def get_rig():
    "returns an object with the character name"
    if character_name in bpy.data.objects:
        return bpy.data.objects[character_name]
    return False


class Nextr_Rig(PropertyGroup):

    @classmethod
    def __init__(self):
        print("Rig initialization ", character_name)
        original_selected = bpy.context.view_layer.objects.active
        rig = get_rig()
        bpy.context.view_layer.objects.active = rig
        data = rig.data
        if "nextrrig_properties" not in data:
            data["nextrrig_properties"] = {}
        if "prev_nextrrig_properties" not in data:
            data["prev_nextrrig_properties"] = {}
        if "update" not in data:
            data["update"] = 1
        self.ui_build()
        bpy.context.view_layer.objects.active = original_selected

    @classmethod
    def ui_build(self):
        self.ui_build_outfits()

    @classmethod
    def ui_build_outfits(self):
        outfits_collection_name = character_name+" Outfits"
        if outfits_collection_name in bpy.data.collections:
            outfits = bpy.data.collections[outfits_collection_name].children.keys(
            )
            options = self.create_enum_options(outfits, "Show outfit: ")
            default = self.get_property("outfit_enum")
            if default == None:
                default = len(options) - 1

            self.ui_setup_enum("outfit_enum", self.update_outfits,
                               "Outfits", "Changes outfits", options, default)
            self.ui_build_outfit_buttons(outfits)

    @classmethod
    def ui_build_outfit_buttons(self, collections):
        data = get_rig().data["nextrrig_properties"]
        for collection in collections:
            objects = bpy.data.collections[collection].objects
            for o in objects:
                default = False
                default_lock = False
                name = o.name_full.replace(" ", "_")+"_outfit_toggle"
                if name in data and name+"_lock" in data:
                    default = data[name]
                    default_lock = data[name+"_lock"]
                self.ui_setup_toggle(
                    name, self.update_outfit_pieces, o.name_full, "Toggles outfit piece on and off", default)
                self.ui_setup_toggle(
                    name+"_lock", None, "", "Locks the outfit piece to be visible even when changing outfits", default_lock)

    @classmethod
    def get_property(self, property_name):
        data = get_rig().data.nextrrig_properties

        if property_name in data:
            return data[property_name]
        return None

    @staticmethod
    def create_enum_options(array, description_prefix="Empty description for:"):
        "method for creating options for blender UI enums"
        items = []
        for array_item in array:
            items.append(("OP"+str(array.index(array_item)),
                          array_item, description_prefix+" "+array_item))
        return items

    @classmethod
    def ui_setup_enum(self, property_name, update_function, name="Name", description="Empty description", items=[], default=0):
        "method for easier creation of enums (selects)"
        rig_data = get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):
            rig_data['nextrrig_properties'][property_name] = default
            prop = EnumProperty(
                name=name,
                description=description,
                items=items,
                update=update_function,
                default='OP'+str(default)
            )

            setattr(self, property_name, prop)

    @classmethod
    def ui_setup_toggle(self, property_name, update_function, name='Name', description='Empty description', default=False):
        "method for easier creation of toggles (buttons)"
        rig_data = get_rig().data
        if hasattr(rig_data, 'nextrrig_properties'):
            rig_data.nextrrig_properties[property_name] = default
            prop = BoolProperty(
                name=name,
                description=description,
                update=update_function,
                default=default
            )
            setattr(self, property_name, prop)
    @staticmethod
    def update_outfit_pieces_visibility(ignore_props_check = 1):
        data = get_rig().data
        props = data["nextrrig_properties"]
        prev_props = data["prev_nextrrig_properties"]
        for i, c in enumerate(bpy.data.collections[character_name+" Outfits"].children):
            for o in c.objects:
                name = o.name.replace(" ","_")+"_outfit_toggle"
                if props[name] != prev_props[name] or ignore_props_check:
                    if ignore_props_check:
                        if not props[name+"_lock"]:
                            if i == props["outfit_enum"]:
                                o.hide_render = o.hide_viewport = not props[name]
                                Nextr_Rig.update_body_masks_by_object_name(o.name, props[name])
                                Nextr_Rig.update_body_shapekeys_by_object(o.name,props[name])
                            else:
                                o.hide_render = o.hide_viewport = not (i == props["outfit_enum"])
                                Nextr_Rig.update_body_masks_by_object_name(name, (i == props["outfit_enum"]))
                                Nextr_Rig.update_body_shapekeys_by_object(o.name,(i == props["outfit_enum"]))
                    else:
                        o.hide_render = o.hide_viewport = not props[name]
                        Nextr_Rig.update_body_masks_by_object_name(o.name, props[name])
                        Nextr_Rig.update_body_shapekeys_by_object(o.name,props[name])
        data["prev_nextrrig_properties"] = data["nextrrig_properties"]

    @staticmethod
    def update_body_masks_by_object_name(name, show):
        if character_name+" Body" in bpy.data.objects:
            body = bpy.data.objects[character_name+" Body"]
            for m in body.modifiers:
                if re.search(name+"\s?(m|M)ask", m.name):
                    m.show_viewport = m.show_render = show
    @staticmethod
    def update_body_shapekeys_by_object(name, show):
        if character_name+" Body" in bpy.data.objects:
            body = bpy.data.objects[character_name+" Body"]
            for s in body.data.shape_keys.key_blocks:
                if re.search(name+"\s?(s|S)hape", s.name):
                    s.value = show
                    
    def update_outfits(self, context):
        Nextr_Rig.update_outfit_pieces_visibility()
        
    def update_outfit_pieces(self, context):
        Nextr_Rig.update_outfit_pieces_visibility(0)

    def pre_depsgraph_update(self, context):
        start = time.time()
        data = get_rig().data
        update = False
        for key in data["nextrrig_properties"]:
            if (key not in data["prev_nextrrig_properties"] or key not in data["nextrrig_properties"]) or data["nextrrig_properties"][key] != data["prev_nextrrig_properties"][key]:
                update = True
                continue

        if update:
            data['update'] = 1
        # print("update took: ", time.time() - start)

    def post_depsgraph_update(self, context):
        data = get_rig().data
        if data['update']:
            data['update'] = 0
            data["prev_nextrrig_properties"] = data["nextrrig_properties"]


class VIEW3D_PT_nextr_rig(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = character_name

    @classmethod
    def poll(self, context):
        "show the panel if context.object is same as the character_name"
        if context.object and context.object.name == character_name:
            return True


class VIEW3D_PT_outfits(VIEW3D_PT_nextr_rig):
    bl_label = "Outfits"
    """no idea if this is the correct way but classes with identical ids get destroyed 
    so this way multiple classes with same(or atleast similar) functionality can exist at the same time"""
    bl_idname = "VIEW3D_PT_outfits_"+character_name

    def draw(self, context):
        layout = self.layout
        props = context.object.data.nextrrig_properties

        box = layout.box()
        box.label(text="Outfit", icon="MATCLOTH")
        if len(bpy.data.collections[character_name+" Outfits"].children) == 1:
            box.operator(
                "nextr.empty", text=bpy.data.collections[character_name+" Outfits"].children[0].name, emboss=False, depress=True)
        else:
            box.prop(props, "outfit_enum")
        
        for o in bpy.data.collections[character_name+" Outfits"].children[props["outfit_enum"]].objects:
            row = box.row(align=True)
            name = o.name.replace(" ", "_")+"_outfit_toggle"
            row.prop(props, name, toggle=True)
            row.prop(props, name+"_lock",icon="LOCKED" if props[name+"_lock"] else "UNLOCKED")

        locked_pieces = {}
        
        for i, c in enumerate(bpy.data.collections[character_name+" Outfits"].children):
            pieces = []
            for o in c.objects:
                if i != props["outfit_enum"]:
                    name = o.name.replace(" ", "_")+"_outfit_toggle"
                    if props[name+"_lock"]:
                        pieces.append(name)
            if len(pieces):
                locked_pieces[c.name] = pieces
        for n,pcs in locked_pieces.items():
            box.operator('nextr.empty', text=n,  emboss=False, depress=True)
            for p in  pcs:
                row = box.row(align=True)
                row.prop(props, p, toggle=True)
                row.prop(props, p+"_lock",icon="LOCKED" if props[p+"_lock"] else "UNLOCKED")
class VIEW3D_PT_links(VIEW3D_PT_nextr_rig):
    bl_label = "Links"
    bl_idname = "VIEW3D_PT_links_"+character_name

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.operator('nextr.empty', text='Nextr Rig UI v'+str(bl_info['version'][0])+'.'+str(
            bl_info['version'][1])+'.'+str(bl_info['version'][2]), icon='SETTINGS', emboss=False, depress=True)
        col = layout.column()
        for user in links:
            box = col.box()
            box.operator('nextr.empty', text=user,  emboss=False, depress=True)
            column = box.column(align=True)
            for link in links[user]:
                column.operator(
                    "wm.url_open", text=link, icon=links[user][link][0]).url = links[user][link][1]


class OPS_OT_Empty(Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'


classes = (
    VIEW3D_PT_outfits,
    VIEW3D_PT_links,
    OPS_OT_Empty,
    Nextr_Rig
)


def register():
    for c in classes:
        register_class(c)
    bpy.types.Armature.nextrrig_properties = bpy.props.PointerProperty(
        type=Nextr_Rig)
    bpy.types.Armature.prev_nextrrig_properties = bpy.props.PointerProperty(
        type=Nextr_Rig)
    Nextr_Rig.__init__()


def unregister():
    for c in classes:
        unregister_class(c)


if __name__ == "__main__":
    register()


bpy.app.handlers.depsgraph_update_post.append(Nextr_Rig.post_depsgraph_update)
bpy.app.handlers.depsgraph_update_pre.append(Nextr_Rig.pre_depsgraph_update)
