
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from gamecontext import GameContext

if platform() in ('ios', 'android'):
    # use cymunk for mobile platforms 
    import cymunk as phy
else:
    # othervise use pymunk
    import pymunk as phy

# init space as global variable 
space = phy.Space()
GameContext.space = space
 
def init_physics(**kw):
    """ init physics for game here """
    global space
    
    space.iterations = kw.pop('iterations', 30)
    space.gravity = kw.pop('gravity', (0, 0))
    space.collision_slop = kw.pop('collision_slop', 0.5)
    
    return space


class PhysicalObject(object):
    
    def __init__(self):
        global space
        self.space = space
        self.shape = None
        self._shapes = []
        self.body = self.body_factory()
        self.widget = self.widget_factory()
        self.define_shape()
        if hasattr(self, 'pos'):
            self.body.position = self.pos
        
        if not self.body.is_static:
            # adding static body to space is illegal
            self.space.add(self.body)
        for shape in self.shapes:
            self.space.add(shape)
        GameContext.add(self)
    
    @property
    def shapes(self):
        if self._shapes:
            return self._shapes
        else:
            if self.shape:
                return [self.shape]
            else:
                return []
    
    @shapes.setter
    def _set_shapes(self, val):
        self._shapes = val
    
    def widget_factory(self):
        return Widget()
    
    def body_factory(self):
        raise NotImplemented

    def define_shape(self):
        """ Should be overrided in subclass to define object shape """
        raise NotImplemented
        
    def update(self):
        """ Override it in subcalss if it supports updates """
        pass # do nothing


class StaticObject(PhysicalObject):
    
    def body_factory(self):
        # create static body
        return phy.Body()
    
    def __init__(self, pos=(0, 0)):
        self.pos = pos
        super(StaticObject, self).__init__()


class DynamicObject(PhysicalObject):
    
    def body_factory(self):
        # create static body
        return phy.Body(self.mass, self.moment)
    
    def __init__(self, mass, pos=(0, 0), moment=1e5):
        self.mass = mass
        self.moment = moment # define moment of inertia(inertia for rotation)
        super(PhysicalObject, self).__init__()


class StaticBox(StaticObject):
    
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.size)
  
    def widget_factory(self):
        widget = Widget(size=self.size)
        widget.center = self.pos
        with widget.canvas:
            if self.texture:
                Rectangle(pos=widget.pos, texture=self.texture, size=self.size)
            else:
                Color(0, 1, 0, 1)
                Rectangle(pos=widget.pos, size=self.size)
        return widget
    
    def __init__(self, pos=(0, 0), size=(100, 100), texture=None):
        """ Creates new static box with size and pos which is the position of the center """
        self.size = size
        self.texture = texture
        super(StaticBox, self).__init__(pos=pos)
    
