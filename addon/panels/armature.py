import bpy
from bpy.props import PointerProperty
from bpy.types import Collection, Object, Panel
from bpy.utils import register_class, unregister_class

from ..constants import  SceneProperties, CharacterProperties


class VIEW3D_PT_character_ui_armature(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Character-UI"
    bl_label = "Character UI Armature"

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, SceneProperties.OBJECT.value): return False

        o: Object | None = context.scene[SceneProperties.OBJECT.value]

        return o and o.type == "ARMATURE" and hasattr(o, CharacterProperties.CHARACTER_ID.value)

    def draw(self, context):
        layout = self.layout
        
        o: Object | None = context.scene[SceneProperties.OBJECT.value]
        
        if not o: return
        active_bcoll = o.data.collections.active

        row = layout.row()
        row.template_bone_collection_tree()

        col = row.column(align=True)
        col.operator("armature.collection_add", icon='ADD', text="")
        col.operator("armature.collection_remove", icon='REMOVE', text="")

        col.separator()

        col.menu("ARMATURE_MT_collection_context_menu", icon='DOWNARROW_HLT', text="")

        if active_bcoll:
            col.separator()
            col.operator("armature.collection_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("armature.collection_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row()

        sub = row.row(align=True)
        sub.operator("armature.collection_assign", text="Assign")
        sub.operator("armature.collection_unassign", text="Remove")

        sub = row.row(align=True)
        sub.operator("armature.collection_select", text="Select")
        sub.operator("armature.collection_deselect", text="Deselect")
       

modules = [
    VIEW3D_PT_character_ui_armature
]


def register():
    setattr(bpy.types.Scene, SceneProperties.OBJECT.value, PointerProperty(
        name="Character UI Object",
        description="Which object is going to be used as the main Character UI object",
        type=Object,
    ))
    setattr(bpy.types.Scene, SceneProperties.COLLECTION.value, PointerProperty(
        name="Collection",
        type=Collection
    ))
   
    for m in modules:
        register_class(m)


def unregister():
    delattr(bpy.types.Scene, SceneProperties.OBJECT.value)
    delattr(bpy.types.Scene, SceneProperties.COLLECTION.value)
   
    for m in reversed(modules):
        unregister_class(m)

