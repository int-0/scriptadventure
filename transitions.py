#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import time
import video

import pygame

_TRANSITIONS_FPS_ = 50

def __center__(dest, source):
    dest_res = dest.get_size()
    src_res = source.get_size()
    ofs_x = dest_res[0] - src_res[0]
    ofs_y = dest_res[1] - src_res[1]
    return (ofs_x / 2, ofs_y / 2)


def cut(first_frame, last_frame, time_wait=0.0, per_frame_cb=None):
    screen = video.Screen()
    first = first_frame.copy()
    last = last_frame.copy()

    screen.show_image(first, __center__(screen, first))
    screen.update()
    time.sleep(time_wait)
    if per_frame_cb is not None:
        per_frame_cb(0, 1)
    screen.show_image(first, __center__(screen, last))
    screen.update()


def fade(first_frame, last_frame, time_wait=0.0, per_frame_cb=None):

    frames = int(time_wait * float(_TRANSITIONS_FPS_)) + 1
    
    clock = pygame.time.Clock()
    
    screen = video.Screen()
    first = first_frame.copy()
    first = first.convert()
    last = last_frame.copy()
    last = last.convert()

    first_pos = __center__(screen, first)
    last_pos = __center__(screen, last)

    screen.show_image(first, first_pos)
    screen.update()

    for x in range(frames):
        clock.tick(_TRANSITIONS_FPS_)
        
        alpha = int((255.0 / float(frames)) * float(x))
        
        first.set_alpha(255 - alpha)
        last.set_alpha(alpha)

        screen.show_image(first, first_pos)
        screen.show_image(last, last_pos)
        screen.update()

        if per_frame_cb is not None:
            per_frame_cb(x, frames)
        
    screen.show_image(last, last_pos)
    screen.update()
