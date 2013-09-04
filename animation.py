from kivy.clock import Clock

class Animation(object):
    """
    Generic interface. Override __init__ in inherited class
    
    each frame in the list '_frames' is tuple (texture, time_to_show)
    to show animation, main method -- 'launch'
    """
    _frames = []
    
    def __init__(self, *args, **kwargs):
        pass
    
    def launch(self, drawer, frame_no=0):
        """
        drawer: function that accepts single argument - texture
        """
        if frame_no >= len(self._frames):
            return
        texture, _time = self._frames[frame_no]
        drawer(texture)
        Clock.schedule_once(lambda dt: self.launch(drawer, frame_no + 1), _time)


# implementation
class SimpleAnimation(Animation):
    def __init__(self, frames):
        self._frames = frames
        super(SimpleAnimation, self).__init__()
