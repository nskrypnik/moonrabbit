from physics import phy
import random

def wait_counter(func):
    " Wait counter decorator "
    def wrap(self):
        if self._counter:
            self._counter -= 1
        else:
            func(self)
    return wrap


class BaseController(object):
    
    def do_nothing(self):
        pass
    
    _state = 'IDLE' # inner state
    _counter = 0    # inner counter value
    
    _state_handlers = {'IDLE': do_nothing}
    
    def __init__(self, phyobj):
        self.obj = phyobj # set object we control

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


class HeroRabbitController(BaseController):
    
    """ This is the controller for main Rabbit character """
    
    _state = 'IDLE'
    _counter = 20
    
    @wait_counter
    def do_idle(self):
        next_state = random.choice(['TURN_LEFT', 'TURN_RIGHT'])
    
    _state_handlers = {
                       'IDLE': do_idle   
                    } 
                       
                       