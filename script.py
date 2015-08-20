#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import time

import logging
logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning

class Interpreter(object):
    def __init__(self, scene):
        self.__scene = scene
        self.__next_scene = None

    @property
    def next_scene(self):
        return self.__next_scene
    
    def run(self, command):
        # Ignore unrecogniced steps
        if not isinstance(command, dict):
            _WRN('Ingnore bad command: %s' % command)
            return

        operation = command.get('operation', 'no_operation')
        operation = 'cmd_%s' % operation
        arguments = tuple(command.get('arguments', []))
        kwarguments = command.get('kwarguments', {})

        # Ignore unknown operations
        if operation not in dir(self):
            _WRN('Ignore unknown command: %s' % operation)
            return

        try:
            return getattr(self, operation)(*arguments, **kwarguments)
        except Exception, e:
            _WRN('Cannot run command "%s": %s' % (operation, e))
            
    def cmd_no_operation(self):
        _DEB('Interpreter: no_operation()')

    def cmd_time_wait(self, duration):
        _DEB('Interpreter: time_wait(%s)' % duration)
        time.sleep(duration)

    def cmd_go_to(self, scene):
        _DEB('Interpreter: go_to(%s)' % scene)
        self.__scene.jump_to(scene)

    def cmd_show_layout(self, layout=None):
        _DEB('Interpreter: show_widgets(%s)' % layout)
        self.__scene.adventure.layouts.show(layout)

    def cmd_hide_layout(self):
        _DEB('Interpreter: hide_layout()')
        self.__scene.adventure.layouts.hide()
