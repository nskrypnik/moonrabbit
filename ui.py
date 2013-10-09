
import sys

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup 
from kivy.uix.button import Button
from kivy.uix.scatter import ScatterPlane
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from kivy.metrics import dp
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
        
    
    def set_background(self):
        texture = GameContext.resources['textures']['toolbar_bg']
        th, tw = texture.size
        th, tw = dp(th), dp(tw)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            for i in xrange(20):
                Rectangle(pos=(i*tw, 0) , size=(tw, th), texture=texture)
    
    def get_real_height(self):
        return dp(self._height)
    
    def on_resize(self, width, height):
        height_in_pixels = Window.height - dp(self._height)
        self.size = (Window.width, self.get_real_height())
        self.pos = (0, height_in_pixels)
        
    def collide_point(self, x, y):
        return False


class UI(Widget):
    
    def __init__(self, *args, **kw):
        super(UI, self).__init__(*args, **kw)
        if GameContext.ui:
            raise Exception('Creating more than one UI object is not avaliable')
        GameContext.ui = self
        self.greeting_popup = None
        self.context = GameContext
        
        self.timer = Timer(self.update_time)
        self.clock = Label(text=self.timer.get_formated_time(),
                           pos=(0, 0),
                           font_size = '35dp'
        )
        self.toolbar = ToolBar()
        
        self.add_widget(self.clock)
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
            label = Label(text='Help Rabbit to find the Moon Stone. You cannot directly control the'\
                          ' Rabbit, but you may move some stones and wood to show the right way for'\
                          ' Moon Stone', valign="middle", halign="center")
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
        