#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'GPL'

from contextlib import closing
from datetime import datetime
from logging import getLogger
from urllib2 import urlopen
from mutagen import File
from shutil import copy2
from os import path
import logging.config
import subprocess
import json
import yaml
import sys
import os

config = None
logger = None

def init():
    _setup_logging()
    _load_config()

def _setup_logging():
    global logger
    with open('log_conf.yaml') as log_conf:
        config = yaml.load(log_conf)
    logging.config.dictConfig(config)
    logger = getLogger('amundsen')

def _load_config():
    global config
    with open('config.yaml') as config_file:
        config = yaml.load(config_file)
    logger.debug('Config: %s', config)

def run():
    logger.info('Starter Amundsen v. %s.', __version__)
    src_file = get_src_file()
    logger.info('Source file: %s', src_file)
    wav_file = to_wav(src_file)
    logger.info('As wave: %s', wav_file)
    load_metadata_to_config(src_file)
    converted_files = convert_file(wav_file)
    logger.info('Files converted: %s', '\n'.join(converted_files))
    os.remove(wav_file)
    filename = os.path.splitext(os.sep.join(converted_files[0].split(os.sep)[-2:]))[0]
    logger.info('Filename: \n%s', filename)
    set_clipboard_if_possible(filename)

def load_metadata_to_config(src_file):
    artist = get_artist(src_file)
    title = get_title(src_file)
    metadata = {'title': title, 'artist': artist}
    config['metadata'] = metadata

def copy(src_files, dest):
    for src_file in src_files:
        copy2(src_file, dest)

def to_wav(src_file):
    new_filename = path.splitext(src_file)[0] + '.wav'
    command = ['sox', src_file, new_filename]
    logger.info('Command: %s', command)
    subprocess.check_call(command)
    return new_filename

def get_src_file():
    if len(sys.argv) == 2:
        src = sys.argv[1]
    else:
        src = raw_input('Enter the path to the src file: ')
        src = src.strip('"')
    return src

def convert_file(src):
    formats = config['formats']
    metadata = config['metadata']
    artist = metadata['artist']
    filename = path.split(src)[1]
    basename = path.splitext(filename)[0]
    target_folder = path.join(config['music_src_dir'], artist)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    converted = []
    for format in formats.values():
        new_filename = '%s%s' % (basename, format['extension'])
        target = path.join(target_folder, new_filename)
        command = [format['application']] + format.get('arguments', []) + [src, target]
        logger.info("Command: %s", command)
        subprocess.check_call(command)
        converted.append(target)
    return converted

def get_artist(song):
    alts = ['artist', 'Artist', 'ARTIST', 'TPE1']
    return _get_property(song, alts)

def get_title(song):
    alts = ['Title', 'title', 'TITLE', 'TIT2']
    return _get_property(song, alts)

def _get_property(song, alts):
    audio = File(song)
    for alt in alts:
        try:
            return audio[alt][0]
        except:
            pass
    return None

def set_clipboard_if_possible(string):
    try:
        from Tkinter import Tk
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(string)
        r.destroy()
        print 'Filename copied to your clipboard.'
    except:
        pass

if __name__ == '__main__':
    init()
    run()