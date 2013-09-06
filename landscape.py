from kivy.graphics import Color, Rectangle
from kivy.core.image import Image
from kivy.graphics.fbo import Fbo
from gamecontext import GameContext
from animation import AnimationMixin
from settings import BLOCK_SIZE


class WaterAnimation(AnimationMixin):
    
    def __init__(self):
        self.widget = Fbo(size=BLOCK_SIZE, clear_color=(0., 0., 0., 0.))      


class Landscape(Rectangle):
    velocity_coefficient = 1.0
    
    def __init__(self, *args, **kw):
        super(Landscape, self).__init__(*args, **kw)


class Grass(Landscape):
        
    def __init__(self, *args, **kw):
        kw['texture'] = GameContext.resources['textures']['grass']
        super(Grass, self).__init__(*args, **kw)

    

class Water(Landscape):
    velocity_coefficient = 1.5


class Sand(Landscape):
    velocity_coefficient = 0.7

    
class Hole(Landscape):
    velocity_coefficient = 0.0


class Carrot(Landscape):
    velocity_coefficient = 0.0
