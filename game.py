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
from physics import phy, init_physics


class MoonRabbitGame(Widget):
    block_width = 25
    block_height = 25
    _objects = DictProperty({})

    def __init__(self, **kwargs):
        super(MoonRabbitGame, self).__init__(**kwargs)
        self.num_of_blocks_X = Window.width / self.block_height
        self.num_of_blocks_Y = Window.height / self.block_width
        
        # create 2-dimensional array to store blocks
        self.blocks = [[0 for j in xrange(self.num_of_blocks_Y)]
                            for i in xrange(self.num_of_blocks_X)]
        
        self.init_physics()
        self.create_bounds()
        self.add_objects()
        # FIXME: rid test function from here
        self.test()

    def init_physics(self):
        self.space = init_physics()
        self.controller = Controller()
        Clock.schedule_interval(self.step, 1 / 30.)

    def step(self, dt):
        self.space.step(dt)
        self.update_objects()

    def update_objects(self):

        for body, obj in self._objects.iteritems():
            self.controller(body)
            # Now it's a hack
            # It must be something like
            # obj.update()
            p = body.position
            obj.pos = p

    def add_objects(self):
        """
        Add all objects to the map, except rabbit
        """
        pass

    def create_bounds(self):
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

        # self.add_circle(50, 200, 20)
        for i in range(5):
            body = phy.Body(100, 1e5)
            body.position = self.x + random.random() * self.width, \
                            self.y + random.random() * self.height

            radius = 20
            star = phy.Circle(body, radius)
            star.elasticity = 1
            star.friction = 1.0
            self.space.add(body, star)
            with self.canvas:
                Color(3, 0.3, 1, mode='hsv')
                # Color(3, 0.3, 1, mode='rgb')
                rect = Ellipse(
                    texture=Image(join(dirname(__file__), 'examples/PlanetCute PNG/Star.png'), mipmap=True).texture,
                    pos=(300, 400),
                    size=(40, 40),
                    segments=100,
                    angle_start=0,
                    angle_end=360,
                )
                body.apply_force((random.randint(900, 1000), random.randint(900, 1000)), r=(0, 0))
                self._objects[body] = rect


