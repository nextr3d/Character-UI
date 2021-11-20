from . import operators
from . import panels
import importlib
bl_info = {
    "name": "Character-UI",
    "description": "Addon for creating simple yet functional menus for your characters",
    "author": "nextr",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3d > Sidebar > Character-UI",
    "category": 'Interface',
    "doc_url": "https://github.com/nextr3d/Character-UI/wiki",
    "tracker_url": "https://github.com/nextr3d/Character-UI/issues"
}


modules = [
    panels,
    operators
]


def register():
    for m in modules:
        importlib.reload(m)
        if hasattr(m, 'register'):
            m.register()


def unregister():
    # Apparently it's better to unregister modules in the reversed order
    for m in reversed(modules):
        if hasattr(m, "unregister"):
            m.unregister()


if __name__ == "__main__":
    register()
