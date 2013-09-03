#!/usr/bin/env python


from kivy.app import App
from game import MoonRabbitGame
#from kivy.graphics import Color, Rectangle


class MoonRabbitApp(App):
    def build(self):
        return MoonRabbitGame()


if __name__ == '__main__':
    MoonRabbitApp().run()