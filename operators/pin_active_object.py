from bpy.types import (Operator) 
from bpy.utils import (register_class, unregister_class)


class OPS_OT_PinActiveObject(Operator):
    bl_idname = 'character.pin_active_object'
    bl_label = 'Pin active object'
    bl_label = 'Pins active object'
    
    def execute(self, context):
        if context.active_object:
            if 'active_object' in context.scene:
                if context.scene['active_object']:
                    context.scene['active_object'] = None
                    self.report({'INFO'}, "Unpinned "+context.active_object.name)
                else:
                    context.scene['active_object'] = context.active_object
                    self.report({'INFO'}, "Pinned "+context.active_object.name)
                    context.scene['nextr_rig_properties_key'] = context.active_object.name+"_properties"
                    context.scene['nextr_rig_attributes_key'] = context.active_object.name+"_attributes"
            else:
                context.scene['active_object'] = context.active_object
                self.report({'INFO'}, "Pinned "+context.active_object.name)
        return {'FINISHED'}

def register():
    register_class(OPS_OT_PinActiveObject)

def unregister():
    unregister_class(OPS_OT_PinActiveObject)