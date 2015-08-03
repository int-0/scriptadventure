#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#

import time
import video

def __center__(dest, source):
    dest_res = dest.get_size()
    src_res = source.get_size()
    ofs_x = dest_res[0] - src_res[0]
    ofs_y = dest_res[1] - src_res[1]
    return (ofs_x / 2, ofs_y / 2)


def cut(first_frame, last_frame, time_wait=0.0):
    screen = video.Screen()
    first = first_frame.copy()
    last = last_frame.copy()

    screen.show_image(first, __center__(screen, first))
    screen.update()
    time.sleep(time_wait)
    screen.show_image(first, __center__(screen, last))
    screen.update()


def fade(first_frame, last_frame, frame_skip=0):
    frame_increment = frame_skip + 1
    screen = video.Screen()
    first = first_frame.copy()
    first = first.convert()
    last = last_frame.copy()
    last = last.convert()

    first_pos = __center__(screen, first)
    last_pos = __center__(screen, last)

    screen.show_image(first, first_pos)
    screen.update()

    for x in range(255):
        if x % frame_increment:
            continue
        first.set_alpha(255 - x)
        last.set_alpha(x)

        screen.show_image(first, first_pos)
        screen.show_image(last, last_pos)
        screen.update()
        
    screen.show_image(last, last_pos)
    screen.update()
