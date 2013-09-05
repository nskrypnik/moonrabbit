from kivy.graphics import Color, Rectangle
from kivy.core.image import Image
from os.path import join, dirname

RESOURCES = join(dirname(__file__), 'resources')

class Landscape(Rectangle):
    velocity_coefficient = 1.0
    _texture = None
    
    def __init__(self, *args, **kw):
        # set appropriate color for drawing
        kw['texture'] = self._texture
        super(Landscape, self).__init__(*args, **kw)


class Grass(Landscape):
    texture_path = join(RESOURCES, 'grass/grass-01.png')
    _texture = Image(texture_path, mipmap=True).texture \
        .get_region(0, 0, 72, 72)
    

class Water(Landscape):
    velocity_coefficient = 1.5


class Sand(Landscape):
    velocity_coefficient = 0.7

    
class Hole(Landscape):
    velocity_coefficient = 0.0


class Carrot(Landscape):
    velocity_coefficient = 0.0
