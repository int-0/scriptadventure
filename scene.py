#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import video
import script
import transitions

import logging
logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning

class Scene(object):
    def __init__(self, scene_config, adventure):
        self.__screen = video.Screen()
        self.__config = scene_config
        self.__adventure = adventure
        
        self.__background = self.__config.get('scenario', None)
        if self.__background is None:
            self.__background = video.empty_image()
        else:
            self.__background = video.load_image(self.__background)
        self.__frame = self.__background.copy()

        self.__intro = self.__config.get('intro', None)
        self.__outtro = self.__config.get('outtro', None)
        
        self.__script = self.__config.get('script', [])
        self.__script.reverse()
        self.__interpreter = script.Interpreter(self)

    def jump_to(self, scene):
        self.__adventure.go_to(scene)
        self.__script = []
        
    @property
    def current_frame(self):
        return self.__frame

    def set_previous_frame(self, image):
        self.__frame = image
    
    def run(self):
        self.presentation()
        result = self.main_loop()
        self.termination()
        return result

    def presentation(self):
        _DEB('Presentation(%s)' % self.__intro)
        if self.__intro is None:
            return

        if self.__intro not in dir(transitions):
            _WRN('Ignore unrecognized transition: %s' % self.__intro)
            return

        getattr(transitions, self.__intro)(self.__frame,
                                           self.__background)
        
    def termination(self):
        _DEB('Termination(%s)' % self.__outtro)
        if self.__outtro is None:
            return

        if self.__outtro not in dir(transitions):
            _WRN('Ignore unrecognized transition: %s' % self.__intro)
            return
                 
        getattr(transitions, self.__outtro)(self.__frame,
                                            video.empty_image())

    def main_loop(self):
        _DEB('Main_loop()')
        self.__screen.show_image(self.__background)
        self.__screen.update()
        self.__frame = self.__background
        while len(self.__script) > 0:
            self.__interpreter.run(self.__script.pop())
