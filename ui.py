
import sys
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup 
from kivy.uix.button import Button
from kivy.uix.scatter import ScatterPlane
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.metrics import dp
from kivy.core.image import Image
from kivy.properties import ObjectProperty

from gamecontext import GameContext
from msgbox import MsgBox

FONT_NAME = 'resources/Intro.ttf'


class Timer(object):
    def __init__(self, callback, time=70, **kw):
        self.timer_counter = time
        self.callback = callback

    def start(self):
        Clock.max_iteration = self.timer_counter
        Clock.schedule_interval(self.timer_callback, 1)

    def stop(self):
        self.timer_counter = 0
        Clock.unschedule(self.timer_callback)

    def pause(self):
        Clock.unschedule(self.timer_callback)

    def get_left_time(self):
        return self.timer_counter

    def get_formated_time(self):
        minutes = self.timer_counter / 60
        seconds = self.timer_counter % 60

        return "{minutes}:{seconds}".format(minutes=minutes if minutes >=10 else '0'+str(minutes),
                                           seconds=seconds if seconds >=10 else '0'+str(seconds))

    def timer_callback(self, dt):
        self.timer_counter -= 1
        self.callback()
        if self.timer_counter <= 0:
            self.stop()


class ToolBar(ScatterPlane):
    
    _height = 55
    
    def __init__(self, *args, **kw):
        kw.setdefault('do_scale', False)
        kw.setdefault('do_translation', False)
        kw.setdefault('do_rotation', False)
        kw.setdefault('size_hint', (None, None))
        super(ToolBar, self).__init__(*args, **kw)
        self.size = (Window.width, self.get_real_height())
        self.on_resize(Window.width, Window.height)
        self.set_background()
        self.set_layout()
        
    def disable(self):
        self.button_menu.disabled = True
        self.button_play.disabled = True
    
    def set_layout(self):
        
        #anchor_left = AnchorLayout(anchor_x='left', anchor_y='bottom')
        boxlayout1 = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(Window.width, '%sdp' % self._height)) #, size=('350dp', 0))
        button_menu = Button(size_hint=(None, None), size=('127dp', '51dp'), border=(0, 0, 0, 0), 
                             background_normal='resources/interface/menu.png',
                             background_down='resources/interface/menu-pressed.png',
                             background_disabled_normal='resources/interface/menu.png',
                             background_color=(1, 1, 1, 1),
                             on_release=self.go_to_menu
                             )
        self.button_menu = button_menu
        #button_save = Button(size_hint=(None, None), size=('132dp', '57dp'), border=(0, 0, 0, 0),
        #                     background_normal='resources/interface/save.png',
        #                     background_down='resources/interface/save-pressed.png',
        #                     background_color=(1, 1, 1, 1))
        button_play = Button(size_hint=(None, None), size=('68dp', '51dp'), border=(0, 0, 0, 0),
                             background_normal='resources/interface/pause.png',
                             background_down='resources/interface/pause-pressed.png',
                             background_disabled_normal='resources/interface/pause.png',
                             on_release=GameContext.game.pause,
                             background_color=(1, 1, 1, 1))
        boxlayout1.add_widget(button_menu)
        #boxlayout1.add_widget(button_save)
        boxlayout1.add_widget(button_play)
        
        self.button_play = button_play
        self.button_play.set_paused = self.set_paused
        self.button_play.set_resumed = self.set_resumed
        
        #anchor_left.add_widget(boxlayout1)
        
        anchor_center = AnchorLayout(anchor_x='center', anchor_y="bottom", size_hint=(1, 1))
        #size=(Window.width, '%sdp' % self._height))
        steps = Label(text="STEPS:0", font_size="31dp", font_name=FONT_NAME) #, font_name="resources/Intro.ttf")
        self.steps = steps
        anchor_center.add_widget(steps)
        
        boxlayout1.add_widget(anchor_center)
        
        #anchor_right = AnchorLayout(anchor_x='right', anchor_y="bottom", size_hint=(None, None),
        #                             size=(Window.width, '%sdp' % self._height))
        boxlayout2 = BoxLayout(orientation='horizontal', size_hint=(None, 1), size=('120dp', 0))
        button_trees = Button(size_hint=(None, None), size=('68dp', '57dp'), border=(0, 0, 0, 0),
                             background_normal='resources/interface/trees.png',
                             background_down='resources/interface/trees.png',
                             background_disabled_normal='resources/interface/trees_press.png',
                             background_color=(1, 1, 1, 1),
                             on_release=GameContext.game.switch_to_plant_tree
                             )
        number_of_trees = Label(text='x5', font_size="31dp", font_name=FONT_NAME)
        boxlayout2.add_widget(button_trees)
        boxlayout2.add_widget(number_of_trees)
        
        self.button_trees = button_trees
        self.number_of_trees = number_of_trees
        
        boxlayout1.add_widget(boxlayout2)
        self.add_widget(boxlayout1)
        #self.add_widget(anchor_right)
    
    def go_to_menu(self,btn):
        GameContext.game.pause(self.button_play)
        def _yes_callback():
            _cb = GameContext.app.back_to_menu
            GameContext.app.fade_to_black(_cb)
        msg = MsgBox(text="You are about to go to main menu.\nAre you sure?",
                     font_size='34dp', type='question', size_hint=(0.9, 0.8),
                     buttons_padding='40dp',
                     no_callback=lambda: GameContext.game.resume(self.button_play),
                     yes_callback=_yes_callback
                     )
        msg.open()
        
        
    def set_paused(self):
        self.button_play.background_normal='resources/interface/resume.png'
        self.button_play.background_down='resources/interface/resume-pressed.png'
        
    def set_resumed(self):
        self.button_play.background_normal='resources/interface/pause.png'
        self.button_play.background_down='resources/interface/pause-pressed.png'
    
    def set_background(self):
        texture = GameContext.resources['textures']['toolbar_bg']
        th, tw = texture.size
        th, tw = dp(th), dp(tw)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            for i in xrange(50):
                Rectangle(pos=(i*tw, 0) , size=(tw, th), texture=texture)
    
    def get_real_height(self):
        return dp(self._height)
    
    def on_resize(self, width, height):
        height_in_pixels = Window.height - dp(self._height)
        self.size = (Window.width, self.get_real_height())
        self.pos = (0, height_in_pixels)
        
    def collide_point(self, x, y):
        if y > Window.height - dp(self._height):
            return True
        else:
            return False


