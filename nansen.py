#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'MIT'

try:
    from urllib2 import urlopen
except ImportError:
    #Python3
    from urllib.request import urlopen

from contextlib import closing
from datetime import datetime
from logging import getLogger
from shutil import copy2
from os import path
import logging.config
import subprocess
import json
import yaml
import sys
import os

config = None
logger = getLogger('expeditious.nansen')

def init():
    _setup_logging()
    _load_config()

def _setup_logging():
    with open('log_conf.yaml') as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))

def _load_config():
    global config
    with open('config.yaml') as config_file:
        config = yaml.load(config_file)

def run():
    logger.info('Starter Nansen v-%s.', __version__)
    files = get_filenames()
    mp3 = merge_files(files)
    copy2(mp3, config['music_src_dir'])
    logger.info('Fullført. Den ferdige fila ligger her: %s', mp3)
    write_metadata(mp3, files)

def get_filenames():
    logger.info('Henter sanger...')
    with closing(urlopen(config['song_data_url'])) as json_data:
        song_list = json.loads(json_data.read().decode('utf-8'))
    path_list = [config['music_src_dir'] + song['filename'] + '.mp3' for song in song_list]
    logger.info('%d sanger funnet.', len(path_list))
    return path_list

def merge_files(files):
    logger.info('Slår sammen filer...')
    target = get_new_filename()
    command = ['sox']
    for song_file in files:
        if sys.version_info > (3, 0, 0):
            command.append(song_file)
        else:
            # Python2, wtf?
            command.append(song_file.encode('latin-1'))
        command.append(config['silence_file'])
    command.append(target)
    command.append('--show-progress')
    try:
        subprocess.check_call(command)
    except Exception:
        logger.exception('Klarte ikke slå sammen filer. Kommando: %s', command)
        sys.exit(1)
    return target

def get_new_filename():
    datestr = datetime.now().strftime('%Y.%m.%d')
    suffix = get_month_name()
    return config['music_dest_dir'] + '%s - %s.mp3' % (datestr, suffix)

def write_metadata(filename, files):
    targets = [
        config['music_src_dir'] + path.split(filename)[1] + '.json',
        config['music_src_dir'] + 'top_meta.json',
        path.splitext(filename)[0] + '.json',
    ]
    metadata = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'filename': os.path.split(filename)[1],
        'songs': [path.split(song)[1] for song in files],
    }
    for target in targets:
        with open(target, 'w') as json_file:
            json.dump(metadata, json_file, indent=2)

def get_month_name():
    months = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober',
              'november', 'desember']
    return months[datetime.now().month - 1]

if __name__ == '__main__':
    init()
    run()
