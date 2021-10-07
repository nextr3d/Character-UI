bl_info = {
    "name": "Character-UI",
    "description": "Addon for creating simple yet functional menus for your characters",
    "author": "nextr",
    "version": (1, 0, 0),
    "blender": (2, 92, 0),
	"location": "View3d > Sidebar > Character-UI",
	"category": 'Interface',
	"doc_url" : "https://github.com/nextr3d/Character-UI/wiki",
    "tracker_url" : "https://github.com/nextr3d/Character-UI/issues"
}

import importlib
from . import panels
from . import operators


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
    for m in reversed(modules): #Apparently it's better to unregister modules in the reversed order
        if hasattr(m,"unregister"):
            m.unregister()


if __name__ == "__main__":
    register()