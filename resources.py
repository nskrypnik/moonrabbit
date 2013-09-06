
from kivy.core.image import Image
from gamecontext import GameContext
from animation import SimpleAnimation
from os.path import join, dirname
from settings import BLOCK_SIZE, GAME_AREA_SIZE


RESOURCES_DIR = join(dirname(__file__), 'resources')


def load_resources():
    context = GameContext
    
    textures = context.resources['textures'] = {}
    animations = context.resources['animations'] = {}
    
    texture_path = join(RESOURCES_DIR, 'grass/grass-01.png')
    texture = Image(texture_path, mipmap=True).texture \
        .get_region(0, 0, *BLOCK_SIZE)
    
    textures['grass'] = texture
    
    # load test star animation
    # TODO: delete it after it's unnecessary 
    frames = []
    frame_time = 0.04  # sec
    for i in xrange(6):
        texture = Image(join(dirname(__file__), 'examples/PlanetCute PNG/Star{}.png'.format(i)), mipmap=True).texture
        texture = texture.get_region(1, 20, 98, 98)
        frames.append((texture, frame_time))
    animations['star'] = SimpleAnimation(frames) # shine
