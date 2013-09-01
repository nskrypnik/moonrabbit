#!/usr/bin/env python

import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
#from kivy.graphics import Color, Rectangle

from landscape import Water, Grass, Sand


class MoonRabbitGame(Widget):
    block_width = 25
    block_height = 25
    
    def __init__(self, **kwargs):
        super(MoonRabbitGame, self).__init__(**kwargs)
        self.num_of_blocks_X = Window.width / self.block_height
        self.num_of_blocks_Y = Window.height / self.block_width
        
        # create 2-dimensional array to store blocks
        self.blocks = [[0 for j in xrange(self.num_of_blocks_Y)]
                            for i in xrange(self.num_of_blocks_X)]

        with self.canvas:
            allowed_landscapes = (Water, Grass, Sand)
            for i in xrange(self.num_of_blocks_X):
                for j in xrange(self.num_of_blocks_Y):
                    rand_landscape = allowed_landscapes[random.randint(0, 2)]
                    self.blocks[i][j] = rand_landscape(
                        pos=(i*self.block_width, j*self.block_height),
                        size=(self.block_width, self.block_height)
                    )


class MoonRabbitApp(App):
    def build(self):
        return MoonRabbitGame()


if __name__ == '__main__':
    MoonRabbitApp().run()