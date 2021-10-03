from . import main
from . import body
from . import rig_layers
from . import attributes
from . import miscellaneous
from . import generate


modules = [
    main,
	body,
	rig_layers,
	attributes,
	miscellaneous,
	generate
]

def register():
	for m in modules:
		m.register()

def unregister():
	for m in reversed(modules):
		m.unregister()
