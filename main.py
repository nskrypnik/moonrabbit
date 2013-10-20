#!/usr/bin/env python

# hook for windows

import sys
from kivy.config import Config

#Config.set('graphics', 'width','1008')
#Config.set('graphics', 'height', '720')

from kivy.app import App
from kivy.clock import Clock 
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.graphics import Rectangle, Color
from viewport import Viewport
from game import MoonRabbitGame
from gamecontext import GameContext
from ui import UI, Menu, Loader, WinPicture, LosePicture 
from settings import BLOCK_SIZE, GAME_AREA_SIZE


class MoonRabbitApp(App):
    
    def __init__(self, *args, **kw):
        super(MoonRabbitApp, self).__init__(*args, **kw)
        self.context = GameContext 
        self.context.app = self
        self.fade_layer = None

    def build(self):
        
        root = Widget()
        menu = Menu()
        root.add_widget(menu)
        self.context.menu = menu
        Window.bind(on_resize=self.resize)
        self.root = root
        return root
    
    def fade_to_black(self, callback, da=0.2):
        
        def _fade_to_black(*largs):
            color, rect = self.fade_layer
            alpha = color.rgba[3]
            alpha += da
            if alpha > 1:
                callback()
                self.root.canvas.after.clear()
                self.fade_layer = None
                return
            # repeat itself
            color.rgba = (0, 0, 0, alpha)
            Clock.schedule_once(_fade_to_black, 0.05)
        
        color = Color(0, 0, 0, 0)
        rect = Rectangle(size=(Window.width, Window.height))
        self.fade_layer = [color, rect]
        self.root.canvas.after.add(color)
        self.root.canvas.after.add(rect)
        _fade_to_black()
        
    def back_to_menu(self):
        if self.context.scene:
            self.root.remove_widget(self.context.scene)
        for child in self.root.children:
            self.root.remove_widget(child)
        self.context.reset()
        menu = Menu()
        self.root.add_widget(menu)
        self.context.menu = menu
        
        
    def finish_round(self):
        game = self.context.game
        if game.win:
            splash = WinPicture()
        else:
            splash = LosePicture()
        self.root.add_widget(splash)
        self.root.remove_widget(self.context.scene)
        # totally remove scene
        self.context.scene = None
        self.context.game = None
    
    def resize(self, inst, w, h):
        """ Some resize extra logic """
        if GameContext.ui:
            GameContext.ui.resize(w, h)
        if GameContext.menu:
            GameContext.menu.resize(w, h)
            
    def switch_to_scene(self):
        self.root.add_widget(self.context.scene)
        self.root.add_widget(UI())
        self.root.remove_widget(self.context.loader)
        self.context.game.start_round()
    
    def start_game(self):
        self.root.remove_widget(self.context.menu)
        loader = Loader()
        self.context.loader = loader
        self.root.add_widget(loader)
        def _launch_game_round(dt=None):
            width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
            height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
            game_scene = Viewport(width=width, height=height)
            game = MoonRabbitGame()
            game_scene.add_widget(game)
            self.context.scene = game_scene
            Clock.schedule_once(game_scene.fit_to_window, -1)
            
        Clock.schedule_once(_launch_game_round, 0.5)
        
        def _emulate_loader(dt=None):
            loader.set_progress(loader.percents + 20)
            if loader.percents != 100:
                Clock.schedule_once(_emulate_loader, 0.1)
        
        _emulate_loader()

    def on_pause(self):
        return True


if __name__ == '__main__':
    MoonRabbitApp().run()