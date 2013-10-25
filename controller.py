import random
import math
from kivy.clock import Clock
from physics import phy
from gamecontext import GameContext
from settings import HERO_SPEED, OBJECT_MASS, CHARACTER_MASS
from landscape import Grass, Sand, Water
from settings import BLOCK_SIZE, GAME_AREA_SIZE
from utils.astar import AStar, SQ_MapHandler, SQ_Location

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
        
        IDLE_TIME = 15

        self.faced = False
        self._state = 'IDLE'
        self._path = None # path of the character
        self.check_points = []
        self.next_point = None
        self.speed = HERO_SPEED
        self._counter = 30
        
        self._direction = 'l'
        self._prev_direction = ''

        self._directions = ['l', 'u', 'r', 'd']
        self._dir_opposites = {'u': 'd', 'd': 'u', 'l': 'r', 'r': 'l'}
        self._dir_vectors = {'l': (-1, 0), 'u': (0, 1), 'r': (1, 0), 'd': (0, -1)}
        self.swim_mode = False
        self._prev_swim_mode = False
        self.vision = VisionVector((-1, 0), 36)
        
        self.vision_vectors = {'l': VisionVector((-1, 0), BLOCK_SIZE[0]),
                               'u': VisionVector((0, 1), BLOCK_SIZE[1]),
                               'r': VisionVector((1, 0), BLOCK_SIZE[0]),
                               'd': VisionVector((0, -1), BLOCK_SIZE[1]),
                               }

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
        self._prev_swim_mode = self.swim_mode
        if isinstance(block, Water):
            self.swim_mode = True
        else:
            self.swim_mode = False
        super(BaseCharacterController, self).__call__()
    
    def get_path_to_goal(self):
        body = phy.Body()
        shape = phy.Poly.create_box(body, (BLOCK_SIZE[0]-1, BLOCK_SIZE[1]-1))
        game_map = []
        dx, dy = BLOCK_SIZE[0] / 2., BLOCK_SIZE[1] / 2. 
        for y in xrange(GAME_AREA_SIZE[1]):
            for x in xrange(GAME_AREA_SIZE[0]):
                body.position = x*BLOCK_SIZE[0] + dx, y*BLOCK_SIZE[1] + dy
                shape_list = GameContext.space.shape_query(shape)
                if not shape_list: 
                    game_map.append(1)
                else:
                    rigid = 1
                    for _s in shape_list:
                        if hasattr(_s.body, 'data') and not isinstance(_s, (phy.Segment)) and \
                            _s.body.data.__class__.__name__ not in self.MAY_GO_THROUGH:
                            rigid = -1
                            
                    game_map.append(rigid)
        # define start position
        start_pos = self.obj.body.position
        start_x, start_y = int(start_pos.x) / BLOCK_SIZE[0], int(start_pos.y) / BLOCK_SIZE[1]
        start = SQ_Location(start_x, start_y)
        # define end position
        game_map[GAME_AREA_SIZE[0]*start_y + start_x] = 1
        end_pos = self.get_goal_obj().body.position
        end_x, end_y = int(end_pos.x) / BLOCK_SIZE[0], int(end_pos.y) / BLOCK_SIZE[1]
        end = SQ_Location(end_x, end_y)
        game_map[GAME_AREA_SIZE[0]*end_y + end_x] = 1
        astar = AStar(SQ_MapHandler(game_map, GAME_AREA_SIZE[0], GAME_AREA_SIZE[1]))
        return astar.findPath(start,end)
    
    def load_path(self):
        self.check_points = [] # reset check point
        self.next_point = None
        start_pos = self.obj.body.position
        start_x, start_y = int(start_pos.x) / BLOCK_SIZE[0], int(start_pos.y) / BLOCK_SIZE[1]
        _prev_point = (start_x, start_y)
        node = self._path.get_next_node()
        while node:
            x, y = node.location.x, node    .location.y
            px, py = _prev_point
            if x == px:
                d = 'u' if py < y else 'd'
            if y == py:
                d = 'r' if px < x else 'l'
            _prev_point = x, y
            x, y = (x + 0.5)*BLOCK_SIZE[0], (y + 0.5)*BLOCK_SIZE[1]
            self.check_points.insert(0, (d, (x, y)))
            node = self._path.get_next_node()
    
    @property
    def _dir_opposite(self):
        return self._dir_opposites[self._direction]
    
    @wait_counter
    def do_idle(self):
        self._path = self.get_path_to_goal()
        if not self._path:
            # can't define map stay in this position
            self._counter = 15
        else:
            self.load_path()
            self.switch_to_moving()
        
    @wait_counter
    def do_turning(self):
        # check first after turning if current directions is avaliable
        #if self.meet_something():
        #    return
        self.switch_to_moving()
        
    def do_moving(self):
        # update body position
        pos = self.obj.body.position
        d, point = self.next_point
        v = self._dir_vectors[self._direction]
        self.speed = self.define_velocity()
        
        if (self._direction in ('l', 'r') and math.fabs(pos.x - point[0]) < self.speed):
            self.speed = math.fabs(pos.x - point[0])
        if (self._direction in ('u', 'd') and math.fabs(pos.y - point[1]) < self.speed):
            self.speed = math.fabs(pos.y - point[1])
        
        self.obj.body.position = pos.x + v[0]*self.speed, pos.y + v[1]*self.speed
        
        if self._prev_swim_mode != self.swim_mode:
            self.set_run_animation()
        
        pos = self.obj.body.position
        if (math.fabs(pos.x - point[0]) < .1) and (math.fabs(pos.y - point[1]) < .1):
            # if reached check point
            if self.meet_something():
                return
            self.next_point = None
            self.switch_to_moving()
    
    def switch_animation(self, animation, endless=False):
        #if self._state == 'SAWING':
        #    import ipdb; ipdb.set_trace()
        self.obj.set_animation(animation, True)
        self.obj.animate(endless=endless)
    
    def switch_to_moving(self):
        if not self.next_point:
            if self.check_points:
                self.next_point = self.check_points.pop()
            else:
                self.switch_animation('idle', True)
                self.set_state('IDLE', 15)
                return
        
        d = self.next_point[0]
        
        if self._direction != d:
            self.stop()
            self.switch_to_turning(d)
        else:
            self.set_run_animation()
            self.set_state('MOVING')
    
    def set_run_animation(self):
        animation = 'run' if self._direction in ('l', 'r')\
                        else 'run_up' if self._direction == 'u'\
                        else 'run_down'
        if self.swim_mode:
            animation = animation.replace('run', 'swim')
        if self.obj.animations[animation] != self.obj.current_animation:
            self.switch_animation(animation, True)
        
    def switch_to_turning(self, d):
        # current dirrection is bad
        if d == self._dir_opposite:
            choices = set(self._directions) - set([d, self._direction])
            d = random.choice(list(choices))
            
        if self._direction in ('l', 'r'):
            animation = {'u': 'rotate_top', 'd': 'rotate_down'}[d]
        else:
            animation = {'u': 'rotate_top_r', 'd': 'rotate_down_r'}[self._direction]
        
        self._prev_direction = self._direction
        self._direction = d
        
        if self._direction == 'r' and not self.obj.h_flipped \
                or self._direction == 'l' and self.obj.h_flipped:
            self.obj.flip_h()
        
        if self.swim_mode:
            animation = "swim_%s" % animation
        self.switch_animation(animation)
        self.set_state('TURNING', 15)

    def meet_something(self):
        vision = self.vision_vectors[self._direction]
        some = vision.look_from(self.obj.body.position)
        if some or self.faced:
            if self.meet_callback(some):
                # if returnse true - this function should make some custom logic
                return True
            self.stop()
            self.faced = False
            #self.switch_to_moving()
            self.set_state('IDLE', self.IDLE_TIME)
            if self.swim_mode:
                animation = 'swim_idle'
            else:
                animation = 'idle'
            self.switch_animation(animation, True)
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
        
        return SPEED
    
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
    
    IDLE_TIME = 15
    
    MAY_GO_THROUGH = ['HolyCarrot', 'HeroRabbit']
    
    def __init__(self, *args, **kw):
        super(HeroRabbitController, self).__init__(*args, **kw)
        self._steps_counter = 0
        self._steps = 0
            
    def do_moving(self):
        super(HeroRabbitController, self).do_moving()
        self._steps_counter += 1
        if self._steps_counter > 5:
            self._steps += 1
            self.context.ui.toolbar.steps.text = "STEPS:%s" % self._steps
            self._steps_counter = 0

    def meet_callback(self, some):
        if hasattr(some, 'body'):
            if some.body.data.__class__.__name__ ==  'HolyCarrot':
                self.context.game.game_over(win=True)
                return True
            
    def get_goal_obj(self):
        return GameContext.holy_carrot
                

