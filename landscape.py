from kivy.graphics import Color, Rectangle


class Landscape(Rectangle):
    _velocity_coefficient = 1.0
    _color = (1, 1, 1)
    
    def __init__(self, *args, **kwargs):
        # set appropriate color for drawing
        Color(*self._color)
        super(Landscape, self).__init__(*args, **kwargs)
    
    def get_velocity_coefficient(self):
        """
        how fast rabbit moves on this type of landscape
        """
        return self._velocity_coefficient


class Grass(Landscape):
    _color = (0, 255, 0)


class Water(Landscape):
    _velocity_coefficient = 1.5
    _color = (0, 0, 255)


class Sand(Landscape):
    _velocity_coefficient = 0.7
    _color = (255, 255, 0)
