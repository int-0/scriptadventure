#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import time
import shlex
import pygame
import logging
import argparse

logger = logging.getLogger(__name__)
_DEB = logger.debug
_INF = logger.info
_WRN = logger.warning

import video
import widgets
import transitions

class NoExitArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            print message
            
    def error(self, message):
        print 'CMDLINE error: %s' % message


class UIError(Exception):
    def __init__(self, msg):
        self.__msg = msg
    def __str__(self):
        return 'UI Error: %s' % self.__msg

class UI(object):
    __parser = None
    __video = None
    __last_frame = None
    __transition = 0.0

    __current_bgm = None

    __font = None
    __text_area = None
    __text_position = None

    __actor_position = {}
    __actor_image = {}
    __actors = []
    
    def __init__(self):
        self.__parser = NoExitArgumentParser(prog='ui', description='User Interface options')
        self.__parser.add_argument('-r', '--resolution', help='Set resolution',
                                   default=None, action='store', dest='resolution')
        self.__parser.add_argument('-c', '--caption', help='Set window caption',
                                   default=None, action='store', dest='caption')
        self.__parser.add_argument('-t', '--transition', help='Set transition time',
                                   type=float, default=-1.0, action='store', dest='transition')
        self.__parser.add_argument('-f', '--font', help='Set font (file/system) with size',
                                   default=None, action='store', dest='font')
        

    def __assert_video_enabled__(self):
        if self.__video is None:
            raise UIError('No video mode active yet!')

    def __assert_font_ready__(self):
        if self.__font is None:
            raise UIError('No font loaded!')

    def __assert_text_ready__(self):
        self.__assert_font_ready__()
        if self.__text_area is None:
            raise UIError('No text area defined!')

    def init(self):
        _DEB('init()')
        pygame.init()

    def kill(self):
        _DEB('quit()')
        pygame.quit()
        
    def cfg(self, line):
        _DEB('run(%s)' % line)
        args = self.__parser.parse_args(shlex.split(line))
        if args.resolution is not None:
            self.__set_mode__(args.resolution)
        if args.caption is not None:
            self.__set_caption__(args.caption)
        if args.transition > 0.0:
            _DEB('Set transition time to %s' % args.transition)
            self.__transition = args.transition
        if args.font is not None:
            self.__load_font__(args.font)
                    
    def cfg_help(self):
        self.__parser.print_help()

    def __set_mode__(self, resolution):
        _DEB('Switch to: %s' % resolution)
        if (('x' not in resolution) and (',' not in resolution)):
            raise UIError('Resolution must be in WIDTHxHEIGTH or WIDTH,HEIGHT format!')
        try:
            if 'x' in resolution:
                x, y = resolution.split('x')
            else:
                x, y = resolution.split(',')
            resolution = (int(x), int(y))
        except:
            raise UIError('Resolution must be two integer values!')
        self.__video = video.Screen(resolution)
        self.__last_frame = video.empty_image()


    def __set_caption__(self, caption):
        _DEB('Set caption: %s' % caption)
        if self.__video is None:
            raise UIError('No window created yet!')
        self.__video.set_caption(caption)

    def __load_font__(self, font):
        _DEB('Load font: %s' % font)
        if ',' not in font:
            raise UIError('Font must be FONT_NAME,SIZE format!')
        try:
            font, size = font.split(',')
            size = int(size)
        except:
            raise UIError('SIZE must be an integer!')
        
        if font in pygame.font.get_fonts():
            _DEB('Load system font')
            self.__font = pygame.font.SysFont(font, size)
        else:
            _DEB('Try to load font')
            self.__font = pygame.font.Font(font, size)
            
    def play_bgm(self, filename):
        _DEB('Start playing: %s' % filename)
        self.__current_bgm = filename
        pygame.mixer.music.stop()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()

    def stop_bgm(self):
        _DEB('Stop playing: %s' % self.__current_bgm)
        self.__current_bgm = None
        pygame.mixer.music.stop()

    def load_image(self, filename):
        _DEB('Load image: %s' % filename)
        return video.load_image(filename)
            
    def show_image(self, filename):
        _DEB('Show image: %s' % filename)
        self.__assert_video_enabled__()
        image = video.load_image(filename)
        self.__show_image__(image)
        
    def show_black(self, fade_audio=False):
        _DEB('Show black')
        self.__assert_video_enabled__()
        self.__show_image__(video.empty_image(), fade_audio)

    def enter_actor(self, filename):
        _DEB('Enter actor: %s' % filename)
        self.__assert_video_enabled__()

        # Move current actors
        new_positions = self.__get_center_points(len(self.__actors) + 1)
        pos_idx = 0
        drawed_actors = []
        for actor in self.__actors:
            actor_width = self.__actor_image[actor].get_width()
            new_pos = (new_positions[pos_idx] - (actor_width / 2),
                       self.__actor_position[actor][1])
            self.__draw_scene(drawed_actors)
            transitions.move(self.__actor_image[actor],
                             self.__actor_position[actor],
                             new_pos,
                             .5)
            drawed_actors.append(actor)
            self.__actor_position[actor] = new_pos
            pos_idx += 1
            
        # Put new actor
        self.__actors.append(filename)
        self.__actor_image[filename] = video.load_image(filename)
        actor_width = self.__actor_image[filename].get_width()
        actor_row = (self.__video.size[1] -
                     self.__actor_image[filename].get_height())
        self.__actor_position[filename] = (
            new_positions[pos_idx] - (actor_width / 2),
            actor_row
        )
        self.__draw_scene(drawed_actors)
        transitions.move(self.__actor_image[filename],
                         (-actor_width, actor_row),
                         self.__actor_position[filename],
                         1.0)

        
    def leave_actor(self, filename):
        _DEB('Leave actor: %s' % filename)
        self.__assert_video_enabled__()
        actor_width = self.__actor_image[filename].get_width()
        self.__actors.remove(filename)      
        self.__draw_scene(self.__actors)
        transitions.move(self.__actor_image[filename],
                         self.__actor_position[filename],
                         (-actor_width, self.__actor_position[filename][1]),
                         1.0)

        # Move remainder actors
        new_positions = self.__get_center_points(len(self.__actors))
        pos_idx = 0
        drawed_actors = []
        for actor in self.__actors:
            actor_width = self.__actor_image[actor].get_width()
            new_pos = (new_positions[pos_idx] - (actor_width / 2),
                       self.__actor_position[actor][1])
            self.__draw_scene(drawed_actors)
            transitions.move(self.__actor_image[actor],
                             self.__actor_position[actor],
                             new_pos,
                             .5)
            self.__actor_position[actor] = new_pos
            drawed_actors.append(actor)
            pos_idx += 1

        del(self.__actor_image[filename])
        del(self.__actor_position[filename])


    def __get_center_points(self, num_actors):
        dist = self.__video.size[0] / (num_actors + 1)
        points = []
        x = 0
        for actor in range(num_actors):
            x += dist
            points.append(x)
        return points
    
    def __dummy_audio(self, current_frame, last_frame):
        pass

    def __fade_audio(self, current_frame, last_frame):
        pygame.mixer.music.set_volume(1.0 - (float(current_frame)/float(last_frame)))
        
    def __show_image__(self, image, fade_audio=False):
        if self.__transition > 0.0:
            transitions.fade(self.__last_frame, image, self.__transition,
                             self.__fade_audio if fade_audio else self.__dummy_audio)
        self.__video.show_image(image)
        self.__video.update()
        self.__last_frame = image
        if fade_audio:
            self.stop_bgm()

    def set_text_area(self, position, height=None):
        _DEB('Set text area: %s, %s' % (repr(position), height))
        self.__assert_video_enabled__()
        self.__assert_font_ready__()
        if height is None:
            height = self.__video.size[1] - position[1]
        width = (self.__video.size[0] - (position[0] * 2))
        
        self.__text_position = position
        self.__text_area = widgets.TextArea((width, height), self.__font)
        
    def say(self, message):
        _DEB('Say: %s' % repr(message))
        self.__assert_text_ready__()
        self.__text_area.show_text(message)
        while not self.__text_area.wait_more:
            self.__text_area.update()
            self.__video.show_image(self.__text_area.surface,
                                    self.__text_position)
            self.__video.update()

    def waste(self, stime):
        _DEB('Waste: %s' % stime)
        time.sleep(stime)

    def __draw_scene(self, show_actors=None):
        if show_actors is None:
            show_actors = self.__actors
        self.__video.show_image(self.__last_frame)
        for actor in show_actors:
            self.__video.show_image(
                self.__actor_image[actor],
                self.__actor_position[actor]
            )
