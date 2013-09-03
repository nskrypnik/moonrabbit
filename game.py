from os.path import dirname, join
import random
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty

from kivy.uix.widget import Widget
from kivy.core.window import Window
from controller import Controller
from landscape import Water, Grass, Sand
from physics import phy, init_physics, StaticBox, Circle
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
        self.create_bounds()
        # FIXME: rid test function from here
        # self.test()
        Clock.schedule_interval(self.update, self.spf)

    def init_physics(self):
        self.space = init_physics()
        self.controller = Controller()

    def step(self, dt):
        self.space.step(dt)
        self.update_objects()


    def create_bounds(self):
        """ Make bounds of the game space """
        # Bounds should be created for
        x0, y0 = (0, 0)
        x1 = Window.width
        y1 = Window.height
        space = self.space

        borders = [
            phy.Segment(space.static_body, phy.Vec2d(x0, y0), phy.Vec2d(x1, y0), 0),
            phy.Segment(space.static_body, phy.Vec2d(x0, y0), phy.Vec2d(x0, y1), 0),
            phy.Segment(space.static_body, phy.Vec2d(x1, y0), phy.Vec2d(x1, y1), 0),
            phy.Segment(space.static_body, phy.Vec2d(x0, y1), phy.Vec2d(x1, y1), 0),
        ]
        for b in borders:
            b.elasticity = 0.5
        self.space.add(borders)

    def setup_scene(self):
        """ Create here and add to scene all game objects """ 
        StaticBox(pos=(300, 150), size=(100, 200))
        
        texture = Image(join(dirname(__file__), 'examples/PlanetCute PNG/Star.png'), mipmap=True).texture
        texture = texture.get_region(1, 20, 98, 98)
        
        c = Circle(1e3, pos=(100, 100), radius=50, texture=texture)
        c.shape.elasticity = 1.
        c.body.apply_force((1e4, 1e4), r=(0, 0))
        #for i in range(5):
        #    pos = self.x + random.random() * self.width, \
        #                    self.y + random.random() * self.height
        #    print pos
        #    Circle(1e4, pos=pos, radius=50.0, texture=texture)

    def update(self, dt):
        self.context.space.step(self.spf)
        for obj in self.context.dynamic_objects:
            obj.update()
    
    def on_touch_down(self, touch):
        shape = self.context.space.point_query_first(phy.Vec2d(touch.x, touch.y))
        print shape
                    
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
