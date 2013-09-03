
import random

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from landscape import Water, Grass, Sand
from physics import phy, init_physics, StaticBox
from gamecontext import GameContext


class MoonRabbitGame(Widget):
    block_width = 25
    block_height = 25
    spf = 1 / 30.
    
    def __init__(self, **kwargs):
        # setup game context
        self.context = GameContext
        self.context.game = self
        
        super(MoonRabbitGame, self).__init__(**kwargs)
        self.num_of_blocks_X = Window.width / self.block_height
        self.num_of_blocks_Y = Window.height / self.block_width
        
        # create 2-dimensional array to store blocks
        self.blocks = [[0 for j in xrange(self.num_of_blocks_Y)]
                            for i in xrange(self.num_of_blocks_X)]
        
        self.init_physics()
        self.setup_scene()
        
        # FIXME: rid test function from here
        #self.test()
        
        Clock.schedule_interval(self.update, self.spf)
    
    def init_physics(self):
        init_physics()
        self.create_bounds()
        
    def create_bounds(self):
        """ Make bounds of the game space """
        # Bounds should be created for
    
    def setup_scene(self):
        """ Create here and add to scene all game objects """ 
        StaticBox(pos=(300, 150), size=(100, 200))
        
    def update(self, dt):
        self.context.space.step(self.spf)
        for obj in self.context.dynamic_objects:
            obj.update()
                    
    def test(self):
        with self.canvas:
            allowed_landscapes = (Water, Grass, Sand)
            for i in xrange(self.num_of_blocks_X):
                for j in xrange(self.num_of_blocks_Y):
                    rand_landscape = allowed_landscapes[random.randint(0, 2)]
                    self.blocks[i][j] = rand_landscape(
                        pos=(i*self.block_width, j*self.block_height),
                        size=(self.block_width, self.block_height)
                    )
    
    def on_touch_down(self, touch):
        # this is for test purposes - returns shape by touch coordinates
        shape = self.context.space.point_query_first(phy.Vec2d(touch.x, touch.y))
        print shape
