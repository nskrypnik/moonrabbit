
from kivy.core.image import Image
#from gamecontext import GameContext
from animation import SimpleAnimation, ReverseAnimation, ReturningAnimation
from os.path import join, dirname
from settings import BLOCK_SIZE, GAME_AREA_SIZE
from copy import copy
import json

RESOURCES_DIR = 'resources'

def loader_cb(percents):
    pass
    #if GameContext.loader:
    #    GameContext.loader.set_progress(percents)

def flip_horizontal(tex):
    #x1, x2, x3, x4, x5, x6, x7, x8 = tex.tex_coords
    #tex.tex_coords = [x3, x4, x1, x2, x7, x8, x5, x6]
    tex.uvpos = (tex.uvpos[0] + tex.uvsize[0], tex.uvpos[1])
    tex.uvsize = (-tex.uvsize[0], tex.uvsize[1])
    return tex

def load_resources(context):
    
    textures = context.resources['textures'] = {}
    animations = context.resources['animations'] = {}
    
    def load_texture(key, path, region=None, mipmap=False, wrap=None):
        texture_path = join(RESOURCES_DIR, path)
        texture = Image(texture_path, mipmap=mipmap).texture
        if region:
            texture = texture.get_region(*region)
    
        textures[key] = texture

    load_texture('grass', 'grass/grass-01.png', (0, 0, BLOCK_SIZE[0], BLOCK_SIZE[1]))
    load_texture('water', 'terrain/water-01.png', (0, 0, BLOCK_SIZE[0], BLOCK_SIZE[1]))
    load_texture('sand', 'terrain/sand-01.png', (0, 0, BLOCK_SIZE[0], BLOCK_SIZE[1]))
    load_texture('rock', 'one-cell-snags/stone-01.png')
    loader_cb(5)
    load_texture('rock2', 'one-cell-snags/stone-02.png')
    load_texture('wood', 'one-cell-snags/log-01.png')
    load_texture('bush', 'one-cell-snags/bush-01.png')
    load_texture('tree', 'tree/tree-01.png')
    loader_cb(10)
    load_texture('rabbit_hero', 'hero/hero-idle-side-01.png')
    load_texture('hare', 'hare/hare-idle-side-01.png')
    load_texture('mountain_horizontal_bottom1', 'mountains/mountain-horizontal-bottom-01.png')
    load_texture('mountain_horizontal_bottom2', 'mountains/mountain-horizontal-bottom-02.png')
    load_texture('mountain_horizontal_bottom3', 'mountains/mountain-horizontal-bottom-03.png')
    load_texture('mountain_horizontal_top1', 'mountains/mountain-horizontal-top-01.png')
    loader_cb(20)
    load_texture('mountain_horizontal_top2', 'mountains/mountain-horizontal-top-02.png')
    load_texture('mountain_horizontal_top3', 'mountains/mountain-horizontal-top-03.png')
    load_texture('mountain_horizontal_left_end_top', 'mountains/mountain-horizontal-left-end-top-01.png')
    load_texture('mountain_horizontal_left_end_bottom', 'mountains/mountain-horizontal-left-end-bottom-01.png')
    load_texture('mountain_horizontal_right_end_top', 'mountains/mountain-horizontal-right-end-top-01.png')
    load_texture('mountain_horizontal_right_end_bottom', 'mountains/mountain-horizontal-right-end-bottom-01.png')
    loader_cb(30)
    load_texture('mountain_vertical1', 'mountains/mountain-vertical-01.png')
    load_texture('mountain_vertical2', 'mountains/mountain-vertical-02.png')
    load_texture('mountain_vertical_top_start', 'mountains/mountain-vertical-top-start-01.png')
    load_texture('mountain_vertical_top_end', 'mountains/mountain-vertical-top-end-01.png')
    load_texture('mountain_vertical_bottom_start', 'mountains/mountain-vertical-down-start-01.png')
    load_texture('mountain_vertical_bottom_end', 'mountains/mountain-vertical-down-end-01.png')
    loader_cb(40)
    load_texture('mountain_central', 'mountains/mountain-center-center-01.png')
    load_texture('mountain_central_top', 'mountains/mountain-center-top-01.png')
    load_texture('holy_carrot', 'holy-carrot/holy-carrot-01.png')
    load_texture('toolbar_bg', 'interface/background.png')
    loader_cb(50)
    
    ##########################################################################
    # All tree animation
    ##########################################################################
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 5):
        texture = Image(join(RESOURCES_DIR, 'tree/tree-blow-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'tree/tree-place-01.png')).texture
    frames.append((texture, frame_time))
    
    animations['tree_blow'] = SimpleAnimation(frames)
    
    frames = []
    frame_time = 1.25  # sec
    for i in xrange(1, 5):
        texture = Image(join(RESOURCES_DIR, 'tree/tree-grow-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    frames.append((textures['tree'], frame_time))
    
    animations['tree_grow'] = SimpleAnimation(frames)
    loader_cb(55)
    
    ##########################################################################
    # Holly carrot animation
    ##########################################################################
    
    
    frames = []
    frame_time = 0.25  # sec
    for i in [3, 1, 2]:
        texture = Image(join(RESOURCES_DIR, 'holy-carrot/holy-carrot-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    
    animations['holy_carrot'] = ReturningAnimation(frames)

    # load water animation
    frames = []
    frame_time = 0.2  # sec
    for i in xrange(1, 6):
        texture = Image(join(RESOURCES_DIR, 'terrain/water-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['water'] = SimpleAnimation(frames)
    
    frame_time = 0.1
    
    # hero run down animation
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hero/hero-run-down-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hero/hero-run-down-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hero_run_down'] = SimpleAnimation(frames)
    
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hero/hero-run-up-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hero/hero-run-up-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hero_run_up'] = SimpleAnimation(frames)
    
    loader_cb(60)
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-idle-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_idle'] = SimpleAnimation(frames)
    
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-rotate-top-and-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_rotate_top'] = SimpleAnimation(frames)
    animations['hero_rotate_top_r'] = ReverseAnimation(copy(frames))

    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-rotate-down-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_rotate_down'] = SimpleAnimation(frames)
    animations['hero_rotate_down_r'] = ReverseAnimation(copy(frames))
    
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 10):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-run-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_run'] = SimpleAnimation(frames)
    
    loader_cb(65)
    ##########################################################################
    # Hero swim animations goes here
    ##########################################################################
    
    # hero swim run side
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-idle-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_swim_idle'] = SimpleAnimation(frames)
    
    # hero swim run side
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-run-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_swim'] = SimpleAnimation(frames)
    
    # hero swim up-down
    
    frame_time = 0.1
    
    # hero swim down 
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-run-down-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-run-down-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hero_swim_down'] = SimpleAnimation(frames)
    
    # hero swim down 
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-run-up-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-run-up-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hero_swim_up'] = SimpleAnimation(frames)
    
    loader_cb(70)
    # hero swim rotate top
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-rotate-top-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_swim_rotate_top'] = SimpleAnimation(frames)
    animations['hero_swim_rotate_top_r'] = ReverseAnimation(copy(frames))

    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hero/hero-swim-rotate-down-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hero_swim_rotate_down'] = SimpleAnimation(frames)
    animations['hero_swim_rotate_down_r'] = ReverseAnimation(copy(frames))
    
    loader_cb(75)
    
    ##########################################################################
    ##########################################################################
    #
    # Load Hare animation here
    #
    ##########################################################################
    ##########################################################################

    frames = []
    frame_time = 0.2  # sec
    for i in xrange(1, 6):
        texture = Image(join(RESOURCES_DIR, 'terrain/water-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['water'] = SimpleAnimation(frames)
    
    frame_time = 0.1
    
    # hare run down animation
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-run-down-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-run-down-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_run_down'] = SimpleAnimation(frames)
    
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-run-up-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-run-up-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_run_up'] = SimpleAnimation(frames)
    loader_cb(80)
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-idle-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_idle'] = SimpleAnimation(frames)
    
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-rotate-top-and-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_rotate_top'] = SimpleAnimation(frames)
    animations['hare_rotate_top_r'] = ReverseAnimation(copy(frames))
    
    loader_cb(85)

    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-rotate-down-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_rotate_down'] = SimpleAnimation(frames)
    animations['hare_rotate_down_r'] = ReverseAnimation(copy(frames))
    
    
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 9):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-run-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_run'] = SimpleAnimation(frames)
    
    loader_cb(90)
    ##########################################################################
    # Hare swim animations goes here
    ##########################################################################

    # hero swim run side
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-idle-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_swim_idle'] = SimpleAnimation(frames)

    # hare swim run side
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-run-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_swim'] = SimpleAnimation(frames)
    
    # hare swim up-down
    
    frame_time = 0.25
    
    # hare swim down 
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-run-down-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-run-down-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_swim_down'] = SimpleAnimation(frames)
    
    # hare swim down 
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-rotate-02.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-rotate-02.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_swim_up'] = SimpleAnimation(frames)
    
    # hare swim rotate top
    
    loader_cb(95)
    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-rotate-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_swim_rotate_top'] = SimpleAnimation(frames)
    animations['hare_swim_rotate_top_r'] = ReverseAnimation(copy(frames))

    frames = []
    frame_time = 0.25  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-swim-rotate-down-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_swim_rotate_down'] = SimpleAnimation(frames)
    animations['hare_swim_rotate_down_r'] = ReverseAnimation(copy(frames))

    frames = []
    frame_time = 0.15  # sec
    for i in xrange(1, 3):
        texture = Image(join(RESOURCES_DIR, 'hare/hare-rage-run-side-0{}.png'.format(i))).texture
        frames.append((texture, frame_time))
    animations['hare_rage_run'] = SimpleAnimation(frames)
    
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-rage-run-down-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-rage-run-down-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_rage_run_down'] = SimpleAnimation(frames)
    
    frames = []
    texture = Image(join(RESOURCES_DIR, 'hare/hare-rage-run-up-01.png'), nocache=True).texture
    frames.append((texture, frame_time))
    texture = Image(join(RESOURCES_DIR, 'hare/hare-rage-run-up-01.png')).texture
    texture = flip_horizontal(texture)
    frames.append((texture, frame_time))
    animations['hare_rage_run_up'] = SimpleAnimation(frames)
    loader_cb(100)

def read_map(fname):
    """
    read map from file which contains data in json format

    format of file:
    global dict which contains the next keys
        options: { "size": [num_of_blocks_X, num_of_blocks_Y], ...}
        landscapes: [(i,j,type), ...], where type is in ['grass', 'water', 'sand', 'hole', 'carrot']
        statics: [(i,j,type), ...], where type is in ['mountain', 'bush']
        dynamics: [(x,y,type), ...], where type is in ['wood', 'rock', 'rock2']
        trees: [(x, y), ... ]
        hero: [x, y]
        hare: [x, y]
    """

    required_fields = {'landscapes', 'statics', 'dynamics', 'options'}
    try:
        with open(fname, 'r') as ifile:
            data = ifile.read()
            map = json.loads(data)
            # check that all required fields are presented
            assert len(required_fields - set(map.keys())) == 0
    except:
        raise ValueError('Invalid map file')

    def list_to_2d_array(num_X, num_Y, lst):
        array = [[None for j in xrange(num_Y)]
                 for i in xrange(num_X)]
        for i, j, _type in lst:
            array[i][j] = _type
        return array

    # number of blocks
    num_X, num_Y = map['options']['size']
    landscapes = list_to_2d_array(num_X, num_Y, map['landscapes'])
    statics = list_to_2d_array(num_X, num_Y, map['statics'])
    dynamics = map['dynamics']

    return map['options'], landscapes, statics, dynamics, map['trees'], map['hero'], map['hare']
