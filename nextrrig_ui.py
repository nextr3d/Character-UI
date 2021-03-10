import bpy, time, re
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty

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

def change_visibility(collection_name, object_name, props):
    "determines if the clothing piece should  have it's visibility changed"
    return collection_name == bpy.data.collections[character_name+" Outfits"].children[props['outfit_enum']].name or props[object_name+"_lock"]

def render_props(props, name, element):
    "renders a prop if it exists"
    if hasattr(props, name):
        element.prop(props, name)
    

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
        "executes all of the methods building the UI"
        self.ui_build_outfits()
        self.ui_build_physics()

    @classmethod
    def ui_build_outfits(self):
        outfits_collection_name = character_name+" Outfits"
        if outfits_collection_name in bpy.data.collections:
            outfits = bpy.data.collections[outfits_collection_name].children.keys()
            options = self.create_enum_options(outfits, "Show outfit: ")
            default = self.get_property("outfit_enum")
            if default == None:
                default = len(options) - 1
            self.ui_setup_enum("outfit_enum", self.update_outfits,"Outfits", "Changes outfits", options, default)
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
                self.ui_setup_toggle(name, self.update_outfit_pieces, o.name_full, "Toggles outfit piece on and off", default)
                self.ui_setup_toggle(name+"_lock", self.update_outfit_pieces, "", "Locks the outfit piece to be visible even when changing outfits", default_lock)

    @classmethod
    def ui_build_physics(self):
        rig = get_rig()
        nextrrig_properties = rig.data.nextrrig_properties
        print(character_name+" Body Physics")
        if character_name+" Body Physics" in bpy.data.collections:
            print("oj")
            for o in bpy.data.collections[character_name+" Body Physics"].objects:
                #create slider for quality
                default_quality = 5
                if o.name.replace(" ","_")+"_quality" in nextrrig_properties:
                    default_quality = nextrrig_properties[o.name.replace(" ","_")+"_quality"]
                self.ui_setup_int(o.name.replace(" ","_")+"_quality", self.update_physics, "Quality", "Sets the quality of the simulation for "+o.name, default_quality, 0, 200)
                #create slider for frame start
                default_frame_start = bpy.data.scenes[bpy.context.scene.name].frame_start
                if o.name.replace(" ","_")+"_frame_start" in nextrrig_properties:
                    default_frame_start = nextrrig_properties[o.name.replace(" ","_")+"_frame_start"]
                self.ui_setup_int(o.name.replace(" ","_")+"_frame_start", self.update_physics, "Frame Start", "Sets the Starting Frame of the simulation for "+o.name, default_frame_start,0,1048573)
                #create slider for frame end
                default_frame_end = bpy.data.scenes[bpy.context.scene.name].frame_end
                if o.name.replace(" ","_")+"_frame_end" in nextrrig_properties:
                    default_frame_end = nextrrig_properties[o.name.replace(" ","_")+"_frame_end"]
                self.ui_setup_int(o.name.replace(" ","_")+"_frame_end", self.update_physics, "Frame End", "Sets the Ending Frame of the simulation for "+o.name, default_frame_end,0,1048574)
    
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
            items.append(("OP"+str(array.index(array_item)),array_item, description_prefix+" "+array_item))
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

    @classmethod
    def ui_setup_int(self, property_name,update_function,name = 'Name', description = 'Empty description', default = 0, min = 0, max = 1):           
        "method for easier creation of ints (sliders)"
        rig_data = get_rig().data
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

    @staticmethod
    def update_outfit_pieces_visibility():
        #updates visibility of an outfit object, updates masks and applies shapekeys
        data = get_rig().data
        props = data["nextrrig_properties"]
        prev_props = data["prev_nextrrig_properties"]
        
        for c in bpy.data.collections[character_name+" Outfits"].children:
            for o in c.objects:
                t_name = o.name.replace(" ","_")+"_outfit_toggle"
                if change_visibility(c.name, t_name, props):
                    if o.parent == None: #object is the first child of it's collection
                        o.hide_render = o.hide_viewport = not props[t_name]
                        Nextr_Rig.update_body_masks_by_object_name(o.name, props[t_name])
                        Nextr_Rig.update_body_shapekeys_by_object(o.name, props[t_name])
                        for child in o.children:
                            show_mask_shapekey = False
                            if not props[t_name]: #hide all children
                                child.hide_render = child.hide_viewport = True
                            else:
                                show_mask_shapekey = props[child.name.replace(" ", "_")+"_outfit_toggle"]
                                child.hide_render = child.hide_viewport = not show_mask_shapekey
                            Nextr_Rig.update_body_masks_by_object_name(child.name, show_mask_shapekey)
                            Nextr_Rig.update_body_shapekeys_by_object(child.name, show_mask_shapekey)
                elif o.parent == None: #hide the object if it's parent
                    o.hide_render = o.hide_viewport = True
                    Nextr_Rig.update_body_masks_by_object_name(o.name, False)
                    Nextr_Rig.update_body_shapekeys_by_object(o.name, False)
                    for child in o.children:#hide all children
                        child.hide_render = child.hide_viewport = True
                        Nextr_Rig.update_body_masks_by_object_name(child.name, False)
                        Nextr_Rig.update_body_shapekeys_by_object(child.name, False)

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
        Nextr_Rig.update_outfit_pieces_visibility()

    def update_physics(self, context):
        "updates all of the values in the physics modifier on a cage"
        nextr_props = context.object.data.nextrrig_properties
        if context.object.name+" Body Physics" in bpy.data.collections:
            for o in bpy.data.collections[context.object.name+" Body Physics"].objects:
                for m in o.modifiers:
                    if m.type == "CLOTH":
                        m.settings.quality = nextr_props[o.name.replace(" ","_")+"_quality"]
                        m.point_cache.frame_start = nextr_props[o.name.replace(" ","_")+"_frame_start"]
                        m.point_cache.frame_end = nextr_props[o.name.replace(" ","_")+"_frame_end"]
    
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
            
