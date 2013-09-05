class Animation(object):
    """
    Generic interface. Override __init__ in inherited class
    
    each frame in the list '_frames' is tuple (texture, time_to_show)
    to show animation, main method -- 'launch'
    """
    _frames = []
    
    def __init__(self, *args, **kwargs):
        self.current_frame = 0
        pass
    
    def next(self):
        if self.current_frame < len(self._frames):
            texture, _time = self._frames[self.current_frame]
            self.current_frame += 1
            return texture, _time
        else:
            self.current_frame = 0
            raise StopIteration
        
    def is_first_call(self):
        return self.current_frame == 0


# implementation
class SimpleAnimation(Animation):
    def __init__(self, frames):
        self._frames = frames
        super(SimpleAnimation, self).__init__()