class UI(Widget):
    
    def __init__(self, *args, **kw):
        super(UI, self).__init__(*args, **kw)
        if GameContext.ui:
            raise Exception('Creating more than one UI object is not avaliable')
        GameContext.ui = self
        self.greeting_msg = None
        self.context = GameContext
        
        self.toolbar = ToolBar()
        
        
        self.add_widget(self.toolbar)
        
    def resize(self, w, h):
        self.toolbar.on_resize(w, h)

    def update_time(self):
        left_seconds = self.timer.get_left_time()
        if left_seconds <= 0:
            self.context.game.game_over()
        self.clock.text = self.timer.get_formated_time()
        
        
    def greeting(self):

        def _greeting(dt):
            
            anchor = AnchorLayout(anchor_x='center', anchor_y='center', size=(Window.width, Window.height))
            label = Label(text='TAP TO START', font_size='50dp', bold=True, font_name=FONT_NAME)
            anchor.add_widget(label)
            anchor.bind(on_touch_up=self.close_greeting)
            self.greeting_msg = anchor
            self.add_widget(self.greeting_msg)
            
            #label.bind(size=label.setter('text_size'))
            
        Clock.schedule_once(_greeting, -1)
    
    def close_greeting(self, inst, touch):
        if self.greeting_msg:
            self.remove_widget(self.greeting_msg)
            self.greeting_msg = None
        if self.context.game:
            self.context.game.start()
        
            
    def game_over(self, win, text=None):
        
        if not text:
            if win:
                text = "You win!"
            else:
                text = "You lose! Time is over!"
        
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=text))
        content.add_widget(Button(text="Close",
                                  on_press=sys.exit,
                                  size_hint=(None, None),
                                  size=(375, 50)))
        popup = Popup(title='Game is over',
                      content=content,
                      size=(400, 400),
                      size_hint=(None, None),
                      auto_dismiss=False)
        popup.open()