class Nextr_Rig_Rig_Layers(PropertyGroup):
    rig_layers: [[{'key':0, 'name':'Face'}]]

class Nextr_Rig_Object_Setting(PropertyGroup):
    modifiers: [] #array of all of the modifiers visible in the viewport
    shape_keys: [] #array of all of the shapekeys visible in the UI
    children:[] #array of the child objects

class VIEW3D_PT_nextrRig(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = character_name

    @classmethod
    def poll(self, context):
        "show the panel if context.object is same as the character_name"
        if context.object and context.object.name == character_name:
            return True


class VIEW3D_PT_outfits(VIEW3D_PT_nextrRig):
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
            if (o.parent == None):
                row = box.row(align=True)
                name = o.name.replace(" ", "_")+"_outfit_toggle"
                row.prop(props, name, toggle=True, icon="TRIA_DOWN" if ("settings" in o.data and props[name]) else ("TRIA_RIGHT" if "settings" in o.data else "NONE"))
                row.prop(props, name+"_lock",icon="LOCKED" if props[name+"_lock"] else "UNLOCKED")
                if "settings" in o.data and props[name]:
                    settings_box = box.box()
                    s = o.data["settings"]
                    if "modifiers" in s:
                        settings_box.operator('nextr.empty', text="Modifiers",  emboss=False, depress=True, icon="MODIFIER")
                        for m_name in s['modifiers']:
                            if m_name in o.modifiers:
                                modifier_row = settings_box.row(align=True)
                                modifier_row.label(text=m_name, icon='MOD_'+o.modifiers[m_name].type)
                                op = modifier_row.operator('nextr.hide_modifier', text='', icon='RESTRICT_VIEW_OFF' if o.modifiers[m_name].show_viewport else 'RESTRICT_VIEW_ON', depress=o.modifiers[m_name].show_viewport)
                                op.object_name = o.name
                                op.modifier_name = m_name
                                op.hide_mode = "VIEWPORT"

                                op_r = modifier_row.operator('nextr.hide_modifier', text='', icon='RESTRICT_RENDER_OFF' if o.modifiers[m_name].show_render else 'RESTRICT_RENDER_ON', depress=o.modifiers[m_name].show_render)
                                op_r.object_name = o.name
                                op_r.modifier_name = m_name
                                op_r.hide_mode = "RENDER"
                    if 'children' in s:
                        settings_box.operator('nextr.empty', text="Items",  emboss=False, depress=True, icon="MOD_CLOTH")
                        for o_name in s['children']:
                            o_row = settings_box.row(align=True)
                            o_row.prop(props, o_name.replace(" ", "_")+"_outfit_toggle", toggle=True)
                    if len(o.children):
                        settings_box.operator('nextr.empty', text="Items",  emboss=False, depress=True, icon="MOD_CLOTH")
                        for child in o.children:
                            o_row = settings_box.row(align=True)
                            child_name = child.name.replace(" ", "_")+"_outfit_toggle"
                            if hasattr(props, child_name):
                                o_row.prop(props, child_name, toggle=True)

        locked_pieces = {}
        
        for i, c in enumerate(bpy.data.collections[character_name+" Outfits"].children):
            pieces = []
            for o in c.objects:
                if i != props["outfit_enum"]:
                    name = o.name.replace(" ", "_")+"_outfit_toggle"
                    if props[name+"_lock"]:
                        pieces.append([name, o.name])
            if len(pieces):
                locked_pieces[c.name] = pieces
        for n,pcs in locked_pieces.items():
            box.operator('nextr.empty', text=n,  emboss=False, depress=True)
            for p in  pcs:
                row = box.row(align=True)
                row.prop(props, p[0], toggle=True)
                row.prop(props, p[0]+"_lock",icon="LOCKED" if props[p[0]+"_lock"] else "UNLOCKED")

class VIEW3D_PT_links(VIEW3D_PT_nextrRig):
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

class VIEW3D_PT_body(VIEW3D_PT_nextrRig):
    "Body panel"
    bl_label = "Body"
    bl_idname = "VIEW3D_PT_body"+character_name

    def draw(self, context):
        pass
class VIEW3D_PT_physics_panel(VIEW3D_PT_nextrRig):
    "Physics Sub-Panel"
    bl_label = "Physics (Experimental)"
    bl_idname = "VIEW3D_PT_physics_panel"+character_name
    bl_parent_id = "VIEW3D_PT_body"+character_name

    def draw(self, context):
        layout = self.layout
        nextr_props = context.object.data.nextrrig_properties
        if context.object.name+" Body Physics" in bpy.data.collections:
            for o in bpy.data.collections[character_name+" Body Physics"].objects:
                box = layout.box()
                baked = False
                info = ""
                visible = False
                m_name = ""
                for m in o.modifiers:
                    if m.type == "CLOTH":
                        baked = m.point_cache.is_baked
                        info = m.point_cache.info
                        visible = m.show_render
                        
                box.label(text=o.name.replace("Cage","").replace(".L", "Left").replace(".R","Right"), icon="PREFERENCES")
                column = box.column(align=True)
                column.active = not baked
                column.enabled = not baked
                render_props(nextr_props, o.name.replace(" ","_")+"_quality", column)
                render_props(nextr_props, o.name.replace(" ","_")+"_frame_start", column)
                render_props(nextr_props, o.name.replace(" ","_")+"_frame_end", column)
                box.operator('nextr.bake', text="Delete Bake" if baked else "Bake").object_name = o.name
                op = box.operator('nextr.hide_modifier', text="Modifier enabled" if visible else "Modifier disabled", icon="HIDE_OFF" if visible else "HIDE_ON", depress=True if visible else False )
                op.object_name = o.name
                op.modifier_name = 'Cloth'
                op.hide_mode = "BOTH"

                box.operator('nextr.empty', text=info, icon="INFO", depress=True, emboss=False)


class VIEW3D_PT_rig_layers(VIEW3D_PT_nextrRig):
    bl_label = "Rig Layers"
    bl_idname = "VIEW3D_PT_rig_layers_"+character_name

    def draw(self, context):
        box = self.layout.column().box()
        layers = context.object.data.layers
        if 'rig_layers' in context.object.data and 'rig_layers' in context.object.data['rig_layers']:
            for group in context.object.data['rig_layers']['rig_layers']:
                row = box.row(align=True)
                for toggle in group:
                    row.operator('nextr.toggle_rig_layer', text=toggle['name'], depress=layers[toggle['index']]).rig_layer_index = toggle['index']
        else:
            for i in range(31):
                row = box.row(align=True)
                row.operator('nextr.toggle_rig_layer', text=str(i+1)+' Layer', depress=layers[i]).rig_layer_index = i
        

class OPS_OT_Empty(Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'

class OPS_OT_ToggleRigLayer(Operator):
    bl_idname = 'nextr.toggle_rig_layer'
    bl_description = 'Toggles rig layer'
    bl_label = "Toggle rig layer"

    layer_name : StringProperty()
    rig_layer_index : IntProperty()

    def execute(self, context):
        layers = get_rig().data.layers
        layers[self.rig_layer_index] = not layers[self.rig_layer_index]
        return{'FINISHED'}


class OPS_OT_HideModifier(Operator):
    bl_idname = "nextr.hide_modifier"
    bl_description = "Hides modifer"
    bl_label = "Hide modifier"

    object_name : StringProperty()
    modifier_name : StringProperty()
    hide_mode : StringProperty()

    def execute(self, context):
        if self.object_name in bpy.data.objects:
            o = bpy.data.objects[self.object_name]
            if self.modifier_name in o.modifiers:
                if self.hide_mode == "RENDER":
                    o.modifiers[self.modifier_name].show_render = not o.modifiers[self.modifier_name].show_render 
                    self.report({'INFO'}, 'Toggled modifier '+self.modifier_name+' in render mode')
                elif self.hide_mode == "VIEWPORT":
                    o.modifiers[self.modifier_name].show_viewport = not o.modifiers[self.modifier_name].show_viewport 
                    self.report({'INFO'}, 'Toggled modifier '+self.modifier_name+' in viewport mode')
                else:
                    o.modifiers[self.modifier_name].show_viewport = o.modifiers[self.modifier_name].show_render = not o.modifiers[self.modifier_name].show_render  
                    self.report({'INFO'}, 'Toggled modifier '+self.modifier_name+' in both modes')
        return {'FINISHED'}

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

classes = (
    VIEW3D_PT_outfits,
    VIEW3D_PT_rig_layers,
    VIEW3D_PT_body,
    VIEW3D_PT_physics_panel,
    VIEW3D_PT_links,
    OPS_OT_Empty,
    OPS_OT_HideModifier,
    OPS_OT_ToggleRigLayer,
    OPS_PT_BakePhysics,
    Nextr_Rig,
    Nextr_Rig_Object_Setting,
    Nextr_Rig_Rig_Layers
)


def register():
    for c in classes:
        register_class(c)
    bpy.types.Armature.nextrrig_properties = bpy.props.PointerProperty(
        type=Nextr_Rig)
    bpy.types.Armature.prev_nextrrig_properties = bpy.props.PointerProperty(
        type=Nextr_Rig)
    bpy.types.Mesh.settings = bpy.props.PointerProperty(type=Nextr_Rig_Object_Setting)
    bpy.types.Armature.rig_layers = bpy.props.PointerProperty(type=Nextr_Rig_Rig_Layers)
    Nextr_Rig.__init__()


def unregister():
    for c in classes:
        unregister_class(c)


if __name__ == "__main__":
    register()


bpy.app.handlers.depsgraph_update_post.append(Nextr_Rig.post_depsgraph_update)
bpy.app.handlers.depsgraph_update_pre.append(Nextr_Rig.pre_depsgraph_update)
