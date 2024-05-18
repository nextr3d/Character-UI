from ..constants import CharacterLinkProperties, CharacterProperties, SceneProperties
from bpy.props import IntProperty, StringProperty
from bpy.types import  Context, Object, Operator
from bpy.utils import register_class, unregister_class



class OPS_OT_AddLink(Operator):

    bl_idname = "character_ui.add_link"
    bl_label = ""
    bl_description = "Add new link"
    bl_options = {"INTERNAL"}
    edit_link: IntProperty(default=-1)
    link_href: StringProperty(description="The address opened in the default browser", name="URL")
    link_text: StringProperty(description="The value of the button rendered in the UI", name="Text")
    link_icon: StringProperty(description="A custom icon on the button rendered in the UI", name="Icon")

    def invoke(self, context, event):
        if hasattr(context.scene, SceneProperties.OBJECT.value) and (obj := context.scene[SceneProperties.OBJECT.value]):
            if self.edit_link < 0:
                self.link_href = ""
                self.link_icon = ""
                self.link_text = ""
            return context.window_manager.invoke_props_dialog(self, width=550)
        return False
    

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(self, 'link_text', text='Text')
        layout.prop(self, 'link_href', text='URL')
        layout.prop(self, 'link_icon', text="Icon")
        if not len(self.link_icon): return
        row = layout.row(align=True)
        try:
            row.label(text='Icon preview')
            row.label(text="", icon=self.link_icon)
        except:
            if len(self.link_icon):
                row.alert = True
                row.label(text="Invalid icon")

    def execute(self, context: Context):
        link = {    
                    CharacterLinkProperties.HREF.value: self.link_href,
                    CharacterLinkProperties.TEXT.value: self.link_text,
                    CharacterLinkProperties.ICON.value: self.link_icon if len(self.link_icon) else "NONE",
            }
        obj: Object = context.scene[SceneProperties.OBJECT.value]
        
        if self.edit_link < 0:
            links = list()
            try:
                links = obj[CharacterProperties.CHARACTER_LINKS.value]
            except:
                pass
            try:
                links = links.to_list()
            except:
                pass
            links.append(link)
            obj[CharacterProperties.CHARACTER_LINKS.value] = links

        else:
            try:
                links = obj[CharacterProperties.CHARACTER_LINKS.value]
                links[self.edit_link] = link
                obj[CharacterProperties.CHARACTER_LINKS.value] = links
            except:
                self.report({'ERROR'}, "Edited link can not be found")
                return {'CANCELLED'}
        
        self.report({'INFO'}, "Link has been updated")
        return {"FINISHED"}


classes = [
    OPS_OT_AddLink
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
