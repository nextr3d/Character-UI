import os
import bpy
from bpy.types import (Operator)
from bpy.props import (StringProperty) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_GenerateScript(Operator):
    bl_idname = 'characterui_generate.generate_script'
    bl_label = 'Generate UI'
    bl_description = 'Generates the UI script'
    
    character_id : StringProperty()
    character_id_key : StringProperty()


    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self,event)

    def execute(self, context):
        if self.character_id:
            load_ui_script(self.character_id, self.character_id_key)
        else:
            self.report({"ERROR"}, "You need to generate rig id!")
            return {"FAILED"}
        return {'FINISHED'}

def load_ui_script(character_id, character_id_key):
   
    file_name = "%s.py"%(character_id)
    text = bpy.data.texts.get(file_name)
    #check if file already exists
    if not text:
        text = bpy.data.texts.new(name=file_name)
        text.use_fake_user = False

    text.clear() #clear text
    text.use_module = True #enable Register

    file_path = os.path.dirname(os.path.realpath(__file__))

    readfile = open(os.path.join(file_path, "../character_ui.py"), 'r')
    for line in readfile:
        text.write(line)
        if line == "#script variables\n":
            text.write("character_id_key=\"%s\"\n"%(character_id_key))
            text.write("character_id=\"%s\"\n"%(character_id))

    readfile.close()

    # Run UI script
    exec(text.as_string(), {})
    return text

def register():
    register_class(OPS_OT_GenerateScript)

def unregister():
    unregister_class(OPS_OT_GenerateScript)