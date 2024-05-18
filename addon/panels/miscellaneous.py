from ..operators.tooltip import OPS_OT_Tooltip
from ..operators.add_link import OPS_OT_AddLink
from ..operators.remove_links import OPS_OT_RemoveLinks
from ..constants import CharacterLinkProperties, CharacterProperties, SceneProperties
from bpy.types import (Context, Object, Panel)
from bpy.utils import (register_class, unregister_class)


class VIEW3D_PT_character_ui_miscellaneous(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Miscellaneous"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context):
        return hasattr(context.scene, SceneProperties.OBJECT.value) and context.scene[SceneProperties.OBJECT.value]

    def draw(self, context):
        layout = self.layout
        o: Object = context.scene[SceneProperties.OBJECT.value]
        
        box = layout.box()
        box.label(text="Links", icon="LINK_BLEND")
        links_box = box.box()
        links_count = 0
        if CharacterProperties.CHARACTER_LINKS.value in o and (links := o[CharacterProperties.CHARACTER_LINKS.value]):
            links_count = len(links)
            for i in range(links_count):
                link = links[i]
                row = links_box.row(align=True)
                url = icon = label = ""
                try:
                    label: str = link[CharacterLinkProperties.TEXT.value] if CharacterLinkProperties.TEXT.value in link else ""
                    icon: str = link[CharacterLinkProperties.ICON.value] if  CharacterLinkProperties.ICON.value in link else "NONE"
                    url = link[CharacterLinkProperties.HREF.value] if  CharacterLinkProperties.HREF.value in link else ""
                    row.operator("wm.url_open", text=label, icon=icon).url = url
                except:
                    row.alert = True
                    row.label(text="Invalid link data!")
                edit = row.operator(OPS_OT_AddLink.bl_idname, text="", icon="PREFERENCES")
                edit.edit_link = i
                edit.link_href = url
                edit.link_text = label
                edit.link_icon = icon
                del_op = row.operator(OPS_OT_RemoveLinks.bl_idname, text="", icon="TRASH")
                del_op.remove_link = -i
        
        if not links_count:
            links_box.label(text="No links setup")

        
        row = box.row(align=True)
        
        row.operator(OPS_OT_AddLink.bl_idname, text="Add new link", icon="PLUS").edit_link = -1
        row.operator(OPS_OT_Tooltip.bl_idname, text="", icon="QUESTION").tooltip_id = "chui_links"
        if links_count:
            box.operator(OPS_OT_RemoveLinks.bl_idname,text="Remove all links", icon="TRASH").remove_link = -1
        return


classes = [
    VIEW3D_PT_character_ui_miscellaneous,
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
