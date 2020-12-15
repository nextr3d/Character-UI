character_name = "Ellie"
bl_info = {
    "name": "Nextr Rig UI",
    "description": "Script for creating Nextr Rig UI",
    "author": "Nextr3D",
    "version": (3, 2, 0),
    "blender": (2, 91, 0)
}

links = {
"Link 1 Header":{
        "sub link 1": ("USER", "test.com"),
        "sub link 1": ("FUND", "test.com"),
        "sub link 1": ("URL", "test.com")
    }
}

"imports"
import bpy
from bpy.utils import (register_class,unregister_class)
from bpy.types import (Panel, Operator, PropertyGroup)
def get_rig():
    "returns an object with the character name"
    if character_name in bpy.data.objects:
        return bpy.data.objects[character_name]
    return False 
class Nextr_Rig(PropertyGroup):
    @classmethod
    def __init__(self):
        print("Rig initialization ", get_rig().name)
        
class VIEW3D_PT_nextr_rig(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = character_name
   
    @classmethod
    def poll(self, context):
        "show the panel if context.object is same as the character_name"
        print(context.object.name, character_name)
        if context.object and context.object.name == character_name:
            return True

class VIEW3D_PT_outfits(VIEW3D_PT_nextr_rig):
    bl_label = "Outfits"
    """no idea if this is the correct way but classes with identical ids get destroyed 
    so this way multiple classes with same(or atleast similar) functionality can exist at the same time"""
    bl_idname = "VIEW3D_PT_outfits_"+character_name 
    
    def draw(self, context):
        layout = self.layout
        layout.operator("nextr.empty", text="dunno" )
        
class OPS_OT_Empty(Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'

classes = (
VIEW3D_PT_outfits,
OPS_OT_Empty,
Nextr_Rig
)

def register():
    for c in classes:
        register_class(c)
    Nextr_Rig.__init__()
        
def unregister():
    for c in classes:
        unregister_class(c)

if __name__ == "__main__":
    register()