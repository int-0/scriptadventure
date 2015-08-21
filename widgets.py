#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import pygame

def factory(widget_def):
    widget_class = widget_def.get('type', None)
    if not widget_class:
        return DummyWidget()

    if widget_class == 'Box':
        pos = tuple(widget_def.get('position', [0, 0]))
        size = tuple(widget_def.get('size', [0, 0]))
        color = pygame.Color(*tuple(
            widget_def.get('color', [255, 255, 255, 255])))
        return Box(pos, size, color)
    elif widget_class == 'TextArea':
        pass
    else:
        return DummyWidget()

    
class DummyWidget(object):
    def __init__(self, position=(0, 0)):
        self.__scr = pygame.Surface((1, 1)).convert_alpha()
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        self.__position = position

    @property
    def ready(self):
        return True

    @property
    def surface(self):
        return self.__scr

    @property
    def position(self):
        return self.__position

    def update(self):
        pass
    

class Box(object):
    def __init__(self, position, size,
                 color=pygame.Color(255,255,255,255)):
        self.__scr = pygame.Surface(size).convert_alpha()
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        self.__color = color
        self.__pos = position
        self.__size = size
        self.__ready = False
        self.update = self.__opening

        self.__current_pos = (self.__pos[0] + self.__size[0] / 2,
                              self.__pos[1] + self.__size[1] / 2)
        self.__current_size = (0, 0)
        
    @property
    def ready(self):
        return self.__ready

    @property
    def surface(self):
        return self.__scr

    @property
    def position(self):
        return self.__pos

    def __opening(self):
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        current_pos_x, current_pos_y = self.__current_pos
        if current_pos_x > self.__pos[0]:
            current_pos_x -= 1
        if current_pos_y > self.__pos[1]:
            current_pos_y -= 1
        self.__current_pos = (current_pos_x, current_pos_y)
        current_size_x, current_size_y = self.__current_size
        if current_size_x < self.__size[0]:
            current_size_x += 1
        if current_size_y < self.__size[1]:
            current_size_y += 1
        self.__current_size = (current_size_x, current_size_y)
        pygame.draw.rect(self.__scr, self.__color,
                         pygame.Rect(self.__current_pos,
                                     self.__current_size), 2)
        if ((self.__current_size == self.__size) and
            (self.__current_pos == self.__pos)):
            self.update = self.__normal
            self.__ready = True
    
    def __normal(self):
        pass
        
    
class TextArea(object):
    def __init__(self, size, font,
                 color=pygame.Color(255, 255, 255, 255)):
        self.__scr = pygame.Surface(size).convert_alpha()
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        
        self.__font = font
        self.__color = color

        self.__space = self.__font.metrics(' ')[0][4]
        self.__interline = (self.__font.get_ascent() +
                            self.__font.get_descent() + 4)
        self.__ofs = (0, 0)
        self.__text = []
        self.__word = ''

        self.__wait_more = True
        self.__first_word = True

    @property
    def wait_more(self):
        return self.__wait_more

    @property
    def surface(self):
        return self.__scr

    def __cr(self):
        self.__ofs = (0, self.__ofs[1] + self.__interline)
        if ((self.__ofs[1] + self.__interline) >
            self.__scr.get_size()[1]):
            self.__scroll_up()
        self.__first_word = True

    def __fit(self, word):
        size = self.__font.size(word)
        return (self.__ofs[0] + size[0]) <= self.__scr.get_size()[0]
    
    def __scroll_up(self):
        rect = pygame.Rect(
            (0, self.__interline),
            (self.__scr.get_size()[0],
             self.__scr.get_size()[1] - self.__interline))
        old = self.__scr.subsurface(rect).copy()
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        self.__scr.blit(old, (0, 0))
        self.__ofs = (self.__ofs[0], self.__ofs[1] - self.__interline)
        
    def __next_word(self):
        if len(self.__text) == 0:
            self.__wait_more = True
            return
        self.__wait_more = False
        
        word = self.__text[0]
        self.__text = self.__text[1:]

        if word.startswith('*') and word.endswith('*'):
            word = word[1:-1]
            self.__font.set_bold(True)
        elif word.startswith('/') and word.endswith('/'):
            word = word[1:-1]
            self.__font.set_italic(True)
        else:
            self.__font.set_italic(False)
            self.__font.set_bold(False)

        if self.__first_word:
            self.__first_word = False
        else:
            self.__ofs = (self.__ofs[0] + self.__space, self.__ofs[1])
        self.__word = word

        # Check if next 
        if self.__word == '':
            self.__next_word()

        if not self.__fit(self.__word):
            self.__cr()
            
    def show_text(self, text):
        for word in text.split(' '):
            self.__text.append(word)
        self.__wait_more = False

    def clear(self):
        self.__ofs = (0, 0)
        self.__scr.fill(pygame.Color(0, 0, 0, 0))
        self.__first_word = True
        
    def flush(self):
        while not self.__wait_more:
            self.update()
            
    def update(self):
        if len(self.__word) == 0:
            self.__next_word()

        if self.__wait_more:
            return

        next_char = self.__word[0]
        self.__word = self.__word[1:]

        if next_char == '\n':
            self.__cr()
            return
        
        next_char = self.__font.render(next_char, True, self.__color)
        self.__scr.blit(next_char, self.__ofs)
        self.__ofs = (self.__ofs[0] + next_char.get_size()[0],
                      self.__ofs[1])
