
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
    
    def load_texture(key, path, region=None):
        texture_path = join(RESOURCES_DIR, path)
        texture = Image(texture_path, mipmap=True).texture
        if region:
            texture = texture.get_region(*region)
    
        textures[key] = texture
    
    load_texture('grass', 'grass/grass-01.png', (0, 0, BLOCK_SIZE[0], BLOCK_SIZE[1]))
    load_texture('water', 'terrain/water-01.png', (0, 0, BLOCK_SIZE[0], BLOCK_SIZE[1]))    
    load_texture('rock', 'one-cell-snags/stone-01.png')
    load_texture('rabbit_hero', 'hero/hero-rotate-down-01.png')
    
    # load test star animation
    # TODO: delete it after it's unnecessary 
    frames = []
    frame_time = 0.04  # sec
    for i in xrange(6):
        texture = Image(join(dirname(__file__), 'examples/PlanetCute PNG/Star{}.png'.format(i)), mipmap=True).texture
        texture = texture.get_region(1, 20, 98, 98)
        frames.append((texture, frame_time))
    animations['star'] = SimpleAnimation(frames) # shine

    # load water animation
    frames = []
    frame_time = 0.2  # sec
    for i in xrange(1, 6):
        texture = Image(join(RESOURCES_DIR, 'terrain/water-0{}.png'.format(i)), mipmap=True).texture
        frames.append((texture, frame_time))
    animations['water'] = SimpleAnimation(frames)