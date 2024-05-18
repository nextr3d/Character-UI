import bpy
from bpy.types import (Operator)
from bpy.props import (StringProperty)
from bpy.utils import (register_class, unregister_class)

tooltip_texts = {
    "character_ui_object": {
        "header": "Character UI Object",
        "body": "Select one object to which the UI gets bind to. Depending on the type of the object you will get different options.\nFor example only Armatures will have access to the Rig Layers Panel",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-setup"]
    },
    "character_ui_masks": {
        "header": "Masks",
        "body": "Add objects to a modifier which will be used to show or hide the modifier. These modifiers are taken from the body object.\nEach modifier can contain multiple objects and gets enabled when at least one of the added objects is visible.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-body"]
    },
    "character_ui_attributes": {
        "header": "Attribute Groups and Attributes",
        "body": "You can add many controls to the UI so the end user doesn't have to look for them. Very useful for controlling materials from one place instead of going to the material you want to edit.\nAll attributes have to be in a group. By right clicking any controls in the UI you can either add them or synchronize them to already existing attribute so they will get the same value as does the primary attribute.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-attributes"]
    },
    "icons": {
        "header": "Icons",
        "body": "Blender has a set of built-in icons which you can use. You can find these icons by enabling the Icon viewer add-on.",
        "doc_url": ["https://docs.blender.org/manual/en/dev/addons/development/icon_viewer.html", "Blender Manual"]
    },
    "character_ui_expression": {
        "header": "Visibility Expressions",
        "body": "You can drive the visibility of the UI element based on some expression. Usefull when you want to show material settings of an outfit piece but only when the outfit piece is visible.\nExpressions behave exactly same as do driver expressions.\nFor example\n 'var1==0 and var2==1' \nwill show the UI element only when data from var1 Data Path equal to 0 and from var2 Data Path equal to 1.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#visibility"]
    },
    "character_ui_physics": {
        "header": "Physics",
        "body": "Lists all of the objects with a cloth modifier from the Physics collection. By clicking the buttons you can set in which panel you want the physics settings to be rendered in.\nNone prevents the settings from rendering.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-physics"]
    },
    "character_ui_version": {
        "header": "Version",
        "body": "Custom property stored on the Character UI Object indicating the version of the character. If left empty it won't render in the UI.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-generate"]
    },
    "character_ui_generation_date": {
        "header": "UI Generation Date",
        "body": "Custom property stored on the Character UI Object indicating when the UI was generated.\n(Can be tweaked by finding the custom property on the Character UI Object if needed. It will get overwritten by next generation)",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-generate"]
    },
    "character_ui_rig_layers": {
        "header": "Rig Layers",
        "body": "You can name Rig Layers to make it more clear what each Rig Layer contains. Like Hair, Torso, Arms,...\nRig Layers are stored the same as CloudRig Rig Layers so if you set the Rig Layers Key to:\nrigify_layers\nit will get them from the CloudRig settings and vice versa.\nEnabling Rig Layer but keeping the name empty will result in a layer with a label 'Layer [index of the layer]'.\nSetting UI Row to the same number will show them one one row in the UI.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-rig-layers"]
    },
    "character_ui_shape_keys": {
        "header": "Shape Keys",
        "body": "Add objects to a shape key which will be used to show or hide the shape key. These shape keys are taken from the body object.\nEach shape key can contain multiple objects and gets enabled when at least one of the added objects is visible.",
        "doc_url": ["https://github.com/nextr3d/Character-UI/wiki/Add-on#character-ui-body"]
    },
    "outfit_piece_parent": {
        "header": "Outfit piece parent",
        "body": "By default parent of each outfit piece should be the Character UI Object so you can grab it and move it and everything follows.\nIf you set the parent to be another object it will be only visible when the parent is visible.\nThis is useful for example when your character has pants and a belt, then it makes no sense to have the belt without pants but pants can be without the belt.",
    },
     "outfits": {
        "header": "Outfits",
        "body": "Each outfit is a collection containing multiple objects. Each object represents one outfit piece and will have a button in the UI.\nThe main outfits collection can't contain any \"unassigned\" objects, if it does, the add-on will notify you and offer one click fix.\nOutfit collections can't (for now) contain other collections.",
    },
     "cant_contain_directly": {
        "header": "Master Collection",
        "body": "To make scenes more organized the add-on requires that all of the outfits are contained in one Master Collection.\nThis means that you have one collection (named Suzanne Outfits for example) and this one is set in the outfits box and this collection contains only other collections and each one is threated as a separate outfit and these collection contain only objects.",
    },
    "chui_id": {
        "header": "Character UI ID",
        "body":"Character UI needs to know which objects in the current scene should be threated as a Character UI character.\nFor this a random ID is used, the random ID is stored in a custom property on the object."
    },
    "chui_links":{
        "header": "Character UI Links",
        "body":"You can add links to the UI, it is going to render a special sections with button which open the default browser on click and navigate to some URL"
    }
}


class OPS_OT_Tooltip(Operator):

    bl_idname = "character_ui.tooltip"
    bl_label = ""
    bl_description = "Click to learn more"
    bl_options = {"INTERNAL"}
    tooltip_id: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=550)

    @classmethod
    def draw_label_with_linebreak(self, layout, text, alert=False, align_split=False):
        """ Attempt to simulate a proper textbox by only displaying as many
            characters in a single label as fits in the UI.
            This only works well on specific UI zoom levels.
            Code taken from: https://gitlab.com/blender/CloudRig
        """

        if text == "":
            return
        col = layout.column(align=True)
        col.alert = alert
        if align_split:
            split = col.split(factor=0.2)
            split.row()
            col = split.row().column()
        paragraphs = text.split("\n")

        max_line_length = 95
        if align_split:
            max_line_length *= 0.95
        for p in paragraphs:

            lines = [""]
            for word in p.split(" "):
                if len(lines[-1]) + len(word)+1 > max_line_length:
                    lines.append("")
                lines[-1] += word + " "

            for line in lines:
                col.label(text=line)
        return col

    def draw(self, context):
        layout = self.layout
        if self.tooltip_id in tooltip_texts:
            tooltip_text = tooltip_texts[self.tooltip_id]
            header_row = layout.row()
            header_row.alert = True
            header_row.label(text=tooltip_text["header"])
            self.draw_label_with_linebreak(layout, tooltip_text["body"])
            if "doc_url" in tooltip_text:
                layout.operator("wm.url_open", text=tooltip_text["doc_url"][1] if len(tooltip_text["doc_url"]) == 2 else "GitHub Wiki").url = tooltip_text["doc_url"][0]
        else:
            layout.label(text="Could not find a documentation", icon="ERROR")

    def execute(self, context):
        return {"FINISHED"}


classes = [
    OPS_OT_Tooltip
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
