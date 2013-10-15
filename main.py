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
from viewport import Viewport
from game import MoonRabbitGame
from gamecontext import GameContext
from ui import UI, Menu, Loader
from settings import BLOCK_SIZE, GAME_AREA_SIZE


class MoonRabbitApp(App):
    
    def __init__(self, *args, **kw):
        super(MoonRabbitApp, self).__init__(*args, **kw)
        self.context = GameContext 
        self.context.app = self

    def build(self):
        
        root = Widget()
        menu = Menu()
        root.add_widget(menu)
        self.context.menu = menu
        Window.bind(on_resize=self.resize)
        self.root = root
        return root
    
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
        def _launch_game_round(dt):
            width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
            height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
            game_scene = Viewport(width=width, height=height)
            game = MoonRabbitGame()
            game_scene.add_widget(game)
            self.context.scene = game_scene
            Clock.schedule_once(game_scene.fit_to_window, -1)
            
        Clock.schedule_once(_launch_game_round, 0.5)

    def on_pause(self):
        return True


if __name__ == '__main__':
    MoonRabbitApp().run()