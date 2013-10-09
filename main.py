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
from ui import UI
from settings import BLOCK_SIZE, GAME_AREA_SIZE


class MoonRabbitApp(App):

    def build(self):
        
        root = Widget()
        width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
        height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
        game_scene = Viewport(width=width, height=height)
        game = MoonRabbitGame()
        game_scene.add_widget(game)
        
        root.add_widget(game_scene)
        root.add_widget(UI())
        # fir game scene to window
        game.start_round()
        Clock.schedule_once(game_scene.fit_to_window, -1)
        Window.bind(on_resize=self.resize)
        return root
    
    def resize(self, inst, w, h):
        """ Some resize extra logic """
        if GameContext.ui:
            GameContext.ui.resize(w, h)
    
    def on_pause(self):
        return True


if __name__ == '__main__':
    MoonRabbitApp().run()