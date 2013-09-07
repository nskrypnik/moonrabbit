
""" Here should be Game objects, based on Physical objects """

from kivy.graphics import VertexInstruction, Rectangle, Color
from kivy.uix.scatter import ScatterPlane
from physics import Circle, DynamicObject, phy
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


class Rock2(DynamicObject):

    def __init__(self, *pos, **kw):
        # note that order of vertices should be counterclockwise
        self.size = (72, 72) # size of texture
        self.vertices = [(69, 3), (69, 50), (54, 65), (20, 65), (0, 27), (0, 3)] # taken from stone-02_BORDERS.png
        self.mass_center = (-36, -36) # size_of_text_texture/2
        texture = GameContext.resources['textures']['rock2']

        # physical params
        mass = 1e50
        moment = 1e500 # very high moment to prevent rotation
        elasticity = 0.1 # not elastic

        super(Rock2, self).__init__(mass, pos=pos, elasticity=elasticity, moment=moment, texture=texture,
                                    draggable=True, **kw)

    def define_shape(self):
        self.shape = phy.Poly(self.body, self.vertices, offset=self.mass_center)

    def widget_factory(self):
        widget = ScatterPlane(size=self.size)
        widget.center = self.pos
        with widget.canvas:
            if self.texture:
                Color(1, 1, 1, 1)
                Rectangle(pos=(0, 0), texture=self.texture, size=self.size)
        return widget


class Character(DynamicObject):
    
    """ Base class for all characters """
    
    def __init__(self, inner_pos, controller, **kw):
        
        self.controller = controller
        self.mirrored = False
        super(Character, self).__init__(pos=inner_pos, **kw)
    
    def mirror_horizontal(self):
        """ Flip sprite in horizontal direction """
        self.mirrored = not self.mirrored
        for obj in self.widget.canvas.children:
            if isinstance(obj, VertexInstruction):
                pass
        