
from kivy.graphics import VertexInstruction
from kivy.clock import Clock

class Animation(object):
    """
    Generic interface. Override __init__ in inherited class
    
    each frame in the list '_frames' is tuple (texture, time_to_show)
    """
    
    def __init__(self, *args, **kw):
        self.current_frame = 0
    
    def set_frames(self, frames):
        self._frames = frames
    
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
    

class AnimationMixin(object):
    
    current_animation = None
    animations = {}
    stop_flag = False
    
    def redraw(self):
        assert not self.widget is None
        
        for obj in self.widget.canvas.children:
            if isinstance(obj, VertexInstruction):
                obj.texture = self.texture
                            
    def set_animation(self, animation):
        """ Here you can set animation directly or give key of predefined animation """
        if isinstance(animation, Animation):
            self.current_animation = animation
        else:
            self.current_animation = self.animations[animation]
    
    def animate(self, endless=False):
        
        if self.stop_flag:
            self.stop_flag = False
            return
        
        animation = self.current_animation
        if animation.is_first_call():
            # backup texture:
            self.original_texture = self.texture
        next_frame = next(animation, None)
        if next_frame is None: # all frames are shown
            if not endless:
                # restore texture
                self.texture = self.original_texture
                self.redraw()
                return
            else:
                next_frame = next(animation, None)
        texture, _time = next_frame
        self.texture = texture
        self.redraw()
        Clock.schedule_once(lambda dt: self.animate(endless=endless), _time)
    
    def stop_animation(self):
        self.stop_flag = True
        


# implementation
class SimpleAnimation(Animation):
    def __init__(self, frames):
        self._frames = frames
        super(SimpleAnimation, self).__init__()
