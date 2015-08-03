#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import pygame

DEFAULT_RESOLUTION = (1024, 768)

# Created as singleton
#
class Screen(object):
    class __implementation(object):
        def __init__(self, resolution=DEFAULT_RESOLUTION,
                     caption='Script Adventure'):
            # Init pygame if needed
            if not pygame.display.get_init():
                pygame.display.init()
            pygame.display.set_caption(caption)

            self.__resolution = resolution
            self.__screen = pygame.display.set_mode(self.__resolution)
            self.__dirty = []

        @property
        def size(self):
            return self.__resolution

        def get_size(self):
            return self.__resolution

        def show_image(self, image, position=None):
            if position is None:
                position = (((self.size[0] - image.get_width()) / 2),
                            ((self.size[1] - image.get_height()) / 2))
            self.__dirty.append(self.__screen.blit(image, position))

        def update(self):
            pygame.display.update(self.__dirty)
            self.__dirty = []
                    

    __instance = None
    def __init__(self, resolution=None, caption=None):
        if Screen.__instance is None:
            # Create the instance
            Screen.__instance = Screen.__implementation(resolution,
                                                        caption)
        self.__dict__['_Screen__instance'] = Screen.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


def empty_image(size=None):
    if size is None:
        size = Screen().size
    image = pygame.Surface(size)
    image = image.convert_alpha()
    image.fill((0, 0, 0, 255))
    return image


def load_image(filename):
    image = pygame.image.load(filename)
    image = image.convert_alpha()
    return image
