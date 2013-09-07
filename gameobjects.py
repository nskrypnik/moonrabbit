
""" Here should be Game objects, based on Physical objects """

from kivy.graphics import VertexInstruction
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Rectangle, Color, Ellipse
from physics import Circle, DynamicObject, Box, phy
from animation import AnimationMixin
from gamecontext import GameContext
from controller import HeroRabbitController
from settings import BLOCK_SIZE
from physics import phy

class AnimatedCircle(Circle, AnimationMixin):
    """ It's just for test """
    pass


class Rock(Circle):
    
    def __init__(self, *pos):
        # define constants for object
        
        # Rock is circle, so we should
        # define its radius
        radius = BLOCK_SIZE[0] / 2.
        mass = 1e50
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic
        texture = GameContext.resources['textures']['rock']
        
        super(Rock, self).__init__(pos=pos, radius=radius,
                                   elasticity=elasticity, mass=mass,
                                   moment=moment, draggable=True,
                                   texture=texture)
        
        
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
    

class Character(Box, FlipMixin):
    
    """ Base class for all characters """
    
    def __init__(self, inner_pos, controller, **kw):
        
        self.controller = controller
        super(Character, self).__init__(pos=inner_pos, **kw)
    

class HeroRabbit(Character, AnimationMixin):
    
    def __init__(self, *inner_pos):
        
        mass = 1e10
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic
        texture = GameContext.resources['textures']['rabbit_hero']
        size = BLOCK_SIZE
        
        self.body_size = (46, 66)
        
        controller = HeroRabbitController(self)
        super(HeroRabbit, self).__init__(inner_pos, controller,
                                        mass=mass, moment=moment,
                                        elasticity=elasticity,
                                        texture=texture, size=size
                                        )

        self.widget.bind(on_touch_down=lambda inst: self.flip_h())
        
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.body_size)
  
    