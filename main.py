#!/usr/bin/env python

# hook for windows

import sys
from kivy.config import Config

Config.set('graphics', 'width','1008')
Config.set('graphics', 'height', '720')

from kivy.app import App
from game import MoonRabbitGame
#from kivy.graphics import Color, Rectangle


class MoonRabbitApp(App):
    def build(self):
        return MoonRabbitGame()


if __name__ == '__main__':
    MoonRabbitApp().run()