class HareController(BaseCharacterController):
    
    MAY_GO_THROUGH = ['Tree', 'Hare']
    IDLE_TIME = 5
    
    _sawing_steps = 0
    
    def __call__(self):
        hero_pos = GameContext.hero.body.position
        pos = self.obj.body.position
        if (math.fabs(pos.x - hero_pos.x) < 1. and  math.fabs(pos.y - hero_pos.y) <= BLOCK_SIZE[1] + 1.) or \
             (math.fabs(pos.y - hero_pos.y) < 1. and  math.fabs(pos.x - hero_pos.x) <= BLOCK_SIZE[0] + 1.):
            self.kill_rabbit() 
            return
        super(HareController, self).__call__()
    
    def get_goal_obj(self):
        return GameContext.hero
    
    def __init__(self, *args, **kw):
        super(HareController, self).__init__(*args, **kw)
        self._state_handlers['SAWING'] = self.do_sawing
        self._sawn_tree = None
    
    def meet_callback(self, some):
        if hasattr(some, 'body'):
            if some.body.data.__class__.__name__ ==  'Tree':
                self.saw_the_tree(some.body.data)
                return True
            
    def kill_rabbit(self):
        hero_pos = GameContext.hero.body.position
        pos = self.obj.body.position
        d = ''
        if (math.fabs(pos.x - hero_pos.x) < 1. and  math.fabs(pos.y - hero_pos.y) <= BLOCK_SIZE[1] + 1.):
            # left or right
            if pos.y > hero_pos.y:
                d = 'd'
            else:
                d = 'u'
        if (math.fabs(pos.y - hero_pos.y) < 1. and  math.fabs(pos.x - hero_pos.x) <= BLOCK_SIZE[0] + 1.):
            if pos.x > hero_pos.x:
                d = 'l'
            else:
                d = 'r'
        animation = 'rage_run' if d in ('l', 'r')\
                        else 'rage_run_up' if d == 'u'\
                        else 'rage_run_down'
        if d == 'r' and not self.obj.h_flipped \
                or d == 'l' and self.obj.h_flipped:
            self.obj.flip_h()
        self.switch_animation(animation, True)
        
        GameContext.game.game_over(win=False)
        
    def switch_to_sawing(self, d=None):
        if not d:
            d = self._direction
        self._sawing_steps = 0
        animation = 'rage_run' if d in ('l', 'r')\
                        else 'rage_run_up' if d == 'u'\
                        else 'rage_run_down'
        self.switch_animation(animation, True)
        self.set_state('SAWING', 15)
        pos = self._sawn_tree.body.position
        self.next_point = self._direction, (pos.x, pos.y)
        self.check_points = []
        
    @wait_counter
    def do_sawing(self):
        # almost same as do moving
        # move to tree position
        
        self._sawn_tree.destroy()
        self.do_moving()
        if self._state != 'SAWING':
            # state was changed during moving
            self._sawn_tree = None
            
    @wait_counter
    def do_turning(self):
        # check first after turning if current directions is avaliable
        if self.next_point:
            d, p = self.next_point
            if d == self._direction and self.meet_something():
                return
        self.switch_to_moving()
    
    def saw_the_tree(self, tree):
        #tree.destroy()
        self._sawn_tree = tree
        self.switch_to_sawing()

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
        
        return SPEED
    
    def handle_collision(self, arbiter):
        obj = super(HareController, self).handle_collision(arbiter)
        return
        if hasattr(obj, 'data') and obj.data.__class__.__name__ == 'Tree':
            # if Hare faced tree - saw it
            Clock.schedule_once(obj.data.destroy, -1)
            self.switch_to_sawing()
            self.faced = False
    
    def switch_to_moving(self):
        self._path = self.get_path_to_goal()
        if not self._path:
            self.set_state('IDLE', self.IDLE_TIME)
            if self.swim_mode:
                animation = 'swim_idle'
            else:
                animation = 'idle'
            self.switch_animation(animation, True)
            return
        self.load_path()
        super(HareController, self).switch_to_moving()
            
