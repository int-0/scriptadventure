#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import video
import scene
import layout

import logging
logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning

class InvalidAdventureScript(Exception):
    def __init__(self, msg):
        self.__msg = msg
    def __str__(self):
        return 'Invalid adventure script: %s' % self.__msg

class SceneNotFound(Exception):
    def __init__(self, scene_name):
        self.__scene = scene_name
    def __str__(self):
        return 'Scene "%s" not defined in the script.' % self.__scene


class Adventure(object):
    def __init__(self, adventure):
        self.__render = video.Screen().get_renderer()
        self.__render.start()
        self.__adventure = adventure
        self.__variables = {}
        self.__first_scene = self.__adventure.get('first_scene', None)
        if not self.__first_scene:
            raise InvalidAdventureScript('Missing "first_scene" key!')

        # Load all layouts
        self.__layouts = layout.LayoutLayer()
        for lname in self.__adventure.get('layouts', {}).keys():
            self.__layouts.add_layout(lname,
                                      self.__adventure['layouts'].get(lname,
                                                                      {}))
        # Load all scenes
        self.__scenes = {}
        self.__scene = None
        for scene_name in self.__adventure.get('scenes', {}).keys():
            self.__scenes[scene_name] = scene.Scene(
                self.__adventure['scenes'].get(scene_name, {}), self)
            if self.__scene is None:
                self.__scene = self.__scenes[scene_name]

        self.__scene_changed = False

        # Goto the first
        self.go_to(self.__first_scene)

    @property
    def layouts(self):
        return self.__layouts
    
    def go_to(self, scene):
        _DEB('Adventure_go_to(%s)' % scene)
        if scene not in self.__scenes.keys():
            raise SceneNotFound(scene)
        current_frame = self.__scene.frame.copy()
        self.__current_scene = scene
        self.__scene = self.__scenes[scene]
        self.__scene.set_previous_frame(current_frame)
        self.__scene_changed = True
        self.__render.clear()
        self.__render.stack_layer(self.__scene.frame)
        self.__render.stack_layer(self.__layouts.current.frame)
        
    def shutdown(self):
        self.__layouts.kill()
        self.__render.stop()
        
    def start(self):
        self.__layouts.start()
        while True:
            self.__scene_changed = False
            self.__scene.run()
            if not self.__scene_changed:
                _DEB('No new scene detected, terminated!')
                self.shutdown()
                return
