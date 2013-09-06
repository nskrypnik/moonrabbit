
""" Here should be Game objects, based on Physical objects """

from physics import Circle, DynamicObject
from animation import AnimationMixin
from gamecontext import GameContext
from settings import BLOCK_SIZE

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


class Character(DynamicObject):
    
    """ Base class for all characters """
    
    def __init__(self, inner_pos, controller, **kw):
        
        self.controller = controller
        super(Character, self).__init__(pos=inner_pos, **kw)
        
        