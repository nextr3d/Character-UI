from . import links
from . import attributes
from . import use_as_mask
from . import use_as_cage
from . import edit_visibility
from . import use_as_deformer
from . import attribute_groups
from . import generate_character_ui_script

modules = [
    links,
    attributes,
    use_as_mask,
    use_as_cage,
    edit_visibility,
    use_as_deformer,
    attribute_groups,
    generate_character_ui_script
]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
