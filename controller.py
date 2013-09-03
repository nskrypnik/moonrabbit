from physics import phy


class Controller(object):

    def __call__(self, body):
        if body.force == phy.Vec2d(0,0):
            body.apply_force((300, -1000), r=(0, 0))

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
