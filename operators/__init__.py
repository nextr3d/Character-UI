from . import generate_character_ui_script

modules = [
   generate_character_ui_script
]

def register():
	for m in modules:
		m.register()

def unregister():
	for m in reversed(modules):
		m.unregister()