import bpy
from bpy.types import (Panel, PropertyGroup, Operator)
from bpy.props import (PointerProperty, StringProperty, BoolProperty, IntProperty)
from bpy.utils import (register_class, unregister_class)



class VIEW3D_PT_character_ui_miscellaneous(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Miscellaneous"

    def draw(self, context):
        layout = self.layout

class VIEW3D_PT_character_ui_links_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Links"
    bl_idname = "VIEW3D_PT_character_ui_links_panel"
    bl_parent_id = "VIEW3D_PT_character_ui_miscellaneous"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "character_ui_links_key")
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch:
            if key and key in ch.data:
                box = layout.box()
                box.label(text="Links", icon="URL")
                if len(ch.data[key]):
                    for s in ch.data[key].to_dict():
                        section_box = box.box()
                        row = section_box.row(align=True)
                        row.label(text=s)
                        row.operator("character_ui.edit_links_section", text="", icon="PREFERENCES").link_section = s
                        row.operator("character_ui.remove_links_section", text="", icon="TRASH").link_section = s
                        for l in ch.data[key][s].to_dict():
                            link_row = section_box.row(align=True)
                            try:
                                link_row.label(text=l, icon=ch.data[key][s][l][0])
                            except:
                                link_row.label(text=l)
                            url = ch.data[key][s][l][1]
                            link_row.operator("wm.url_open", text=url).url = url
                            remove_link = link_row.operator("character_ui.remove_link", text="", icon="TRASH")
                            remove_link.link_section = s
                            remove_link.link = l
                        section_box.operator("character_ui.add_link", text="Add link", icon="PLUS").link_section = s
                box.operator("character_ui.add_links_section", text="Add Links Section")
            else:
                layout.operator("character_ui.enable_links", icon="PLUS")

classes = [
    VIEW3D_PT_character_ui_miscellaneous,
    VIEW3D_PT_character_ui_links_panel
]
def register():
    bpy.types.Scene.character_ui_links_key = StringProperty(name="Links Key",
                                                            description="Under which custom property the links are stored")
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

