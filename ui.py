
import sys

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
    
    _height = 60
    
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
    
    def set_layout(self):
        
        anchor_left = AnchorLayout(anchor_x='left', anchor_y='bottom')
        boxlayout1 = BoxLayout(orientation='horizontal', size_hint=(None, 1), size=('350dp', 0))
        button_menu = Button(size_hint=(None, None), size=('141dp', '57dp'), border=(0, 0, 0, 0), 
                             background_normal='resources/interface/menu.png',
                             background_down='resources/interface/menu-pressed.png',
                             background_color=(1, 1, 1, 1))
        button_save = Button(size_hint=(None, None), size=('132dp', '57dp'), border=(0, 0, 0, 0),
                             background_normal='resources/interface/save.png',
                             background_down='resources/interface/save-pressed.png',
                             background_color=(1, 1, 1, 1))
        button_play = Button(size_hint=(None, None), size=('75dp', '57dp'), border=(0, 0, 0, 0),
                             background_normal='resources/interface/pause.png',
                             background_down='resources/interface/pause-pressed.png',
                             on_release=GameContext.game.pause,
                             background_color=(1, 1, 1, 1))
        boxlayout1.add_widget(button_menu)
        boxlayout1.add_widget(button_save)
        boxlayout1.add_widget(button_play)
        
        self.button_play = button_play
        self.button_play.set_paused = self.set_paused
        self.button_play.set_resumed = self.set_resumed
        
        anchor_left.add_widget(boxlayout1)
        
        self.add_widget(anchor_left)
        
        anchor_center = AnchorLayout(anchor_x='center', anchor_y="bottom", size_hint=(None, None),
                                     size=(Window.width, '%sdp' % self._height))
        steps = Label(text="STEPS:0", font_size="44dp") #, font_name="resources/Intro.otf")
        self.steps = steps
        anchor_center.add_widget(steps)
        
        self.add_widget(anchor_center)
        
        anchor_right = AnchorLayout(anchor_x='right', anchor_y="bottom", size_hint=(None, None),
                                     size=(Window.width, '%sdp' % self._height))
        boxlayout2 = BoxLayout(orientation='horizontal', size_hint=(None, 1), size=('146dp', 0))
        button_trees = Button(size_hint=(None, None), size=('75dp', '57dp'), border=(0, 0, 0, 0),
                             background_normal='resources/interface/trees.png',
                             background_down='resources/interface/trees.png',
                             background_disabled_normal='resources/interface/trees_press.png',
                             background_color=(1, 1, 1, 1),
                             on_release=GameContext.game.switch_to_plant_tree
                             )
        number_of_trees = Label(text='x5', font_size="44dp")
        boxlayout2.add_widget(button_trees)
        boxlayout2.add_widget(number_of_trees)
        
        self.button_trees = button_trees
        self.number_of_trees = number_of_trees
        
        anchor_right.add_widget(boxlayout2)
        self.add_widget(anchor_right)
        
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
        self.greeting_popup = None
        self.context = GameContext
        
        #self.timer = Timer(self.update_time)
        #self.clock = Label(text=self.timer.get_formated_time(),
        #                   pos=(0, 0),
        #                   font_size = '35dp'
        #)
        #self.add_widget(self.clock)
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
            
            content = BoxLayout(orientation='vertical')
            label = Label(text='Help Rabbit to find the Holly Carrot. You cannot directly control the'\
                          ' Rabbit, but you may move some stones and wood to show the right way for'\
                          ' Holly Carrot. Keep the Rabbit from the White Hare!', valign="middle", halign="center")
            content.add_widget(label)
            content.add_widget(Button(text="Start",
                                      on_press=self.context.game.start,
                                      size_hint=(None, None),
                                      size=(375, 50)))
            popup = Popup(title='Moon Rabbit',
                          content=content,
                          size=(400, 400),
                          size_hint=(None, None),
                          auto_dismiss=False)
            self.greeting_popup = popup
            popup.open()
            label.bind(size=label.setter('text_size'))
            
        Clock.schedule_once(_greeting, -1)
    
    def close_greeting(self):
        if self.greeting_popup:
            self.greeting_popup.dismiss()
            
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
        kw.setdefault('font_size', '45dp')
        kw.setdefault('size_hint', (None, None))
        kw.setdefault('size', ('300dp', '65dp'))
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
    return
    bg_texture = Image('resources/grass/grass-01.png').texture
    w, h = bg_texture.size
    # fill all the background
    with widget.canvas.before:
        for i in range(50):
            for e in range(50):
                Rectangle(pos=(i*w, e*h), size=(w, h), texture=bg_texture)


class Menu(Widget):
    
    def __init__(self, *args, **kw):
        kw.setdefault('size', (Window.width, Window.height))
        super(Menu, self).__init__(*args, **kw)
        GameContext.menu = self
        grass_background(self)
                    
    def resize(self, w, h):
        print w, h
        self.size = w, h
        self.content.size = w, h
        
    def start(self):
        """ Starts new game """
        GameContext.app.start_game()
        
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
    
    def complete_callback(self, dt):
        GameContext.app.switch_to_scene()
        
    def set_progress(self, percents):
        
        loader_pic_index = percents / 13
        print percents, loader_pic_index
        self.loader_animation.canvas.children[0].source = self.loader_pictures[loader_pic_index]
        
        self.percent_label.text = "%s%%" % percents
        
        if percents == 100:
            Clock.schedule_once(self.complete_callback, 0.2)
        

         
        