from os.path import dirname, join
import random
from kivy.graphics import Color, Rectangle, Mesh
from kivy.core.image import Image
from kivy.clock import Clock
from kivy.properties import DictProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from kivy.uix.widget import Widget
from kivy.core.window import Window
import sys
from landscape import *
from physics import phy, init_physics, StaticBox, Circle, Box, PhysicalObject
from gamecontext import GameContext
from gameobjects import Rock, Rock2, HeroRabbit, Hare, \
                        Mountain, Wood, Bush, Character, HolyCarrot, Tree
from settings import BLOCK_SIZE, GAME_AREA_SIZE
from resources import read_map
from animation import set_global_pause


class BodyDragMgr():
    
    """ Body drag manager object. Manage dragging of draggable objects with touching  """

    def __init__(self, space, body, touch):
        self.controlled = body
        self.controller = phy.Body(1e1000, 1e1000)
        self.space = space
        self.touch = touch
        self.released = False
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
        if not self.touch.bodydragmgr:
            return
        self.space.remove(self.joint)
        self.controlled.velocity = 0., 0.
        self.controlled.angular_velocity = 0.
        self.touch.bodydragmgr = None
        GameContext.dragged[self.controlled.data].remove(self)


class MoonRabbitGame(Widget):
    
    IDLE_MODE = 0
    PLANT_TREE_MODE = 1
    
    trees_count = 5
    block_width = BLOCK_SIZE[0]
    block_height = BLOCK_SIZE[1]
    game_area_size = BLOCK_SIZE[0]*GAME_AREA_SIZE[0],\
                     BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
    spf = 1 / 30.

    def __init__(self, **kwargs):
        # setup game context
        self.context = GameContext
        self.context.game = self
        #self._touches = [] # container for touches
        super(MoonRabbitGame, self).__init__(**kwargs)
        self.num_of_blocks_X = GAME_AREA_SIZE[0]
        self.num_of_blocks_Y = GAME_AREA_SIZE[1]
        
        self._touches = []

        # create 2-dimensional array to store blocks
        self.blocks = [[0 for j in xrange(self.num_of_blocks_Y)]
                       for i in xrange(self.num_of_blocks_X)]

        self.init_physics()
        #self.load_resources()
        self.setup_scene()
        self.create_bounds()

        self.space.add_collision_handler(0, 0, post_solve=self.collision_handler)
        
        # set game mode
        self.mode = self.IDLE_MODE
        self.folding_screen = None
        self.paused = False
        self.win = False
        
    def start_round(self):
        self.context.ui.greeting()
    
    def start(self):

        Clock.schedule_interval(self.update, self.spf)

    def collision_handler(self, space, arbiter, *args, **kw):
        
        for shape in arbiter.shapes:
            if not hasattr(shape.body, 'data'):
                continue
            phyobj = shape.body.data

            if isinstance(phyobj, Character):
                phyobj.controller.handle_collision(arbiter)
            
            if not phyobj or not phyobj.draggable:
                continue
            dragmgrs = GameContext.dragged[phyobj]
            if dragmgrs:
                if arbiter.total_ke > 1e8*shape.body.mass:
                    for dragmgr in dragmgrs:
                        Clock.schedule_once(lambda dt: dragmgr.release(), -1)
        return True

    def init_physics(self):
        self.space = init_physics()

    def create_bounds(self):
        """ Make bounds of the game space """
        # Bounds should be created for
        x0, y0 = (0, 0)
        x1 = self.game_area_size[0]
        y1 = self.game_area_size[1]
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
        options, landscapes, statics, dynamics = read_map('test.map')
        self.num_of_blocks_X, self.num_of_blocks_Y = options['size']
        with self.canvas:
            # init landscapes
            block_x = 0
            for i in xrange(self.num_of_blocks_X):
                block_y = 0
                for j in xrange(self.num_of_blocks_Y):
                    class_name = landscapes[i][j]
                    if class_name is not None:
                        clazz = eval(class_name.capitalize())
                    else:
                        clazz = Grass
                    block = clazz(pos=(block_x, block_y),
                                  size=(self.block_width, self.block_height), border=(0, 0))
                    self.blocks[i][j] = block
                    block_y += self.block_height 
                block_x += self.block_width

            # init dynamics
            for x, y, class_name in dynamics:
                if 'dynamics_as_blocks' in options and options['dynamics_as_blocks']:
                    x, y = (x + 0.5) * self.block_width, (y + 0.5) * self.block_height
                eval(class_name.capitalize())(x, y)
        
        with self.canvas:
            # draw or hero
            HeroRabbit(self.block_width/2., self.block_height/2.)
            Hare(self.block_width*3.5, self.block_height*3.5)

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
        
        _mountains = []
        _bushes= []
        
        for i in xrange(self.num_of_blocks_X):
            for j in xrange(self.num_of_blocks_Y):
                class_name = statics[i][j]
                if class_name is not None:
                    pos = (i + 0.5) * self.block_width, (j + 0.5) * self.block_height
                    if class_name == 'bush':
                        #Bush(*pos)
                        _bushes.append(pos)
                    elif class_name == 'mountain':
                        _mountains.append((pos, _get_mountain_type(i, j)))
                        #Mountain(*pos, type=_get_mountain_type(i, j))
                        
        Tree(self.block_width*2.5, self.block_height*1.5)
        
        with self.canvas:
            for pos in _bushes:
                Bush(*pos)
            
            for pos, type in _mountains:
                Mountain(*pos, type=type)

        HolyCarrot(13.5*self.block_width, 7.5*self.block_height)
        # This should be called at the end
        self.reindex_graphics()

    def update(self, dt):
        self.context.space.step(self.spf)
        for obj in self.context.dynamic_objects:
            obj.update()
        
        for obj in self.context.characters:
            obj.controller()
    
    def reindex_graphics(self):
        """ Update z-index of all objects on the scene.
        """
        for obj in self.context.static_objects:
            self.canvas.children.remove(obj.widget.canvas)
        # fill _objects_z_index
        _objects_z_index = {}
        for obj in self.context.static_objects:
            y = obj.widget.pos[1]
            if not y in _objects_z_index:
                _objects_z_index[y] = []
            _objects_z_index[y].append(obj)
        _keys = _objects_z_index.keys()
        _keys.sort()
        _keys.reverse()
        for k in _keys:
            objs = _objects_z_index[k]
            for obj in objs:
                self.canvas.add(obj.widget.canvas)
    
    def move_to_bottom(self, obj):
        canvas = obj.widget.canvas
        last_block = self.blocks[GAME_AREA_SIZE[0] - 1][GAME_AREA_SIZE[1] - 1]
        block_index = self.canvas.children.index(last_block)
        self.canvas.children.remove(canvas)
        self.canvas.children.insert(block_index + 1, canvas)

    def on_touch_down(self, touch):
        
        if self.mode == self.PLANT_TREE_MODE:
            self.plant_a_tree(touch)
            return
        
        self._touches.append(touch)
        shape = self.context.space.point_query_first(phy.Vec2d(touch.x, touch.y))
        print shape, int(touch.x) / 72, int(touch.y) / 72  
        
        # drag logic here
        if shape and shape.body.data.draggable:
            touch.bodydragmgr = BodyDragMgr(self.context.space, shape.body, touch)
        else:
            touch.bodydragmgr = None
        
        if not shape or shape.body.is_static:
            # if no shape was touched we should release this touch
            return False
        
        return True

    def on_touch_move(self, touch):
        if hasattr(touch, 'bodydragmgr') and touch.bodydragmgr:
            touch.bodydragmgr.update()
            return True
        else:
            return False

    def on_touch_up(self, touch):
        if touch in self._touches:
            self._touches.remove(touch)
            self.screen_mover = None
            if hasattr(touch, 'bodydragmgr') and touch.bodydragmgr:
                touch.bodydragmgr.release()
            
            return True
        else:
            return False

    def load_resources(self):
        # see resources module
        pass

    def get_indices_by_coord(self, x, y):
        return int(x) / self.block_width, int(y) / self.block_height

    def get_block(self, x, y):
        i, j = self.get_indices_by_coord(x, y)
        if i >= self.num_of_blocks_X or j >= self.num_of_blocks_Y or x < 0 or y < 0:
            raise ValueError("Coordinates out of playground")
        return self.blocks[i][j]

    def game_over(self, win=False, text=None):
        # stop timer
        self.win = win
        Clock.unschedule(self.update)
        if self.context.ui:
            self.context.ui.toolbar.disable()
        cb = self.context.app.finish_round
        # fade to black screen and do finish round
        self.context.app.fade_to_black(cb, da=0.03)
        
    def set_idle(self):
        self.mode = self.IDLE_MODE
    
    def set_plant_tree(self):
        self.mode = self.PLANT_TREE_MODE
        
    def switch_to_plant_tree(self, btn=None):
        if not self.paused and btn and not btn.disabled and self.trees_count:
            btn.disabled = True
            self.set_plant_tree()
            
    def plant_a_tree(self, touch):
        can_plant_tree = True
        body = phy.Body()
        game_pos = int(touch.x) / BLOCK_SIZE[0], int(touch.y) / BLOCK_SIZE[1]
        x, y = (game_pos[0] + 0.5)*BLOCK_SIZE[0], (game_pos[1] + 0.5)*BLOCK_SIZE[1]
        body.position = (x, y)
        shape = phy.Poly.create_box(body, (BLOCK_SIZE[0] - 1., BLOCK_SIZE[1] - 1.))
        shape_list = self.space.shape_query(shape)
        if shape_list:
            # can't place the tree cause it's close to other objects
            objs = []
            for shape in shape_list:
                if hasattr(shape.body, 'data') and isinstance(shape.body.data, PhysicalObject):
                    obj = shape.body.data
                    obj.color_mask.rgba = (1, 0, 0, 1) # color it to red
                    objs.append(obj)
            def _rid_color_mask(objs):
                for obj in objs:
                    obj.color_mask.rgba = 1, 1, 1, 1
            Clock.schedule_once(lambda dt: _rid_color_mask(objs), 0.2)
            can_plant_tree = False
        block = self.get_block(touch.x, touch.y)
        if isinstance(block, Water):
            block.set_color_mask(1, 0, 0, 1)
            Clock.schedule_once(lambda dt: block.set_color_mask(1, 1, 1, 1), 0.2)
            can_plant_tree = False
        
        if can_plant_tree:
            Tree(x, y, growing=True)
            self.trees_count -= 1
            self.reindex_graphics()
                    
        if self.context.ui:
            self.context.ui.toolbar.button_trees.disabled = False
            self.context.ui.toolbar.number_of_trees.text = 'x%s' % self.trees_count 
        self.set_idle()
        
    def pause(self, btn=None):
        self.paused = True
        Clock.unschedule(self.update)
        set_global_pause(True)
        if btn:
            btn.set_paused()
            btn.unbind(on_release=self.pause)
            btn.bind(on_release=self.resume)
        if self.folding_screen:
            color, rect = self.folding_screen
            color.rgba = 0, 0, 0, .5
            return
        with self.canvas.after:
            self.folding_screen = [Color(0, 0, 0, .5),
                                   Rectangle(pos=self.pos, size=self.size)]
    
    def resume(self, btn=None):
        self.paused = False
        Clock.schedule_interval(self.update, self.spf)
        set_global_pause(False)
        if btn:
            btn.set_resumed()
            btn.unbind(on_release=self.resume)
            btn.bind(on_release=self.pause)
        color, rect = self.folding_screen
        color.rgba = 0, 0, 0, 0
