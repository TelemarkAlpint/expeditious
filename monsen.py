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

__version_info__ = (0, 2, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'GPL'

from argparse import ArgumentParser
from logging import getLogger
from shutil import copy2
from os import path
import logging.config
import subprocess
import yaml
import sys

logger = None
args = None

def init():
    _setup_logging()
    _init_parser()

def _setup_logging():
    global logger
    run_dir = path.split(sys.argv[0])[0]
    with open(path.join(run_dir, 'log_conf.yaml')) as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))
    logger = getLogger('monsen')

def _init_parser():
    global args
    parser = ArgumentParser(description='''Monsen will help you trim audio,
        with fading up and down and normalizing.''')
    parser.add_argument('input', help='The file to trim.')
    parser.add_argument('-q', '--quiet', help="Don't print anything but errors to stdout.",
                      action='store_false', default=False)
    parser.add_argument('-v', '--version', help='Display version number and exit.',
                        action='store_true')
    parser.add_argument('-f', '--file', help='Trimmed result will be saved in FILE. Defaults to [input]_trimmed.flac')
    parser.add_argument('-s', '--start', help='The starting point for the trim. Default: 0',
                        type=float, default=0.0)
    parser.add_argument('-d', '--duration', help='''The duration of the trim,
                            ie. total length of the new audio. Default: 45''',
                        type=float, default=45.0)
    args = parser.parse_args()

def run():
    if args.version:
        print('Monsen %s' % __version__)
        sys.exit()
    if args.quiet:
        logger.setLevel(logging.ERROR)
    logger.info('Monsen %s running.' % __version__)
    src_file = args.input
    start_point = args.start
    duration = args.duration
    dst_file = trim_song(src_file, start_point, duration)
    _save_stats(src_file, start_point, duration)

def _save_stats(src, start, duration):
    stat_dict = {'src_file': src,
                 'start_point': start,
                 'duration': duration,
                 }
    stats_filename = path.splitext(src)[0] + '.yaml'
    with open(stats_filename, 'w') as stats_file:
        yaml.dump(stat_dict, stats_file, default_flow_style=False)
    logger.info('Trim options saved to %s', path.relpath(stats_filename))

def trim_song(src, start, duration):
    dst = args.file or path.splitext(src)[0] + '_trimmed.flac'
    cmd = ['sox', src, dst,
           'trim', str(start), str(duration),
           'gain', '-n', '-1',
           'fade', 'h', '1.5', str(duration),
           ]
    try:
        subprocess.check_call(cmd)
        logger.info('Trimmed result can be found at %s', path.relpath(dst))
    except:
        logger.exception('Something failed calling SoX.')
        sys.exit(1)
    return dst

if __name__ == '__main__':
    init()
    run()