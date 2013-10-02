import random
from physics import phy
from gamecontext import GameContext
from settings import HERO_SPEED, OBJECT_MASS, CHARACTER_MASS
from landscape import Grass, Sand, Water

def wait_counter(func):
    " Wait counter decorator "
    def wrap(self):
        if self._counter:
            self._counter -= 1
        else:
            func(self)
    return wrap


class Edge(object):
    pass


class VisionVector(object):
    
    def __init__(self, direction, distance):
        self._dir = direction
        self._d = distance
        self.space = GameContext.space
        
    def set_direction(self, direction):
        self._dir = direction
        
    def look_from(self, pos):
        if isinstance(pos, phy.Vec2d):
            x = pos.x
            y = pos.y
        else:
            x, y = pos
        lx, ly = self._dir[0]*self._d + x, \
                    self._dir[1]*self._d + y
        if lx < 0 or lx > GameContext.scene_width:
            return Edge()
        if ly < 0 or ly > GameContext.scene_height:
            return Edge()
        return self.space.point_query_first(phy.Vec2d(lx, ly))


class BaseController(object):
    
    def do_nothing(self):
        pass
    
    _state = 'IDLE' # inner state
    _counter = 0    # inner counter value
    
    _state_handlers = {'IDLE': do_nothing}
    
    def __init__(self, phyobj):
        self.obj = phyobj # set object we control
        self.context = GameContext

    def __call__(self):
        handler = self._state_handlers.get(self._state)
        if handler:
            handler(self)
    
    def set_state(self, state, counter=0):
        assert state in self._state_handlers
        self._state = state
        self._counter = counter

    def set_speed(self, speed):
        """
        set speed dependence on current ground
        """
        pass

    def turn_by_angle(self, angle):
        """
        rotate trajectory
        """
        pass

    def get_ground(self):
        """
        get current block
        """
        pass
    
    def handle_collision(self, arbiter):
        """ Implement handle of object collision here """
        pass


class HeroRabbitController(BaseController):
    
    """ This is the controller for main Rabbit character """
    
    _state = 'IDLE'
    _counter = 30
    _direction = 'l'
    _last_failed_direction = ''
    _steps_from_last_turning = 0
    _directions = ['l', 'u', 'r', 'd']
    _dir_vectors = {'l': (-1, 0), 'u': (0, 1), 'r': (1, 0), 'd': (0, -1)}
    faced = False
    vision = VisionVector((-1, 0), 36)
    
    @wait_counter
    def do_idle(self):
        self.context.ui.timer.start()
        self.switch_to_moving()
        
    @wait_counter
    def do_turning(self):
        self.switch_to_moving()
        
    def do_moving(self):
        self._steps_from_last_turning += 1
        some = self.vision.look_from(self.obj.body.position)
        if some or self.faced:
            if hasattr(some, 'body'):
                if some.body.data.__class__.__name__ == 'MoonStone':
                    self.context.game.game_over(win=True)
            self.stop()
            self.faced = False
            self.switch_to_turning()
            return
        self.obj.body.velocity = self.define_velocity()
    
    _state_handlers = {
                       'IDLE': do_idle,
                       'MOVING': do_moving,
                       'TURNING': do_turning,
                    }
    
    def switch_animation(self, animation, endless=False):
        self.obj.set_animation(animation, True)
        self.obj.animate(endless=endless)
    
    def switch_to_moving(self):
        animation = 'run' if self._direction in ('l', 'r')\
                        else 'run_up' if self._direction == 'u'\
                        else 'run_down'
        self.switch_animation(animation, True)
        self.set_state('MOVING')
        
    def switch_to_turning(self):
        direction_before = self._direction
        if self._direction in ('l', 'r'):
            self._direction = random.choice(('u', 'd') if self._steps_from_last_turning > 1 else \
                [d for d in ('u', 'd') if d != self._last_failed_direction])
            animation = {'u': 'rotate_top', 'd': 'rotate_down'}[self._direction]
        else:
            animation = {'u': 'rotate_top_r', 'd': 'rotate_down_r'}[self._direction]
            self._direction = random.choice(('l', 'r') if self._steps_from_last_turning > 1 else \
                [d for d in ('l', 'r') if d != self._last_failed_direction])
        
        if self._direction == 'r' and not self.obj.h_flipped \
                or self._direction == 'l' and self.obj.h_flipped:
            self.obj.flip_h()
        
        self.vision.set_direction(self._dir_vectors[self._direction])
        
        self.switch_animation(animation)
        self.set_state('TURNING', 15)

        self._last_failed_direction = direction_before
        self._steps_from_last_turning = 0
    
    def define_velocity(self):
        """ Should get velocity according to conditions """
        SPEED = HERO_SPEED
        
        # define landscape type where we are
        pos = self.obj.body.position 
        block = self.context.game.get_block(pos.x, pos.y)
        SPEED *= block.velocity_coefficient
        
        v = self._dir_vectors[self._direction]
        return v[0]*SPEED, v[1]*SPEED
    
    def handle_collision(self, arbiter):
        """ Implement handle of object collision here """
        
        # TODO: delete all this bullshit and implement EdgeVisor
        shape1, shape2 = arbiter.shapes[:2]
        
        other = None
        if hasattr(shape1.body, 'data') and shape1.body.data == self.obj:
                other = shape2.body
        else:
                other = shape1.body
                
        if other and hasattr(other, 'data') and other.data and other.data.draggable:
            x, y = self._dir_vectors[self._direction]
            if x:
                if self.obj.body.position.x*x > other.position.x*x:
                    return
            if y:
                if self.obj.body.position.y*y > other.position.y*y:
                    return

        if arbiter.total_ke > OBJECT_MASS:
            self.faced = True
        
    def stop(self):
        self.obj.body.velocity = (0, 0)
