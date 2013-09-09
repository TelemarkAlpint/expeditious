#!/usr/bin/env python
# *-* coding: utf-8 *-*

"""
Monsen will take your audio and trim it according to your arguments.
Supported formats is everything supported by SoX. Trimmed audio will always be FLAC,
regardless of source file.

Monsen will also save the trim data (source file, start point and duration), so that you can
redo the trim later with other settings or another source file.

Monsen will also normalize your audio to -1dB, and fade in and out. (1.5 sec half sine wave).

Once mutagen or similar tools support Python3, monsen should be able to take in a file from
arbitrary locations, and move it to a subfolder in the users music directory. (eg. folders
based on artists).
"""

__version_info__ = (0, 2, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'MIT'

from argparse import ArgumentParser
from logging import getLogger
from os import path
import logging.config
import subprocess
import yaml
import sys

logger = getLogger('expeditious.monsen')

def init():
    _setup_logging()

def _setup_logging():
    conf_location = path.abspath('log_conf.yaml')
    with open(conf_location) as log_conf:
        logging.config.dictConfig(yaml.load(log_conf))

def _get_args():
    parser = ArgumentParser(description='''Monsen will help you trim audio,
        with fading up and down and normalizing.''')
    parser.add_argument('input', help='The file to trim.')
    parser.add_argument('-q', '--quiet', help="Don't print anything but errors to stdout.",
                      action='store_false', default=False)
    parser.add_argument('-f', '--file', help='Trimmed result will be saved in FILE. ' \
        'Defaults to [input]_trimmed.flac')
    parser.add_argument('-s', '--start', help='The starting point for the trim. Default: 0',
                        type=float, default=0.0)
    parser.add_argument('-d', '--duration', help='''The duration of the trim,
                            ie. total length of the new audio. Default: 45''',
                        type=float, default=45.0)
    args = parser.parse_args()
    return args

def run():
    args = _get_args()
    if args.quiet:
        logger.setLevel(logging.ERROR)
    logger.info('Monsen %s running.', __version__)
    src_file = args.input
    start_point = args.start
    duration = args.duration
    destination = trim_song(src_file, start_point, duration)
    _save_stats(src_file, start_point, duration, destination)

def _save_stats(src, start, duration, destination):
    src_dir = path.dirname(src)
    stat_dict = {
        'src_file': path.basename(src),
        'start_point': start,
        'duration': duration,
        'destination': path.relpath(destination, src_dir),
    }
    stats_filename = path.splitext(src)[0] + '.yaml'
    with open(stats_filename, 'w') as stats_file:
        yaml.dump(stat_dict, stats_file, default_flow_style=False)
    logger.info('Trim options saved to %s', path.relpath(stats_filename))

def trim_song(src, start, duration, dst=None):
    dst = dst or path.splitext(src)[0] + '_trimmed.flac'
    cmd = [
        'sox', src, dst,
        'trim', str(start), str(duration),
        'gain', '-n', '-1',
        'fade', 'h', '1.5', str(duration),
    ]
    try:
        subprocess.check_call(cmd)
    except Exception:
        logger.exception('Something failed calling SoX.')
        sys.exit(1)
    logger.info('Trimmed result can be found at %s', path.relpath(dst))
    return dst

if __name__ == '__main__':
    init()
    run()
