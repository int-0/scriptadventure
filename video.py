#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import uuid
import pygame
import threading

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

        def set_caption(self, caption):
            if caption is None:
                return
            if self.__screen is None:
                return
            pygame.display.set_caption(caption)


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


class VideoLayer(object):
    def __init__(self):
        self.__layer = pygame.Surface(Screen().size).convet_alpha()
        self.clear()
        self.__elements = {}

    @property
    def layer(self):
        return self.__layer
    
    def clear(self):
        self.__layer.fill(pygame.Color(0, 0, 0, 0))

    def add_element(self, element, element_id=None):
        if element_id is None:
            element_id = uuid.uuid4()
        self.__elements[element_id] = element
        return element_id

    def remove_element(self, element_id):
        if element_id not in self.__elements.keys():
            return
        del(self.__elements[element_id])
        
    def draw(self, surface, position):
        self.__layer.blit(surface, position)
    
    def update(self):
        for element in self.__elements.values():
            self.draw(*element.update())
            
class Render(threading.Thread):
    def __init__(self, screen):
        threading.Thread.__init__(self)
        self.__layers = []
        self.__rendering = True
        self.__screen = screen

    def stack_layer(self, layer):
        self.__layers.append(layer)

    def clear(self):
        self.__layers = []

    def stop(self):
        self.__rendering = False

    def run(self):
        while self.__rendering:
            for layer in self.__layers:
                self.__screen.show_image(layer, (0, 0))
            self.__screen.update()


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
