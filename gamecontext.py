
from settings import BLOCK_SIZE, GAME_AREA_SIZE
from animation import set_global_pause, reset_animations
from resources import load_resources

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
        self.app = None
        self.resources = {}
        load_resources(self)
        self.reset()
        self.scene_width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
        self.scene_height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
        
    def reset(self):
        reset_animations()
        set_global_pause(False)
        self.space = None
        if hasattr(self, 'dynamic_objects'):
            _objs = self.dynamic_objects
            for obj in _objs:
                if hasattr(obj, 'stop_animation'):
                    obj.stop_animation()
                del obj
        self.dynamic_objects = []
        if hasattr(self, 'static_objects'):
            _objs = self.static_objects
            for obj in _objs:
                if hasattr(obj, 'stop_animation'):
                    obj.stop_animation()
                del obj
        self.static_objects = []
        self._objs = []
        self.characters = []
        self.dragged = {}
        self.ui = None
        self.menu = None
        self.loader = None
        self.scene = None
        self.hero = None
        self.holy_carrot = None
    
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