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
            handler()
    
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


class BaseCharacterController(BaseController):
    
    """ This is the controller for main Rabbit character """
        
    def __init__(self, *args):

        self.faced = False
        self._state = 'IDLE'
        self._counter = 30
        self._direction = 'l'
        self._prev_direction = ''
        self._failed_directions = []
        self._steps_from_last_turning = 0
        self._directions = ['l', 'u', 'r', 'd']
        self._dir_opposites = {'u': 'd', 'd': 'u', 'l': 'r', 'r': 'l'}
        self._dir_vectors = {'l': (-1, 0), 'u': (0, 1), 'r': (1, 0), 'd': (0, -1)}
        self.swim_mode = False
        self._prev_swim_mode = False
        self.vision = VisionVector((-1, 0), 36)

        super(BaseCharacterController, self).__init__(*args)
        
        # set controller states
        self._state_handlers = {
                       'IDLE': self.do_idle,
                       'MOVING': self.do_moving,
                       'TURNING': self.do_turning,
                    }
    
    def __call__(self):
        # check if we are in swim mode
        pos = self.obj.body.position 
        block = self.context.game.get_block(pos.x, pos.y)
        if isinstance(block, Water):
            self.swim_mode = True 
        else:
            self.swim_mode = False
        super(BaseCharacterController, self).__call__()
    
    @property
    def _dir_opposite(self):
        return self._dir_opposites[self._direction]
    
    @wait_counter
    def do_idle(self):
        self.switch_to_moving()
        
    @wait_counter
    def do_turning(self):
        # check first after turning if current directions is avaliable
        if self.meet_something():
            return
        self.switch_to_moving()
        
    def do_moving(self):
        
        self._steps_from_last_turning += 1
        if self._steps_from_last_turning > 10:
            # clear failled directions
            self._failed_directions = []
            self._failed_directions.append(self._dir_opposite)
        if self._prev_swim_mode != self.swim_mode:
            self.set_run_animation()
            self._prev_swim_mode = self.swim_mode
        if self.meet_something():
            return
        self.obj.body.velocity = self.define_velocity()
    
    def switch_animation(self, animation, endless=False):
        #if self._state == 'SAWING':
        #    import ipdb; ipdb.set_trace()
        self.obj.set_animation(animation, True)
        self.obj.animate(endless=endless)
    
    def switch_to_moving(self):
        self.set_run_animation()
        self.set_state('MOVING')
    
    def set_run_animation(self):
        animation = 'run' if self._direction in ('l', 'r')\
                        else 'run_up' if self._direction == 'u'\
                        else 'run_down'
        if self.swim_mode:
            animation = animation.replace('run', 'swim')
        self.switch_animation(animation, True)
        
    def switch_to_turning(self):
        # current dirrection is bad
        _d = self._direction
        self._failed_directions.append(_d)
        # check to avoid loop
        if set(self._failed_directions) == set(self._directions):
            self._failed_directions = [_d, self._prev_direction]
        
        print self._failed_directions

        if self._direction in ('l', 'r'):
            turn_choices = ('u', 'd') if self._steps_from_last_turning > 10 else \
                [d for d in ('u', 'd') if d not in self._failed_directions]
            if not turn_choices:
                self._direction = self._prev_direction
            else:
                self._direction = random.choice(turn_choices)
            animation = {'u': 'rotate_top', 'd': 'rotate_down'}[self._direction]
        else:
            animation = {'u': 'rotate_top_r', 'd': 'rotate_down_r'}[self._direction]
            turn_choices = ('l', 'r') if self._steps_from_last_turning > 10 else \
                [d for d in ('l', 'r') if d not in self._failed_directions]
            if not turn_choices:
                self._direction = self._prev_direction
            else:
                self._direction = random.choice(turn_choices)
        
        if self._direction == 'r' and not self.obj.h_flipped \
                or self._direction == 'l' and self.obj.h_flipped:
            self.obj.flip_h()
        
        self.vision.set_direction(self._dir_vectors[self._direction])
        
        if self.swim_mode:
            animation = "swim_%s" % animation
        self.switch_animation(animation)
        self.set_state('TURNING', 15)

        self._steps_from_last_turning = 0
        self._prev_direction = _d
        
    def meet_something(self):
        some = self.vision.look_from(self.obj.body.position)
        if some or self.faced:
            if self.meet_callback(some):
                # if returnse true - this function should make some custom logic
                return True
            self.stop()
            self.faced = False
            self.switch_to_turning()
            return True
        return False
    
    def meet_callback(self, some):
        pass
    
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
        
        return other
        
    def stop(self):
        self.obj.body.velocity = (0, 0)
        

class HeroRabbitController(BaseCharacterController):
    
    @wait_counter
    def do_idle(self):
        self.context.ui.timer.start()
        self.switch_to_moving()

    def meet_callback(self, some):
        if hasattr(some, 'body'):
            if some.body.data.__class__.__name__ ==  'HolyCarrot':
                self.context.game.game_over(win=True)
                return True


class HareController(BaseCharacterController):
    
    _sawing_steps = 0
    
    def __init__(self, *args, **kw):
        super(HareController, self).__init__(*args, **kw)
        self._state_handlers['SAWING'] = self.do_sawing
        self.tree_vision = VisionVector((-1, 0), 54)
        
    
    def meet_callback(self, some):
        if hasattr(some, 'body'):
            if some.body.data.__class__.__name__ ==  'HeroRabbit':
                self.switch_to_sawing()
                self.context.game.game_over(win=False, text="Rabbit was sawn by Hare")
                return True
            
    def switch_to_sawing(self):
        self._sawing_steps = 0
        animation = 'rage_run' if self._direction in ('l', 'r')\
                        else 'rage_run_up' if self._direction == 'u'\
                        else 'rage_run_down'
        self.switch_animation(animation, True)
        self.set_state('SAWING')
        
    def switch_to_turning(self):
        super(HareController, self).switch_to_turning()
        self.tree_vision.set_direction(self._dir_vectors[self._direction])
    
    def do_sawing(self):
        # almost same as do moving
        if self._sawing_steps > 30:
            self.switch_to_moving()
        if self.meet_something():
            return
        self.obj.body.velocity = self.define_velocity()
        self._sawing_steps += 1
    
    def meet_something(self):
        some = self.tree_vision.look_from(self.obj.body.position)
        if some:
            if hasattr(some, 'body') and some.body.data.__class__.__name__ ==  'Tree':
                some.body.data.destroy()
                self.switch_to_sawing()
                return True
        return super(HareController, self).meet_something()

    def define_velocity(self):
        SPEED = HERO_SPEED
        
        # define landscape type where we are
        pos = self.obj.body.position 
        block = self.context.game.get_block(pos.x, pos.y)
        if isinstance(block, Water):
            # hardcoded value for speed on water for Hare
            SPEED = HERO_SPEED*0.5
        else:
            SPEED *= block.velocity_coefficient
        
        v = self._dir_vectors[self._direction]
        return v[0]*SPEED, v[1]*SPEED
    
    def handle_collision(self, arbiter):
        obj = super(HareController, self).handle_collision(arbiter)
        if hasattr(obj, 'data') and obj.data.__class__.__name__ == 'Tree':
            # if Hare faced tree - saw it
            obj.data.destroy()
            self.switch_to_sawing()
            self.faced = False
            
