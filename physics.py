
import math

from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.clock import Clock
from gamecontext import GameContext

#if platform() in ('ios', 'android'):
if True:
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
    space.damping = 0.0005
    return space


class PhysicalObject(object):
    
    apply_default_elasticity = True
    apply_default_friction = True
    
    def __init__(self, **kw):
        global space
        self.space = space
        self.shape = None
        self.texture = kw.pop('texture', None)
        self.elasticity = kw.pop('elasticity', 0.)
        self.friction = kw.pop('friction', 1.0)
        self.draggable = kw.pop('draggable', False)
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
            if self.apply_default_elasticity:
                shape.elasticity = self.elasticity
            if self.apply_default_friction:
                shape.friction = self.friction
                
        self.body.data = self
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
    
    def __init__(self, pos=(0, 0), **kw):
        self.pos = pos
        super(StaticObject, self).__init__(**kw)


class DynamicObject(PhysicalObject):
    
    def body_factory(self):
        # create static body
        body = phy.Body(self.mass, self.moment)
        if self.angular_velocity_limit:
            body.angular_velocity_limit = self.angular_velocity_limit  
        return body
    
    def __init__(self, mass, pos=(0, 0), moment=1e5, **kw):
        self.mass = mass
        self.moment = moment # define moment of inertia(inertia for rotation)
        self.pos = pos
        self.angular_velocity_limit = kw.pop('angular_velocity_limit', None)
        super(DynamicObject, self).__init__(**kw)

    def update(self):
        new_pos = self.body.position.x, self.body.position.y
        self.widget.center = new_pos
        if hasattr(self.widget, 'rotation'):
            self.widget.rotation = math.degrees(self.body.angle)


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
    
    def __init__(self, pos=(0, 0), size=(100, 100), **kw):
        """ Creates new static box with size and pos which is the position of the center """
        self.size = size
        super(StaticBox, self).__init__(pos=pos, **kw)


class Circle(DynamicObject):

    def __init__(self, mass, pos=(0, 0), radius=100, **kw):
        """ Creates new circle """
        self.radius = radius
        self.size = self.radius*2, self.radius*2
        super(Circle, self).__init__(mass, pos=pos, **kw)
    
    def define_shape(self):
        self.shape = phy.Circle(self.body, self.radius)
        
    def widget_factory(self):
        widget = ScatterPlane(size=self.size)
        widget.center = self.pos
        with widget.canvas:
            if not self.texture:
                Color(1, 0, 0, 1)
                Ellipse(pos=(0, 0), size=self.size)
            else:
                Color(1, 1, 1, 1)
                Ellipse(pos=(0, 0), texture=self.texture, size=self.size)
        return widget


class Box(DynamicObject):
    
    def __init__(self, mass, pos=(0, 0), size=(100., 100.), **kw):
        """ Creates new circle """
        self.size = size
        super(Box, self).__init__(mass, pos=pos, **kw)
    
    def define_shape(self):
        self.shape = phy.Poly.create_box(self.body, self.size)
  
    def widget_factory(self):
        widget = ScatterPlane(size=self.size)
        widget.center = self.pos
        with widget.canvas:
            if self.texture:
                Rectangle(pos=(0, 0), texture=self.texture, size=self.size)
            else:
                Color(0, 0, 1, 1)
                Rectangle(pos=(0, 0), size=self.size)
        return widget
        
    
