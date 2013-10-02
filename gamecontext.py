
from settings import BLOCK_SIZE, GAME_AREA_SIZE

class _GameContext(object):
    """ Should be singletone """
    
    game = None # main game object
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_GameContext, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.dynamic_objects = []
        self.static_objects = []
        self._objs = []
        self.characters = []
        self.space = None
        self.resources = {}
        self.dragged = {}
        self.ui = None
        self.scene_width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
        self.scene_height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
    
    def add(self, obj):
        
        from physics import DynamicObject, StaticObject
        from gameobjects import Character
        
        # if object support some widget - add it to main game widget
        if hasattr(obj, 'widget'):
            self.game.add_widget(obj.widget)

        self._objs.append(obj)
        if isinstance(obj, DynamicObject):
            self.dynamic_objects.append(obj)
            if obj.draggable:
                self.dragged[obj] = []
        
        if isinstance(obj, Character):
            self.characters.append(obj)
                
        if isinstance(obj, StaticObject):
            self.static_objects.append(obj)
    
    def set_game(self, game):
        self.game = game
    

GameContext = _GameContext()