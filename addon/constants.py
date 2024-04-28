from enum import Enum

class CharacterProperties(Enum):
    CHARACTER_ID = 'chui_character_id'
    CHARACTER_LABEL = 'chui_character_label'
    OUTFITS_COLLECTION = 'chui_outfits'
    HAIR_COLLECTION = 'chui_hair'
    PHYSICS_COLLECTION = 'chui_physics'
    BODY_COLLECTION = 'chui_body'
    CHARACTER_LINKS = 'chui_links'

class SceneProperties(Enum):
    OBJECT = "character_ui_object"
    COLLECTION = 'character_ui_collection'
    ALWAYS_SHOW = 'character_ui_always_show'