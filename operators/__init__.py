from . import links
from . import helper
from . import attributes
from . import use_as_cage
from . import use_as_driver
from . import edit_visibility
from . import attribute_groups
from . import generate_character_ui_script

modules = [
    links,
    helper,
    attributes,
    use_as_cage,
    use_as_driver,
    edit_visibility,
    attribute_groups,
    generate_character_ui_script
]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
