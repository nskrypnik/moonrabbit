#!/usr/bin/env python

# hook for windows

import sys
from kivy.config import Config

#Config.set('graphics', 'width','1008')
#Config.set('graphics', 'height', '720')

from kivy.app import App
from kivy.clock import Clock 
from viewport import Viewport
from game import MoonRabbitGame
from settings import BLOCK_SIZE, GAME_AREA_SIZE
        

#from kivy.graphics import Color, Rectangle


class MoonRabbitApp(App):
    def build(self):
        width = BLOCK_SIZE[0]*GAME_AREA_SIZE[0]
        height = BLOCK_SIZE[1]*GAME_AREA_SIZE[1]
        game_scene = Viewport(width=width, height=height)
        game = MoonRabbitGame()
        game_scene.add_widget(game)
        # fir game scene to window
        Clock.schedule_once(game_scene.fit_to_window, -1)
        return game_scene


if __name__ == '__main__':
    MoonRabbitApp().run()