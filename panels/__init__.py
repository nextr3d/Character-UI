from . import main
from . import generate


modules = [
    main,
	generate
]

def register():
	for m in modules:
		m.register()

def unregister():
	for m in reversed(modules):
		m.unregister()
