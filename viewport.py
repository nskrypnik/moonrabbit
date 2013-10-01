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

        x, y = touch.x, touch.y
        # let the child widgets handle the event if they want
        if self.collide_point(x, y) and not touch.grab_current == self:
            touch.push()
            touch.apply_transform_2d(self.to_local)
            if super(ScatterPlane, self).on_touch_move(touch):
                touch.pop()
                return True
            touch.pop()

        # rotate/scale/translate
        if touch in self._touches and touch.grab_current == self:
            if self.transform_with_touch(touch):
                self.dispatch('on_transform_with_touch', touch)
            self._last_touch_pos[touch] = touch.pos

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            return True
 
    def on_touch_up(self, touch):
        return super(Viewport, self).on_touch_up(touch)