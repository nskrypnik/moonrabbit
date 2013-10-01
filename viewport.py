from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scatter import ScatterPlane
 
 
class Viewport(ScatterPlane):
    def __init__(self, **kwargs):
        width = kwargs.pop('width', 800)
        height = kwargs.pop('height', 600)
        kwargs.setdefault('size', (width, height))
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('do_scale', False)
        kwargs.setdefault('do_translation', False)
        kwargs.setdefault('do_rotation', False)
        super(Viewport, self).__init__( **kwargs)
 
    def fit_to_window(self, *args):
        if self.height > self.width:
            self.scale = Window.height/float(self.height)
        else:
            self.scale = Window.width/float(self.width)
 
        self.pos = 0, 0
        for c in self.children:
            c.size = self.size
 
    def add_widget(self, w, *args, **kwargs):
        super(Viewport, self).add_widget(w, *args, **kwargs)
        w.size = self.size
 
    def on_touch_down(self, touch):
        return super(Viewport, self).on_touch_down(touch)
 
    def on_touch_move(self, touch):
        return super(Viewport, self).on_touch_move(touch)
 
    def on_touch_up(self, touch):
        return super(Viewport, self).on_touch_up(touch)