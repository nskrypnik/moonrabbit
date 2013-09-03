
from kivy.utils import platform

if platform() in ('ios', 'android'):
    # use cymunk for mobile platforms 
    import cymunk as phy
else:
    # othervise use pymunk
    import pymunk as phy

# init space as global variable 
space = phy.Space()
 
def init_physics(**kw):
    """ init physics for game here """
    global space
    
    space.iterations = kw.pop('iterations', 30)
    space.gravity = kw.pop('gravity', (0, 0))
    space.collision_slop = kw.pop('collision_slop', 0.5)
    
    return space
    
