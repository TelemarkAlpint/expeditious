#!/usr/bin/env python
# *-* coding: utf-8 *-*

"""
Monsen is a thin wrapper around sox to help with trimming audio with fade up and fade down.

Supported formats is everything supported by SoX. Trimmed audio will always be FLAC,
regardless of source file. Run `sox` to get a list of all supported formats.

Monsen will also save the trim data (source file, start point and duration), so that you can
redo the trim later with other settings or another source file. The data saved is:

```
_version: The data format version used. Current latest version is 2 (the one you're reading now).
src_file: The input file that was used.
destination: Where the output was stored.
sox_args: The full list of arguments passed to sox.
```

The data file is stored next to the source file, and all paths are relative to the data file.

Monsen will also normalize your audio to -1dB, and fade in and out. (1.5 sec half sine wave).
"""

from __future__ import print_function

__version_info__ = (0, 2, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'MIT'

from argparse import ArgumentParser
from os import path
import logging
import subprocess
import yaml
import sys

# Used to normalize audio based on perceived loudness levels, not peak amplitudes
_rms_target_level = 0.39


def main():
    """ CLI entry point. """
    args = _get_args()
    monsen = Monsen(args.input)
    monsen.trim(start=args.start, duration=args.duration, dst=args.file)
    monsen.save_stats()


def _get_args():
    parser = ArgumentParser(prog='monsen',
        description='Monsen will help you trim audio, with fade up and down and normalizing.')
    parser.add_argument('input', help='The file to trim.')
    parser.add_argument('-s', '--start',
        help='The starting point for the trim. Default: %(default)s',
        type=float,
        default=0.0)
    parser.add_argument('-d', '--duration',
        help='The new duration of the song. Default: %(default)s',
        type=float,
        default=45.0)
    parser.add_argument('-f', '--file',
        help='Trimmed result will be saved in FILE. Defaults to [input]_trimmed.flac')
    args = parser.parse_args()
    return args


class Monsen(object):

    def __init__(self, src_file):
        self.sanity_check_input(src_file)
        self.src_file = src_file
        self.report = {
            '_version': 2,
        }


    def sanity_check_input(self, source):
        try:
            output = subprocess.check_output(['sox', '--i', source])
            for line in output.split('\n'):
                if line.startswith('Sample Rate'):
                    _, rate = line.split(':', 1)
                    rate = int(rate.strip())
                    if rate != 44100:
                        raise Exception('Wrong input sample rate, was %d, expected 44100' % rate)
        except Exception as e:
            print('Input file is not 44,1kHz, or sox failed to read file, please fix!')
            print('Error was: %s' % e)
            sys.exit(1)


    def _run_command(self, command):
        """ Runs a shell command and prints any errors that may have occurred before terminating. """
        print('Running %s...' % command[0])
        try:
            subprocess.check_call(command)
        except Exception:
            logging.exception('Calling %s failed, is it installed on your system? Arguments were %s',
                command[0], ' '.join(command[1:]))
            sys.exit(1)


    def _normalize_audio(self, input_file):
        cmd = ['normalize-audio', '-a', str(_rms_target_level), input_file, '--no-progress']
        self._run_command(cmd)


    def trim(self, start, duration, dst=None):
        dst = dst or path.splitext(self.src_file)[0] + '_trimmed.flac'
        cmd = [
            'sox', self.src_file, dst,
            'trim', str(start), str(duration),
            'gain', '-n', '-1',
            'fade', 'h', '1.5', str(duration),
        ]
        self.normalize_audio(dst)
        self._run_command(cmd)
        print('Trimmed result can be found at %s' % path.relpath(dst))
        self.report['sox_args'] = cmd
        self.report['destination'] = dst
        return dst


    def save_stats(self):
        src_dir = path.dirname(self.src_file)
        self.report['src_file'] = path.basename(self.src_file)
        self.report['destination'] = path.relpath(self.report['destination'], src_dir)
        stats_filename = path.splitext(self.src_file)[0] + '.yaml'
        with open(stats_filename, 'w') as stats_fh:
            yaml.dump(self.report, stats_fh, default_flow_style=False)
        print('Trim data saved to %s' % path.relpath(stats_filename))
