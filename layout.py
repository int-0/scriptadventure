#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import video
import widgets

import pygame
import threading
import logging
logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning


class LayoutLayer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.__show = False
        self.__active = True

        self.__layouts = {}
        self.__current = None

    @property
    def current(self):
        return self.__layouts[self.__current]
    
    def add_layout(self, layout_name, layout_config):
        _DEB('Adding layout: %s' % layout_name)
        self.__layouts[layout_name] = Layout(layout_config)
        if self.__current is None:
            self.__current = layout_name

    def show(self, layout_name=None):
        self.__show = True
        if layout_name is None:
            return
        if layout_name not in self.__layouts.keys():
            _WRN('Layout not found: %s (ignored)' % layout_name)
            return
        self.__current = layout_name

    def hide(self):
        self.__show = False

    def update(self):
        if not self.__show:
            return
        self.current.update()

    def kill(self):
        self.__show = False
        self.__active = False

    def run(self):
        while self.__active:
            self.update()


class Layout(object):
    def __init__(self, config={}):
        self.__config = config
        self.__frame = pygame.Surface(
            video.Screen().get_size()).convert_alpha()
        self.__frame.fill(pygame.Color(0, 0, 0, 0))
        self.__widgets = {}
        for widget_name in self.__config.keys():
            self.__widgets[widget_name] = widgets.factory(
                self.__config[widget_name])

        self.__ready = False
        
    @property
    def frame(self):
        return self.__frame
    
    @property
    def ready(self):
        return self.__ready
    
    def update(self):
        self.__frame.fill(pygame.Color(0, 0, 0, 0))
        ready = True
        for widget in self.__widgets.values():
            if not widget.ready:
                ready = False
            widget.update()
            self.__frame.blit(widget.surface, widget.position)
        self.__ready = ready
