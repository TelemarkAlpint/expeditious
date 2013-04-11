#!/usr/bin/env python
# *-* coding: utf-8 *-*

"""
Monsen will take your audio and trim it according to your arguments.
Supported formats is everything supported by SoX. Trimmed audio will always be FLAC, regardless of source file.

Monsen will also save the trim data (source file, start point and duration), so that you can redo the trim later with other
settings or another source file.

Monsen will also normalize your audio to -1dB, and fade in and out. (1.5 sec half sine wave).

Once mutagen or similar tools support Python3, monsen should be able to take in a file from arbitrary locations,
and move it to a subfolder in the users music directory. (eg. folders based on artists).
"""

__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'GPL'

from logging import getLogger
from os import path
from shutil import copy2
import logging.config
import subprocess
import yaml
import sys

logger = None
config = None

def init():
    _setup_logging()
    _load_config()
    logger.info('Monsen v. %s running.', __version__)

def _setup_logging():
    global logger
    with open('log_conf.yaml') as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))
    logger = getLogger('monsen')

def _load_config():
    global config
    with open('config.yaml') as config_file:
        config = yaml.load(config_file)

def run():
    src_file = _get_src_file()
    start_point = _get_start_point()
    duration = _get_duration()
    dst_file = trim_song(src_file, start_point, duration)
    _save_stats(src_file, start_point, duration)

def _get_src_file():
    if len(sys.argv) == 2:
        src = sys.argv[1]
    else:
        src = raw_input('Dra en fil hit for å starte.')
        src = src.strip('"')
    return src

def _get_start_point():
    start = raw_input('Angi når sangen skal begynne (i sekunder): ')
    start = start.replace(',', '.')
    return float(start)

def _get_duration():
    duration = raw_input('Hvor lenge skal sangen vare (i sekunder): ')
    duration = duration.replace(',', '.')
    return float(duration)

def _save_stats(src, start, duration):
    stat_dict = {'src_file': src,
                 'start_point': start,
                 'duration': duration,
                 }
    stats_filename = path.splitext(src)[0] + '.yaml'
    with open(stats_filename, 'w') as stats_file:
        yaml.dump(stat_dict, stats_file, default_flow_style=False)
    logger.info('Stats saved to %s', stats_filename)

def trim_song(src, start, duration):
    dst = path.splitext(src)[0] + '_trimmed.flac'
    cmd = ['sox', src, dst,
           'trim', str(start), str(duration),
           'gain', '-n', '-1',
           'fade', 'h', '1.5', str(duration),
           ]
    subprocess.check_call(cmd)
    return dst

if __name__ == '__main__':
    init()
    run()
