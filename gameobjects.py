
""" Here should be Game objects, based on Physical objects """
import math
from kivy.graphics import VertexInstruction, Rectangle, Color
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.clock import Clock
from physics import Circle, DynamicObject, Box, phy, StaticBox
from animation import AnimationMixin
from gamecontext import GameContext
from controller import HeroRabbitController, HareController
from settings import BLOCK_SIZE, OBJECT_MASS, CHARACTER_MASS
from random import choice
from copy import copy


class Rock(Circle):
    
    def __init__(self, *pos):
        # define constants for object
        
        # Rock is circle, so we should
        # define its radius
        radius = BLOCK_SIZE[0] / 2.
        mass = OBJECT_MASS
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic
        texture = GameContext.resources['textures']['rock']
        
        super(Rock, self).__init__(pos=pos, radius=radius,
                                   elasticity=elasticity, mass=mass,
                                   moment=moment, draggable=True,
                                   texture=texture)
    def define_shape(self):
        self.shape = phy.Circle(self.body, self.radius-4)


class Rock2(Box):

    def __init__(self, *pos, **kw):
        # note that order of vertices should be counterclockwise
        size = BLOCK_SIZE  # size of texture
        self.vertices = [(63, 6), (63, 47), (51, 59), (23, 59), (3, 27), (3, 6)]  # taken from stone-02_BORDERS.png
        self.mass_center = (-36, -36)  # size_of_text_texture/2
        texture = GameContext.resources['textures']['rock2']

        # physical params
        mass = OBJECT_MASS
        moment = 1e500  # very high moment to prevent rotation
        elasticity = 0.1  # not elastic

        super(Rock2, self).__init__(mass, pos=pos, elasticity=elasticity, moment=moment, texture=texture,
                                    draggable=True, size=size, **kw)

    def define_shape(self):
        self.shape = phy.Poly(self.body, self.vertices, offset=self.mass_center)


class Wood(Box):

    def __init__(self, *pos, **kw):
        # note that order of vertices should be counterclockwise
        size = BLOCK_SIZE  # size of texture
        # taken from log-01_BORDERS.png:
        self.vertices = [(61, 0), (71, 4), (71, 17), (68, 59), (55, 71), (41, 71), (21, 62), (0, 27), (0, 17), (7, 3)]
        self.mass_center = (-36, -36)  # size_of_text_texture/2
        texture = GameContext.resources['textures']['wood']

        # physical params
        mass = OBJECT_MASS
        moment = 1e500  # very high moment to prevent rotation
        elasticity = 0.1  # not elastic

        super(Wood, self).__init__(mass, pos=pos, elasticity=elasticity, moment=moment, texture=texture,
                                   draggable=True, size=size, **kw)

    def define_shape(self):
        self.shape = phy.Poly(self.body, self.vertices, offset=self.mass_center)


class FlipMixin(object):
    """ Provides for mixed class ability to
        flip its texture
    """

    # TODO: for optimization it should be
    # rewritten with Cython

    h_flipped = False

    def flip_h(self):
        """ Flip sprite in horizontal direction """
        self.h_flipped = not self.h_flipped
        for obj in self.widget.canvas.children:
            if isinstance(obj, VertexInstruction):
                x1, x2, x3, x4, x5, x6, x7, x8 = obj.tex_coords
                obj.tex_coords = [x3, x4, x1, x2, x7, x8, x5, x6]
    
    def post_redraw_hook(self):
        if self.h_flipped:
            self.flip_h()
            self.h_flipped = True


class Character(Box, FlipMixin):

    """ Base class for all characters """
    
    def __init__(self, inner_pos, controller, **kw):
        
        self.controller = controller
        super(Character, self).__init__(pos=inner_pos, **kw)
    

