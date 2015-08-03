#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import scene

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
        self.__adventure = adventure
        self.__variables = {}
        self.__first_scene = self.__adventure.get('first_scene', None)
        if not self.__first_scene:
            raise InvalidAdventureScript('Missing "first_scene" key!')

        self.__scenes = {}
        self.__scene = None

        # Load all scenes
        for scene_name in self.__adventure.get('scenes', {}).keys():
            self.__scenes[scene_name] = scene.Scene(
                self.__adventure['scenes'].get(scene_name, {}), self)
            if self.__scene is None:
                self.__scene = self.__scenes[scene_name]

        self.__scene_changed = False
        
        # Goto the first
        self.go_to(self.__first_scene)

        
    def go_to(self, scene):
        _DEB('Adventure_go_to(%s)' % scene)
        if scene not in self.__scenes.keys():
            raise SceneNotFound(scene)
        current_frame = self.__scene.current_frame.copy()
        self.__current_scene = scene
        self.__scene = self.__scenes[scene]
        self.__scene.set_previous_frame(current_frame)
        self.__scene_changed = True
        

    def start(self):
        while True:
            self.__scene_changed = False
            self.__scene.run()
            if not self.__scene_changed:
                _DEB('No new scene detected, terminated!')
                return
                    
