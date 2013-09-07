from os.path import dirname, join
import random
from kivy.graphics import Color, Rectangle, Mesh
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty

from kivy.uix.widget import Widget
from kivy.core.window import Window
from landscape import Water, Grass, Sand
from physics import phy, init_physics, StaticBox, Circle, Box
from gamecontext import GameContext
from gameobjects import AnimatedCircle, Rock, Rock2, HeroRabbit

from settings import BLOCK_SIZE, GAME_AREA_SIZE
from resources import load_resources

class BodyDragMgr():
    
    def __init__(self, space, body, touch):
        self.controlled = body
        self.controller = phy.Body(1e1000, 1e1000)
        self.space = space
        self.touch = touch
        self.controller.position = (touch.x, touch.y)
        anchor = phy.Vec2d(touch.x - self.controlled.position.x, \
                touch.y - self.controlled.position.y)
        anchor.rotate(-body.angle)
        args = self.controller, self.controlled, (0, 0), anchor
        joint = phy.constraint.PivotJoint(*args)
        joint.max_bias = 1e5
        self.joint = joint
        space.add(joint)
        
        # add Physical object as dragged to context
        GameContext.dragged[body.data].append(self)
        
    def update(self):
        #print self.touch.dx, self.touch.dy
        pos = self.controller.position.x + self.touch.dx, \
                self.controller.position.y + self.touch.dy
        self.controller.position = pos
    
    def release(self):
        self.space.remove(self.joint)
        self.controlled.velocity = 0., 0.
        self.controlled.angular_velocity = 0.
        self.touch.bodydragmgr = None
        GameContext.dragged[self.controlled.data].remove(self)


class MoonRabbitGame(Widget):
    
    block_width = BLOCK_SIZE[0]
    block_height = BLOCK_SIZE[1]
    spf = 1 / 30.

    def __init__(self, **kwargs):
        # setup game context
        self.context = GameContext
        self.context.game = self
        #self._touches = [] # container for touches
        
        super(MoonRabbitGame, self).__init__(**kwargs)
        self.num_of_blocks_X = GAME_AREA_SIZE[0]
        self.num_of_blocks_Y = GAME_AREA_SIZE[1]
        
        # create 2-dimensional array to store blocks
        self.blocks = [[0 for j in xrange(self.num_of_blocks_Y)]
                            for i in xrange(self.num_of_blocks_X)]
        
        self.init_physics()
        self.load_resources()
        self.setup_scene()
        self.create_bounds()
        
        def _handler(space, arbiter, *args, **kw):
            for shape in arbiter.shapes:
                if not hasattr(shape.body, 'data'):
                    continue
                phyobj = shape.body.data
                if not phyobj.draggable:
                    continue 
                dragmgrs = GameContext.dragged[phyobj]
                if dragmgrs:
                    if arbiter.total_ke > 1e5*shape.body.mass:
                        for dragmgr in dragmgrs:
                            dragmgr.release()
            return True
        
        self.space.add_collision_handler(0, 0, post_solve=_handler)
        
        # FIXME: rid test function from here
        # self.test()
        Clock.schedule_interval(self.update, self.spf)

    def init_physics(self):
        self.space = init_physics()

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
        
        self.build_landscape()
         
        st = StaticBox(pos=(300, 150), size=(100, 200), elasticity=.5)
        
        texture = Image(join(dirname(__file__), 'examples/PlanetCute PNG/Star.png'), mipmap=True).texture
        texture = texture.get_region(1, 20, 98, 98)
        
        rock = Rock(600, 500)
        rock2 = Rock2(600, 100)      
        HeroRabbit(700, 600)

    
    def build_landscape(self):
        # while build only with grass
        with self.canvas:
            for i in xrange(self.num_of_blocks_X):
                for j in xrange(self.num_of_blocks_Y):
                    if (i, j) in ((0, 0), (0, 1), (1, 0), (1, 1), (1, 3), (5, 2)):
                        landscape = Water(
                            pos=(i*self.block_width, j*self.block_height),
                            size=(self.block_width, self.block_height)
                        )
                    else:
                        landscape = Grass(
                            pos=(i*self.block_width, j*self.block_height),
                            size=(self.block_width, self.block_height)
                        )
                    self.blocks[i][j] = landscape
                    
    

    def update(self, dt):
        self.context.space.step(self.spf)
        for obj in self.context.dynamic_objects:
            obj.update()
        for obj in self.context.characters:
            obj.controller()
    
    def on_touch_down(self, touch):
        shape = self.context.space.point_query_first(phy.Vec2d(touch.x, touch.y))
        print shape
        # animation test here
        if shape and isinstance(shape.body.data, AnimatedCircle):
            shape.body.data.animate()
        if shape and isinstance(shape.body.data, HeroRabbit):
            shape.body.data.flip_h()
        # drag logic here
        if shape and shape.body.data.draggable:
            touch.bodydragmgr = BodyDragMgr(self.context.space, shape.body, touch)
        else:
            touch.bodydragmgr = None
        
    def on_touch_move(self, touch):
        if touch.bodydragmgr:
            touch.bodydragmgr.update()
    
    def on_touch_up(self, touch):
        if touch.bodydragmgr:
            touch.bodydragmgr.release()

    def load_resources(self):
        # see resources module
        load_resources()
                
    def get_block(self, x, y):
        i = int(x) / self.block_width
        j = int(y) / self.block_height
        if i >= self.num_of_blocks_X or j >= self.num_of_blocks_Y or x < 0 or y < 0:
            raise ValueError("Coordinates out of playground")
        return self.blocks[i][j]

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
