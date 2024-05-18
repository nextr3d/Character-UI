from ..constants import CharacterProperties, SceneProperties
from bpy.props import IntProperty
from bpy.types import  Context, Object, Operator
from bpy.utils import register_class, unregister_class



class OPS_OT_RemoveLinks(Operator):

    bl_idname = "character_ui.remove_link"
    bl_label = "Remove one or more links?"
    bl_description = "Remove one or more links from the character"
    bl_options = {"INTERNAL"}
    remove_link: IntProperty(default=-1)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: Context):
        try:
            obj: Object = context.scene[SceneProperties.OBJECT.value]
            
            if self.remove_link < 0:
                del obj[CharacterProperties.CHARACTER_LINKS.value]
            else:
                links = obj[CharacterProperties.CHARACTER_LINKS.value]
                del links[self.remove_link]
                obj[CharacterProperties.CHARACTER_LINKS.value] = links

            count:int = len(obj[CharacterProperties.CHARACTER_LINKS.value]) if self.remove_link < 0 else 1
            texts = ["s", 've'] if count else ["", "s"]
            self.report({'INFO'}, "%i link%s ha%s been deleted"%(count, texts[0], texts[1]))
            return {"FINISHED"}
        except:
            self.report({'ERROR'}, "Could not remove links")
            return {"CANCELLED"}
        
        


classes = [
    OPS_OT_RemoveLinks
]


def register():
    for c in classes:
        register_class(c)


def unregister():
    for c in reversed(classes):
        unregister_class(c)
