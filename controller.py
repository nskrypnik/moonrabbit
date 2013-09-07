from physics import phy


class BaseController(object):
    
    def __init__(self, phyobj):
        self.obj = phyobj # set object we control

    def __call__(self):
        pass

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