import bpy
from bpy.types import (Operator)
from bpy.props import (StringProperty) 
from bpy.utils import (register_class, unregister_class)

class OPS_OT_AddLink(Operator):
    bl_idname = "character_ui.add_link"
    bl_label = "Add new link"
    bl_description = "Adds new link"

    link_section : StringProperty()
    link_text : StringProperty(name="Button Text")
    link_icon : StringProperty(name="Button Icon")
    link_url : StringProperty(name="URL Address")
    
    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
             if key in ch.data:
                if self.link_section in ch.data[key]:
                    s = ch.data[key][self.link_section]
                    if self.link_text != s:
                        s[self.link_text] = (self.link_icon, self.link_url)
                    else:
                        self.report({"WARNING"}, "Duplicate link name")
                        return {"CANCELLED"}
        return {"FINISHED"}                     

    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        self.layout.prop(self, 'link_icon')
        try:
            self.layout.label(text="-   Icon Preview", icon=self.link_icon)
        except:
            self.layout.label(text="This icon does not exist - Icon Preview")
        self.layout.prop(self, 'link_text')
        self.layout.prop(self, 'link_url')

class OPS_OT_RemoveLink(Operator):
    bl_idname = "character_ui.remove_link"
    bl_label = "Remove link"
    bl_description = "Removes link"

    link_section : StringProperty()
    link : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
             if key in ch.data:
                 if self.link_section in ch.data[key]:
                     del ch.data[key][self.link_section][self.link]
                     self.report({"INFO"}, "Removed Link")
        return {"FINISHED"}  


class OPS_OT_EnableLinks(Operator):
    bl_idname = "character_ui.enable_links"
    bl_label = "Enable Links Sections"
    bl_description = "Adds custom property to the rig which allows you to create links sections containing links to your social media, websites, etc."

    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
            if key not in ["", " "]:
                ch.data[key] = {}
                self.report({"INFO"}, "Enabled Links Sections")
                return {"FINISHED"}
        self.report({"ERROR"}, "Could not enable links")
        return {"CANCELLED"}


class OPS_OT_RemoveLinksSection(Operator):
    bl_idname = 'character_ui.remove_links_section'
    bl_label = "Remove section"
    bl_description = "Removes links section"

    link_section : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
             if key in ch.data:
                if self.link_section != "": # remove section
                    new_sections = {}
                    for s in ch.data[key].to_dict():
                        if s != self.link_section:
                            new_sections[s] = ch.data[key][s]
                    ch.data[key] = new_sections
                    self.report({"INFO"}, "Removed links section")
        return {"FINISHED"}

class OPS_OT_AddLinksSection(Operator):
    bl_idname = "character_ui.add_links_section"
    bl_label = "Add Links Section"
    bl_description = "Adds links section"

    link_section_name : StringProperty(name="Name")

    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
             if key in ch.data:
                if self.link_section_name != "" and self.link_section_name not in ch.data[key]:
                    ch.data[key][self.link_section_name] = {}
                    self.report({"INFO"}, "Added links section")
                else:
                    self.report({"WARNING"}, "Section with this name already exists!")
                    return {"CANCELLED"}
                return {"FINISHED"}
        return {"CANCELED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        self.layout.prop(self, 'link_section_name')

class OPS_OT_EditLinksSection(Operator):
    bl_idname = "character_ui.edit_links_section"
    bl_label = "Edit Links Section"
    bl_description = "Edits links section"

    link_section : StringProperty()
    link_section_name : StringProperty(name="New Name")

    def invoke(self, context, event):
        self.link_section_name = self.link_section 
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        self.layout.prop(self, 'link_section_name')

    def execute(self, context):
        ch = context.scene.character_ui_object
        key = context.scene.character_ui_links_key
        if ch and key:
             if key in ch.data:
                if self.link_section_name not in ch.data[key].to_dict():
                    new_sections = {}
                    for s in ch.data[key].to_dict():
                        if s != self.link_section:
                            new_sections[s] = ch.data[key][s]
                        else:
                            new_sections[self.link_section_name] = ch.data[key][s]
                    ch.data[key] = new_sections
                    self.report({"INFO"}, "Updated section")
                else:
                    self.report({"ERROR"}, "Section with this name already exists!")
                    return {"CANCELLED"}
        return {"FINISHED"}

classes = [
    OPS_OT_AddLink,
    OPS_OT_RemoveLink,
    OPS_OT_EnableLinks,
    OPS_OT_RemoveLinksSection,
    OPS_OT_AddLinksSection,
    OPS_OT_EditLinksSection
]
def register():
    for c in classes:
        register_class(c)
  

def unregister():
    for c in reversed(classes):
        unregister_class(c)

