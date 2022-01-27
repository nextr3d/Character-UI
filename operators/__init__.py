from . import links
from . import tooltip
from . import attributes
from . import use_as_cage
from . import use_as_driver
from . import edit_visibility
from . import attribute_groups
from . import edit_outfit_piece
from . import parent_to_character
from . import move_unassigned_objects
from . import generate_character_ui_script

modules = [
    links,
    tooltip,
    attributes,
    use_as_cage,
    use_as_driver,
    edit_visibility,
    attribute_groups,
    edit_outfit_piece,
    parent_to_character,
    move_unassigned_objects,
    generate_character_ui_script
]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
