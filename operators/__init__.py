from . import links
from . import generate_character_ui_script
from. import use_as_mask

modules = [
	links,
	use_as_mask,
   	generate_character_ui_script
]

def register():
	for m in modules:
		m.register()

def unregister():
	for m in reversed(modules):
		m.unregister()
