#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import cmd

class DummyClient(object):
    def init(self):
        pass

    def stop(self):
        pass

class AdventureScript(cmd.Cmd):
    __client = None
    prompt = 'AdventureScript: '

    def attach(self, client):
        self.__client = client

    @property
    def attached(self):
        return self.__client is not None
    
    def emptyline(self):
        return

    def parseline(self, line):
        if line.strip().startswith('#'):
            line = ''
        return cmd.Cmd.parseline(self, line)

    def preloop(self):
        if self.attached:
            self.__client.init()

    def postloop(self):
        if self.attached:
            self.__client.stop()
        print
    
    def do_client(self, line):
        if not self.attached:
            return
        print line
        
    def do_EOF(self, line):
        return True
    
if __name__ == '__main__':
    shell = AdventureScript()
    shell.attach(DummyClient())
    shell.cmdloop()
