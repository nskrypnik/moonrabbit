from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scatter import ScatterPlane
 
 
 
 
class Viewport(ScatterPlane):
    def __init__(self, **kwargs):
        width = kwargs.pop('width', 800)
        height = kwargs.pop('height', 600)
        kwargs.setdefault('size', (width, height))
        kwargs.setdefault('size_hint', (None, None))
        #kwargs.setdefault('do_scale', False)
        #kwargs.setdefault('do_translation', False)
        kwargs.setdefault('do_rotation', False)
        kwargs.setdefault('auto_bring_to_front', False)
        super(Viewport, self).__init__( **kwargs)

    def collide_point(self, x, y):
        return True
 
    def fit_to_window(self, *args):
        if Window.height > Window.width:
            self.scale = Window.height/float(self.height)
        else:
            self.scale = Window.width/float(self.width)
        
            
        self.scale_min = self.scale
        self.scale_max = self.scale*3
 
        self.pos = 0, 0
        for c in self.children:
            c.size = self.size
 
    def add_widget(self, w, *args, **kwargs):
        super(Viewport, self).add_widget(w, *args, **kwargs)
        w.size = self.size
 
    def on_touch_down(self, touch):
        return super(Viewport, self).on_touch_down(touch)
 
    def on_touch_move(self, touch):
        res = super(Viewport, self).on_touch_move(touch)
        (x, y), (w, h) = self.bbox
        if x > 0:
            self.pos = 0, self.pos[1]
        if y > 0:
            self.pos = self.pos[0], 0
        if x + w < Window.width:
            self.pos = Window.width - w, self.pos[1]
        if y + h < Window.height:
            self.pos = self.pos[0], Window.height - h
        
        return res
     
    def on_touch_up(self, touch):
        return super(Viewport, self).on_touch_up(touch)