class MenuItem(Label):
    
    release = ObjectProperty(None)
    
    def __init__(self, *args, **kw):
        kw.setdefault('font_size', 30)
        kw.setdefault('font_name', 'resources/Intro.ttf')
        kw.setdefault('size_hint', (None, None))
        kw.setdefault('size', (300, 45))
        kw.setdefault('bold', True)
        super(MenuItem, self).__init__(*args, **kw)
    
    def on_touch_down(self, touch):
        super(MenuItem, self).on_touch_down(touch)
        if self.collide_point(touch.x, touch.y):
            self.color = 1, 1, 0, 1
        
    def on_touch_up(self, touch):
        super(MenuItem, self).on_touch_up(touch)
        self.color = 1, 1, 1, 1 # restore color
        
        if self.collide_point(touch.x, touch.y) and self.release:
            self.release()
            
            
def grass_background(widget):
    bg_texture = Image('resources/grass/grass-texture.png', nocache=True).texture
    # get POT texture
    #bg_texture = bg_texture.get_region(0, 0, 64, 64)
    #bg_texture.uvpos = (0, 0)
    bg_texture.uvsize = (35, 35)
    bg_texture.wrap = 'repeat'
    # fill all the background
    with widget.canvas.before:
        Rectangle(pos=(0, 0), size=(2560, 2560), texture=bg_texture)


class Menu(Widget):
    
    def __init__(self, *args, **kw):
        kw.setdefault('size', (Window.width, Window.height))
        super(Menu, self).__init__(*args, **kw)
        GameContext.menu = self
        grass_background(self)
        self.scale_content()
        
    def scale_content(self):
        scale = Window.height/float(self.content.size[1])
        self.content.scale = scale
        self.content.center = Window.width / 2, Window.height / 2
                    
    def resize(self, *largs):
        self.size = Window.width, Window.height
        #self.content.size = Window.width, Window.height
        self.scale_content()
        
    def start(self):
        """ Starts new game """
        game_start = GameContext.app.start_game
        GameContext.app.fade_to_black(game_start)
        
    def exit(self):
        """ Exits from the application """
        GameContext.app.stop()


class LoaderAnimation(Widget):
    pass


class Loader(Widget):

    def __init__(self, *args, **kw):
        kw.setdefault('size', (Window.width, Window.height))
        super(Loader, self).__init__(*args, **kw)
        grass_background(self)
        self.loader_pictures = ['resources/loader/loader-0{}.png'.format(i) for i in xrange(1, 9)]
        self.percents = 0
    
    def complete_callback(self, dt):
        GameContext.app.switch_to_scene()
        
    def set_progress(self, percents):
        self.percents = percents
        print percents
        loader_pic_index = percents / 13
        print percents, loader_pic_index
        self.loader_animation.canvas.children[0].source = self.loader_pictures[loader_pic_index]
        
        self.percent_label.text = "%s%%" % percents
        
        if percents == 100:
            Clock.schedule_once(self.complete_callback, 0.2)



class BasePicture(Widget):
    
    IMG_PATH = ''
    
    def __init__(self, *args, **kw):
        kw.setdefault('size', (Window.width, Window.height))
        super(BasePicture, self).__init__(*args, **kw)
        self.picture = Image(self.IMG_PATH).texture
        grass_background(self)
        scatter = ScatterPlane(size=self.picture.size,
                               do_translation=False, do_rotation=False, do_scale=False)
        with scatter.canvas:
            Rectangle(size=scatter.size, texture=self.picture)
        scale = Window.height/float(self.picture.size[1])
        scatter.scale = scale
        self.picture_holder = scatter 
        self.add_widget(scatter)
        self.picture_holder.center = Window.center
        
    
    def on_touch_up(self, touch):
        cb = GameContext.app.back_to_menu
        GameContext.app.fade_to_black(cb)
    
    def resize(self, w, h):
        self.size = Window.width, Window.height
        scale = Window.height/float(self.picture.size[1])
        self.picture_holder.scale = scale
        self.picture_holder.center = Window.center


class LosePicture(BasePicture):
    
    IMG_PATH = 'resources/sunny--games--rabbit--game-over.png'


class WinPicture(BasePicture):
    
    IMG_PATH = 'resources/sunny--games--rabbit--win.png'
        