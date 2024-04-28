# from addon import operators
import importlib
from . import panels 
from . import operators

modules = [
    operators,
    panels
]

def register():
    for m in modules:
        importlib.reload(m)
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
