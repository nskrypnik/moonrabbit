
from kivy.graphics import VertexInstruction
from kivy.clock import Clock
from copy import copy

GLOBAL_PAUSE = False

def set_global_pause(val):
    global GLOBAL_PAUSE
    GLOBAL_PAUSE = val

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
    
    def reset(self):
        self.current_frame = 0

class AnimationMixin(object):
    
    
    def __new__(cls, *args, **kw):
        self = super(AnimationMixin, cls).__new__(cls)

        self.current_animation = None
        self.animations = {}
        self.endless_animation = False
        self.animation_callback = None
        if hasattr(cls, 'restore_original'):
            self.restore_original = cls.restore_original
        
        return self
        
    
    def redraw(self):
        assert not self.widget is None
        
        for obj in self.widget.canvas.children:
            if isinstance(obj, VertexInstruction):
                obj.texture = self.texture
        
        if hasattr(self, 'post_redraw_hook'):
            self.post_redraw_hook()
                            
    def set_animation(self, animation, stop=False):
        """ Here you can set animation directly or give key of predefined animation """
        if stop:
            self.stop_animation()
        if isinstance(animation, Animation):
            self.current_animation = animation
        else:
            self.current_animation = self.animations[animation]
    
    def animate(self, endless=False):
        self.endless_animation = endless
        self._animate()
    
    def _animate(self, *largs):

        global GLOBAL_PAUSE
        
        if GLOBAL_PAUSE:
            Clock.schedule_once(self._animate, 0.1)
            return

        animation = self.current_animation
        if animation.is_first_call():
            # backup texture:
            self.original_texture = self.texture
        next_frame = next(animation, None)
        if next_frame is None: # all frames are shown
            if callable(self.animation_callback):
                self.callback()
            if not self.endless_animation:
                # restore texture
                if self.restore_original:
                    self.texture = self.original_texture
                    self.redraw()
                return
            else:
                next_frame = next(animation, None)
        texture, _time = next_frame
        self.texture = texture
        self.redraw()
        Clock.schedule_once(self._animate, _time)
    
    def stop_animation(self):
        if self.current_animation:
            self.current_animation.reset()
        Clock.unschedule(self._animate)
        

# implementation
class SimpleAnimation(Animation):
    def __init__(self, frames):
        self._frames = frames
        super(SimpleAnimation, self).__init__()
        

class ReverseAnimation(Animation):
    def __init__(self, frames):
        frames.reverse()
        self._frames = frames
        super(ReverseAnimation, self).__init__()


class ReturningAnimation(Animation):
    def __init__(self, frames):
        
        back_frames = copy(frames)
        back_frames.reverse()
        self._frames = frames
        self._frames.extend(back_frames)
        super(ReturningAnimation, self).__init__()
    

