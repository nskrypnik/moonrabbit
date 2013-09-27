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
        viewport = Viewport(width=width, height=height)
        game = MoonRabbitGame()
        viewport.add_widget(game)
        Clock.schedule_once(viewport.fit_to_window, -1)
        return viewport


if __name__ == '__main__':
    MoonRabbitApp().run()