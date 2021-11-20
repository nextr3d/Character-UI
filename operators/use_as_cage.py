import bpy
from bpy.types import (Operator)
from bpy.props import (PointerProperty, StringProperty, EnumProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_UseAsCage(Operator):
    bl_idname = "character_ui.use_as_cage"
    bl_label = "Select object to be used as physics cage"
    bl_description = "Options for object which could be used as mesh deform cage"

    cage: StringProperty()
    panel: EnumProperty(name="Panel", items=[("OP1", "Outfits", "Toggles in the Outfits Panel"), ("OP2", "Body", "Toggles in the Body Panel"), (
        "OP3", "Miscellaneous", "Toggles in the MIscellanesou Panel"), ("OP4", "None", "Not visible in the UI")])

    def invoke(self, context, event):
        ch = context.scene.character_ui_object
        if "character_ui_cages" in ch.data:
            if "cages" in ch.data["character_ui_cages"]:
                for c in ch.data["character_ui_cages"]["cages"]:
                    if c[0].name == self.cage:
                        self.panel = c[1]
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        self.layout.label(text=self.cage)
        self.layout.prop(self, "panel")

    def execute(self, context):
        ch = context.scene.character_ui_object
        if ch:
            if "cages" in ch.data["character_ui_cages"]:
                new_cages = []
                add_new = True
                for c in ch.data["character_ui_cages"]["cages"]:
                    if c[0].name == self.cage and self.panel != "OP4":
                        new_cages.append(
                            (bpy.data.objects[self.cage], self.panel))
                        add_new = False
                    elif c[0].name != self.cage:
                        new_cages.append(c)
                if add_new and self.panel != "OP4":
                    new_cages.append((bpy.data.objects[self.cage], self.panel))
                ch.data["character_ui_cages"]["cages"] = new_cages
            else:
                ch.data["character_ui_cages"]["cages"] = [
                    (bpy.data.objects[self.cage], self.panel)]
        return {"FINISHED"}


classes = [
    OPS_OT_UseAsCage
]


def register():

    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
