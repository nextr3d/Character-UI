from . import links
from . import tooltip
from . import add_link
from . import attributes
from . import fix_new_id
from . import use_as_cage
from . import remove_links
from . import use_as_driver
from . import edit_visibility
from . import attribute_groups
from . import edit_outfit_piece
from . import parent_to_character
from . import move_unassigned_objects
from . import format_outfit_piece_name
from . import generate_character_ui_script
import importlib

modules = [
    links,
    tooltip,
    add_link,
    attributes,
    fix_new_id,
    use_as_cage,
    remove_links,
    use_as_driver,
    edit_visibility,
    attribute_groups,
    edit_outfit_piece,
    parent_to_character,
    move_unassigned_objects,
    format_outfit_piece_name,
    generate_character_ui_script
]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
