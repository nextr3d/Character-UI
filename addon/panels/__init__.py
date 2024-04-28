from . import main
from . import generate
from . import armature
import importlib


modules = [
    main,
    generate,
    armature
]


def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