class HeroRabbit(Character, AnimationMixin):
    
    """ Hero rabbit object """
    
    restore_original = False # never restore original texture after animation
    
    def __init__(self, *inner_pos):
        
        mass = CHARACTER_MASS
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic
        texture = GameContext.resources['textures']['rabbit_hero']
        size = BLOCK_SIZE
        
        self.body_size = (46, 66)
        
        self.animations['idle'] = GameContext.resources['animations']['hero_idle']
        self.animations['run'] = GameContext.resources['animations']['hero_run']
        self.animations['run_down'] = GameContext.resources['animations']['hero_run_down']
        self.animations['run_up'] = GameContext.resources['animations']['hero_run_up']
        self.animations['rotate_top'] = GameContext.resources['animations']['hero_rotate_top']
        self.animations['rotate_down'] = GameContext.resources['animations']['hero_rotate_down']
        # reversed animations
        self.animations['rotate_top_r'] = GameContext.resources['animations']['hero_rotate_top_r']
        self.animations['rotate_down_r'] = GameContext.resources['animations']['hero_rotate_down_r']
        
        # hero swim animations
        self.animations['swim_idle'] = GameContext.resources['animations']['hero_swim_idle']
        self.animations['swim'] = GameContext.resources['animations']['hero_swim']
        self.animations['swim_down'] = GameContext.resources['animations']['hero_swim_down']
        self.animations['swim_up'] = GameContext.resources['animations']['hero_swim_up']
        self.animations['swim_rotate_top'] = GameContext.resources['animations']['hero_swim_rotate_top']
        self.animations['swim_rotate_top_r'] = GameContext.resources['animations']['hero_swim_rotate_top_r']
        self.animations['swim_rotate_down'] = GameContext.resources['animations']['hero_swim_rotate_down']
        self.animations['swim_rotate_down_r'] = GameContext.resources['animations']['hero_swim_rotate_down_r']

        controller = HeroRabbitController(self)
        super(HeroRabbit, self).__init__(inner_pos, controller,
                                        mass=mass, moment=moment,
                                        elasticity=elasticity,
                                        texture=texture, size=size
                                        )
        GameContext.hero = self
        
        self.set_animation('idle')
        self.animate(endless=True)
        
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.body_size)
        

class Hare(Character, AnimationMixin):

    restore_original = False # never restore original texture after animation
    
    def __init__(self, *inner_pos):
        
        mass = CHARACTER_MASS
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic
        texture = GameContext.resources['textures']['rabbit_hero']
        size = BLOCK_SIZE
        
        self.body_size = (46, 66)
        
        self.animations['idle'] = GameContext.resources['animations']['hare_idle']
        self.animations['run'] = GameContext.resources['animations']['hare_run']
        self.animations['run_down'] = GameContext.resources['animations']['hare_run_down']
        self.animations['run_up'] = GameContext.resources['animations']['hare_run_up']
        self.animations['rotate_top'] = GameContext.resources['animations']['hare_rotate_top']
        self.animations['rotate_down'] = GameContext.resources['animations']['hare_rotate_down']
        # reversed animations
        self.animations['rotate_top_r'] = GameContext.resources['animations']['hare_rotate_top_r']
        self.animations['rotate_down_r'] = GameContext.resources['animations']['hare_rotate_down_r']
        
        # hare swim animations
        self.animations['swim_idle'] = GameContext.resources['animations']['hare_swim_idle']
        self.animations['swim'] = GameContext.resources['animations']['hare_swim']
        self.animations['swim_down'] = GameContext.resources['animations']['hare_swim_down']
        self.animations['swim_up'] = GameContext.resources['animations']['hare_swim_up']
        self.animations['swim_rotate_top'] = GameContext.resources['animations']['hare_swim_rotate_top']
        self.animations['swim_rotate_top_r'] = GameContext.resources['animations']['hare_swim_rotate_top_r']
        self.animations['swim_rotate_down'] = GameContext.resources['animations']['hare_swim_rotate_down']
        self.animations['swim_rotate_down_r'] = GameContext.resources['animations']['hare_swim_rotate_down_r']
        
        self.animations['rage_run'] = GameContext.resources['animations']['hare_rage_run']
        self.animations['rage_run_up'] = GameContext.resources['animations']['hare_rage_run_up']
        self.animations['rage_run_down'] = GameContext.resources['animations']['hare_rage_run_down']
        
        
        controller = HareController(self)
        super(Hare, self).__init__(inner_pos, controller,
                                        mass=mass, moment=moment,
                                        elasticity=elasticity,
                                        texture=texture, size=size
                                        )
        
        self.set_animation('idle')
        self.animate(endless=True)
        
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.body_size)


