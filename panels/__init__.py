from . import main
from . import body
from . import outfits
from . import physics
from . import generate
from . import rig_layers
from . import attributes
from . import miscellaneous
import importlib


modules = [
    main,
    body,
    outfits,
    rig_layers,
    attributes,
    physics,
    miscellaneous,
    generate
]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
