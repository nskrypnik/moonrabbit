from kivy.graphics import Color, Rectangle
from kivy.core.image import Image
from kivy.graphics.fbo import Fbo
from gamecontext import GameContext
from animation import AnimationMixin
from settings import BLOCK_SIZE


class WaterAnimation(AnimationMixin):
    
    class DummyWidget(object):
        pass
    
    def __init__(self):
        self.widget = self.DummyWidget() 
        self.widget.canvas = Fbo(size=BLOCK_SIZE, clear_color=(0., 0., 0., 0.))  
        self.texture = GameContext.resources['textures']['water']
        self.set_animation(GameContext.resources['animations']['water'])
        with self.widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=(0, 0), size=BLOCK_SIZE, texture=self.texture)

class Landscape(Rectangle):
    velocity_coefficient = 1.0
    
    def __init__(self, *args, **kw):
        super(Landscape, self).__init__(*args, **kw)


class Grass(Landscape):

    def __init__(self, *args, **kw):
        kw['texture'] = GameContext.resources['textures']['grass']
        super(Grass, self).__init__(*args, **kw)


class Water(Landscape):
    _animation = None
    velocity_coefficient = 1.5

    def __init__(self, *args, **kw):
        if not Water._animation:
            Water._animation = WaterAnimation()
            Water._animation.animate(endless=True)
        kw['texture'] = self._animation.widget.canvas.texture
        super(Water, self).__init__(*args, **kw)


class Sand(Landscape):
    velocity_coefficient = 0.5
    def __init__(self, *args, **kw):
        kw['texture'] = GameContext.resources['textures']['sand']
        super(Sand, self).__init__(*args, **kw)

    
class Hole(Landscape):
    velocity_coefficient = 0.0


class Carrot(Landscape):
    velocity_coefficient = 0.0
