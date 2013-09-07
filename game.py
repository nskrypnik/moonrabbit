from os.path import dirname, join
import random
from kivy.graphics import Color, Rectangle, Mesh
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivy.uix.widget import Widget
from kivy.core.window import Window
from landscape import *
from physics import phy, init_physics, StaticBox, Circle, Box
from gamecontext import GameContext
from gameobjects import AnimatedCircle, Rock, Rock2, HeroRabbit, Mountain, Wood, Bush, Character, MoonStone
from settings import BLOCK_SIZE, GAME_AREA_SIZE
from resources import load_resources, read_map


class Timer(object):
    def __init__(self, callback, time=90, **kw):
        self.timer_counter = time
        self.callback = callback

    def start(self):
        Clock.max_iteration = self.timer_counter
        Clock.schedule_interval(self.timer_callback, 1)

    def stop(self):
        self.timer_counter = 0
        Clock.unschedule(self.timer_callback)

    def pause(self):
        Clock.unschedule(self.timer_callback)

    def get_left_time(self):
        return self.timer_counter

    def get_formated_time(self):
        minute = self.timer_counter / 60 or '00'
        return "{minute}:{seconds}".format(minute=minute,
                                           seconds=self.timer_counter % 60)

    def timer_callback(self, dt):
        self.timer_counter -= 1
        self.callback()
        if self.timer_counter <= 0:
            self.stop()


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

        self.space.add_collision_handler(0, 0, post_solve=self.collision_handler)


        self.timer = Timer(self.update_time, time=5)
        self.clock = Label(text=self.timer.get_formated_time(),
                           pos=(Window.width - 100, Window.height-100),
                           font_size = 30
        )

        self.add_widget(self.clock)
        # self.timer.start()

        Clock.schedule_interval(self.update, self.spf)

    def update_time(self):
        left_seconds = self.timer.get_left_time()
        if left_seconds <= 0:
            self.game_over()
        self.clock.text = self.timer.get_formated_time()

    def collision_handler(self, space, arbiter, *args, **kw):

        for shape in arbiter.shapes:
            if not hasattr(shape.body, 'data'):
                continue
            phyobj = shape.body.data

            if isinstance(phyobj, Character):
                phyobj.controller.handle_collision(arbiter)

            if not phyobj.draggable:
                continue
            dragmgrs = GameContext.dragged[phyobj]
            if dragmgrs:
                if arbiter.total_ke > 1e5*shape.body.mass:
                    for dragmgr in dragmgrs:
                        dragmgr.release()
        return True

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

        # read map
        (self.num_of_blocks_X, self.num_of_blocks_Y), landscapes, statics, dynamics = read_map('test.map')
        with self.canvas:
            # init landscapes
            for i in xrange(self.num_of_blocks_X):
                for j in xrange(self.num_of_blocks_Y):
                    class_name = landscapes[i][j]
                    if class_name is not None:
                        clazz = eval(class_name.capitalize())
                    else:
                        clazz = Grass
                    self.blocks[i][j] = clazz(pos=(i * self.block_width, j * self.block_height),
                                              size=(self.block_width, self.block_height))

            # init dynamics
            for x, y, class_name in dynamics:
                eval(class_name.capitalize())(x, y)

            # draw or hero
            HeroRabbit(700, 600)

            # init statics
            def _is_mountain(i, j):
                return int(0 <= i < self.num_of_blocks_X and 0 <= j <= self.num_of_blocks_Y and
                           statics[i][j] == 'mountain')

            def _get_mountain_type(i, j):
                opensides = (_is_mountain(i - 1, j), _is_mountain(i, j + 1),
                             _is_mountain(i + 1, j), _is_mountain(i, j - 1))  # left, top, right, bottom
                opensides_to_type = {
                    (1, 1, 1, 1): 'center',
                    (1, 0, 1, 0): 'horizontal_center',
                    (0, 1, 0, 1): 'vertical_center',
                    (1, 0, 0, 0): 'horizontal_right',
                    (0, 1, 0, 0): 'vertical_bottom',
                    (0, 0, 1, 0): 'horizontal_left',
                    (0, 0, 0, 1): 'vertical_top',
                    }
                return opensides_to_type.get(opensides, 'horizontal_center')

            for i in xrange(self.num_of_blocks_X):
                for j in xrange(self.num_of_blocks_Y):
                    class_name = statics[i][j]
                    if class_name is not None:
                        pos = (i + 0.5) * self.block_width, (j + 0.5) * self.block_height
                        if class_name == 'bush':
                            Bush(*pos)
                        elif class_name == 'mountain':
                            print pos, _get_mountain_type(i, j)
                            Mountain(*pos, type=_get_mountain_type(i, j))


        MoonStone(300, 400)
        # Mountain(500, 372, type='vertical_top')
        # HeroRabbit(700, 600)

        # Mountain(356, 300, type='horizontal_left')
        # Mountain(428, 300, type='horizontal_center')
        # Mountain(572, 300, type='horizontal_center')
        # Mountain(644, 300, type='horizontal_right')
        #
        # Mountain(500, 498, type='vertical_top')
        # Mountain(500, 444, type='vertical_center')
        # Mountain(500, 372, type='vertical_center')
        # Mountain(500, 238, type='vertical_center')
        # Mountain(500, 166, type='vertical_bottom')
        #
        # Mountain(500, 300, type='center')

    # def build_landscape(self):
    #     # while build only with grass
    #
    #         for i in xrange(self.num_of_blocks_X):
    #             for j in xrange(self.num_of_blocks_Y):
    #                 if (i, j) in ((0, 0), (0, 1), (1, 0), (1, 1), (1, 3), (5, 2)):
    #                     landscape = Water(
    #                         pos=(i*self.block_width, j*self.block_height),
    #                         size=(self.block_width, self.block_height)
    #                     )
    #                 else:
    #                     landscape = Grass(
    #                         pos=(i*self.block_width, j*self.block_height),
    #                         size=(self.block_width, self.block_height)
    #                     )
    #                 self.blocks[i][j] = landscape

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

    def game_over(self, win=False):
        self.timer.stop()
        print "popup!!"
        if win:
            text = "You win!"
        else:
            text = "You lose!"
        Clock.unschedule(self.update)
        popup = Popup(title=text,
                      content=Label(text=text),
                      size=(400, 400),
                      size_hint=(None, None))
        popup.open()


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
