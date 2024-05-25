from . import main
from . import outfits
from . import generate
from . import armature
from . import miscellaneous
import importlib


modules = [
    main,
    outfits,
    generate,
    armature,
    miscellaneous
]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
