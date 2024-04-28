# from addon import operators
import importlib
from . import addon

bl_info = {
    "name": "Character-UI",
    "description": "Create simple yet functional menus for your characters",
    "author": "nextr",
    "version": (2, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3d > Sidebar > Character-UI",
    "category": 'Interface',
    "doc_url": "https://github.com/nextr3d/Character-UI/wiki",
    "tracker_url": "https://github.com/nextr3d/Character-UI/issues"
}

modules = [
    addon
]

def register():
    for m in modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()


def unregister():
    for m in reversed(modules):
        if hasattr(m, "unregister"):
            m.unregister()


if __name__ == "__main__":
    register()