class Mountain(StaticBox):

    mountain_texture_names = {
        'vertical': {
            'top': [
                'mountain_vertical_top_end',
            ],
            'center': [
                'mountain_vertical1',
                'mountain_vertical2',
            ],
            'bottom': [
                'mountain_vertical_bottom_end'
            ]

        },
        'horizontal': {
            'left': [
                'mountain_horizontal_left_end_bottom',
            ],
            'center': [
                'mountain_horizontal_bottom1',
                'mountain_horizontal_bottom2',
                'mountain_horizontal_bottom3',
            ],
            'right': [
                'mountain_horizontal_right_end_bottom'
            ],

        },
        'top': {
            'left': [
                'mountain_horizontal_left_end_top',
            ],
            'center': [
                'mountain_horizontal_top1',
                'mountain_horizontal_top2',
                'mountain_horizontal_top3',
            ],
            'right': [
                'mountain_horizontal_right_end_top'
            ],
        },
        'center': 'mountain_central'
    }

    def __init__(self, *pos, **kw):
        self.type = kw.pop('type')
        texture = GameContext.resources['textures'][self.get_texture()]
        self.size = texture.size
        super(Mountain, self).__init__(pos=pos,
                                       size=texture.size,
                                       texture=texture,
                                       **kw)

    def get_texture(self):
        if self.type == 'center':
            return self.mountain_texture_names['center']
        m_type = self.type.split('_')
        return choice(self.mountain_texture_names[m_type[0]][m_type[1]])

    def get_horizontal_top_texture(self):
        m_type = self.type.split('_')
        return choice(self.mountain_texture_names['top'][m_type[1]])

    def widget_factory(self):
        widget = super(Mountain, self).widget_factory()
        if 'horizontal' in self.type or self.type == 'center':
            try:
                top_texture = GameContext.resources['textures'][self.get_horizontal_top_texture()]
            except IndexError:
                top_texture = GameContext.resources['textures']['mountain_central_top']
            with widget.canvas:
                Rectangle(pos=(widget.pos[0], self.pos[1]+36), texture=top_texture, size=top_texture.size)
        return widget


class Bush(StaticBox):
    def __init__(self, *pos, **kw):
        texture = GameContext.resources['textures']['bush']
        self.body_size = [BLOCK_SIZE[0]-4,BLOCK_SIZE[1]-4]
        super(Bush, self).__init__(pos=pos, size=texture.size, texture=texture, **kw)
    
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.body_size)


class HolyCarrot(StaticBox, AnimationMixin):
    
    restore_original = False
    
    def __init__(self, *pos, **kw):
        texture = GameContext.resources['textures']['holy_carrot']
        self.set_animation(GameContext.resources['animations']['holy_carrot'])
        super(HolyCarrot, self).__init__(pos=pos, size=texture.size, texture=texture, **kw)
        self.animate(True)
        
        GameContext.holy_carrot = self


class Tree(StaticBox, AnimationMixin):
    
    restore_original = False
    
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, BLOCK_SIZE)
    
    def __init__(self, *pos, **kw):
        growing = kw.pop('growing', False)
        texture = GameContext.resources['textures']['tree']
        self.animations['blow'] = copy(GameContext.resources['animations']['tree_blow'])
        self.animations['grow'] = copy(GameContext.resources['animations']['tree_grow'])
        super(Tree, self).__init__(pos=pos, size=texture.size, texture=texture, **kw)
        if growing:
            # rid shape from emulation
            self.space.remove(self.shape)
            self.start_grow()
        self._destroyed = False
            
    def start_grow(self, *largs):
        dummy = phy.Body()
        dummy.position = self.pos[0], self.pos[1]
        shape = phy.Poly.create_box(dummy, (BLOCK_SIZE[0] - 1., BLOCK_SIZE[1] - 1.))
        shapes = self.space.shape_query(shape)
        if shapes:
            for shape in shapes:
                if not isinstance(shape, phy.Segment):
                    self.start_grow_deffered(2)
                    return
        
        self.space.add(self.shape)
        self._destroyed = False
        self.set_animation('grow', True)
        self.animate()
        if GameContext.game:
            GameContext.game.reindex_graphics()
    
    def start_grow_deffered(self, dt=4):
        Clock.schedule_once(self.start_grow, dt)
    
    def destroy(self, *largs):
        # first remove shape from emulated space
        if not self._destroyed:
            self._destroyed = True
            self.space.remove(self.shape)
            #then set blow animation
            self.set_animation('blow', True)
            self.animation_callback = self.start_grow_deffered()
            self.animate()
            GameContext.game.move_to_bottom(self)
    
    def widget_factory(self):
        t_pos = self.pos
        self.pos = self.pos[0], self.pos[1] + 18
        widget = super(Tree, self).widget_factory()
        self.pos = t_pos
        return widget
