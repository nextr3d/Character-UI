import os
import bpy
from datetime import datetime
from bpy.types import (Operator)
from bpy.props import (StringProperty, BoolProperty)
from bpy.utils import (register_class, unregister_class)


class OPS_OT_GenerateScript(Operator):
    "Generates script, executes it and adds it to the character's custom props"
    bl_idname = 'characterui_generate.generate_script'
    bl_label = 'Generate UI'
    bl_description = 'Generates the UI script'

    character_id: StringProperty()
    character_id_key: StringProperty()
    rig_layers_key: StringProperty()
    always_show: BoolProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if self.character_id:
            text = load_ui_script(context, self.character_id,
                                  self.character_id_key, self.rig_layers_key, self.always_show)
            for o in bpy.data.objects:
                if str(type(o.data)) != "<class 'NoneType'>":
                    if self.character_id_key in o.data:
                        if o.data[self.character_id_key] == self.character_id:
                            o.data["character_ui_generation_date"] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
                            if "character_ui_char_version" not in o.data:
                                o.data["character_ui_char_version"] = ""
                            o.data["character_ui_textfile"] = text
            self.report({"INFO"}, "Generated script")
        else:
            self.report({"ERROR"}, "You need to generate rig id!")
            return {"FAILED"}
        return {'FINISHED'}


def load_ui_script(context, character_id, character_id_key, rig_layers_key, always_show):

    file_name = "%s.py" % (character_id)
    text = bpy.data.texts.get(file_name)
    # check if file already exists
    if not text:
        text = bpy.data.texts.new(name=file_name)
        text.use_fake_user = False

    text.clear()  # clear text
    text.use_module = True  # enable Register

    file_path = os.path.dirname(os.path.realpath(__file__))

    readfile = open(os.path.join(file_path, "../character_ui.py"), 'r')
    for line in readfile:
        text.write(line)
        if line == "# script variables\n":
            text.write("character_id_key=\"%s\"\n" % (character_id_key))
            text.write("character_id=\"%s\"\n" % (character_id))
            text.write("rig_layers_key=\"%s\"\n" % (rig_layers_key))
            text.write("links_key=\"%s\"\n" %
                       (context.scene.character_ui_links_key))
            text.write("custom_label=\"%s\"\n" %
                       (context.scene.character_ui_custom_label))
            text.write("always_show=%s\n" % (str(always_show)))

    readfile.close()

    # Run UI script
    exec(text.as_string(), {})
    return text


def register():
    register_class(OPS_OT_GenerateScript)


def unregister():
    unregister_class(OPS_OT_GenerateScript)
