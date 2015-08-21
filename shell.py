#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
import cmd
import logging
logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning

class DummyUI(object):
    def init(self):
        _INF('UI: init()')

    def kill(self):
        _INF('UI: kill()')

    def run(self, line):
        _INF('UI: run(%s)' % line)

    def help(self):
        _INF('UI: help()')


class AdventureScript(cmd.Cmd):
    __ui = None
    prompt = 'AdventureScript: '
    child_mode = False

    def attach(self, user_interface):
        self.__ui = user_interface

    @property
    def attached(self):
        return self.__ui is not None
    
    def emptyline(self):
        return

    def parseline(self, line):
        line = line.strip()
        if line.startswith('#'):
            line = ''
        return cmd.Cmd.parseline(self, line)

    def preloop(self):
        if self.attached and not self.child_mode:
            self.__ui.init()

    def postloop(self):
        if self.attached and not self.child_mode:
            self.__ui.kill()
        print
    
    def do_uicfg(self, line):
        "User Interface handling"
        if not self.attached:
            _WRN('UI not attached, ingnoring: "%s"' % line)
            return
        if line == '':
            self.__ui.cfg_help()
            return
        self.__ui.cfg(line)

    def help_uicfg(self):
        self.__ui.cfg_help()
        
    def do_play_music(self, line):
        "Play background music"
        self.__ui.play_bgm(line)

    def do_stop_music(self, line):
        "Stop background music"
        self.__ui.stop_bgm()

    def do_show_image(self, line):
        "Show image in screen"
        self.__ui.show_image(line)

    def do_show_black(self, line):
        "Clear screen to black color"
        self.__ui.show_black()

    def do_goto_sleep(self, line):
        "Clear screen to black color and stop music"
        self.__ui.show_black(fade_audio=True)

    def do_text_area(self, line):
        if ',' in line:
            parameters = line.split(',')
        else:
            parameters = line.split()
        if len(parameters) not in [2, 3]:
            self.help_text_area()
            return
        try:
            x = int(parameters[0])
            y = int(parameters[1])
            h = None
            if len(parameters) == 3:
                h = int(parameters[2])
        except:
            self.help_text_area()
            return
        self.__ui.set_text_area((x, y), h)
        
    def help_text_area(self):
        print 'Define text area on the screen: text_area X,Y[,HEIGHT]'
        print 'Width is auto selected. If HEIGHT is omited, area is'
        print 'created from (x,y) to the bottom of the screen.'
        print 'All values must be integers.'

    def do_say(self, line):
        "Send text to TextArea"
        self.__ui.say(line + '\n')

    def do_waste(self, line):
        "Waste time in msecs"
        try:
            stime = float(line)
        except:
            _WRN('Time "%s" is not a float' % line)
            return
        self.__ui.waste(stime)

    def do_include(self, line):
        "Include another adsc file"
        fd = open(line, 'rt')
        child_shell = AdventureScript(stdin=fd)
        child_shell.use_rawinput = False
        child_shell.child_mode = True
        child_shell.attach(self.__ui)
        child_shell.cmdloop()
        
    def do_exit(self, line):
        "Exit"
        return True

    def do_quit(self, line):
        "Exit"
        return True
    
    def do_EOF(self, line):
        "Exit"
        return True
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    import sdlui

    if len(sys.argv) > 1:
        _INF('Loading "%s"...' % sys.argv[1])
        fd = open(sys.argv[1], 'rt')
        shell = AdventureScript(stdin=fd)
        shell.use_rawinput = False
    else:
        fd = None
        shell = AdventureScript()
    shell.attach(sdlui.UI())
    shell.cmdloop()

    if fd is not None:
        fd.close()
