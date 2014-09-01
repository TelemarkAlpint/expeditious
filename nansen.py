#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version_info__ = (0, 1, 0)
__version__ = '.'.join(str(part) for part in __version_info__)
__license__ = 'MIT'

from datetime import datetime
from shutil import copy2
from os import path
import requests
import shutil
import subprocess
import tempfile
import json
import sys
import os


def main():
    """ CLI entrypoint. """
    temp_dir = tempfile.mkdtemp()
    print('temp_dir is %s' % temp_dir)
    silence_file = generate_silence_file(temp_dir)
    urls = get_song_urls()
    files = fetch_songs(temp_dir, urls)
    wav = merge_files(files, silence_file)
    mp3 = convert_to_mp3(wav)
    write_metadata(mp3, urls)
    os.remove(wav)
    print('Fullført. Den ferdige fila ligger her: %s' % mp3)
    shutil.rmtree(temp_dir)


def generate_silence_file(temp_dir):
    print('Creating silence file...')
    filename = os.path.join(temp_dir, 'silence.wav')
    subprocess.check_call(['sox', '-n', '-r', '44100', '-c', '2', filename, 'trim', '0.0', '15.0'])
    print('Silence created.')
    return filename


def fetch_songs(temp_dir, song_urls):
    files = []
    for song_num, song_url in enumerate(song_urls, 1):
        target_file = os.path.join(temp_dir, str(song_num) + '.ogg')
        with open(target_file, 'w') as fh:
            print('Downloading song %s' % song_url)
            response = requests.get(song_url, stream=True)
            if not response.ok:
                print 'Fetching song failed: %s' % song_url
                sys.exit(1)
            for block in response.iter_content(1024):
                if not block:
                    break
                fh.write(block)
            files.append(target_file)
    return files


def get_song_urls():
    print('Henter sanger...')
    song_list = requests.get('http://ntnuita.no/musikk/top/list/').json()
    url_list = [song['filename'] + '.ogg' for song in song_list]
    print('%d sanger funnet.' % len(url_list))
    return url_list


def merge_files(files, silence_file):
    print('Slår sammen filer...')
    target = get_new_filename()
    command = ['sox']
    for song_file in files:
        if sys.version_info > (3, 0, 0):
            command.append(song_file)
        else:
            # Python2, wtf?
            command.append(song_file.encode('latin-1'))
        command.append(silence_file)
    command.append(target)
    command.append('--show-progress')
    try:
        subprocess.check_call(command)
    except Exception:
        print('Klarte ikke slå sammen filer. Kommando: %s' % command)
        sys.exit(1)
    return target


def convert_to_mp3(source):
    dest = path.splitext(source)[0] + '.mp3'
    subprocess.check_call(['lame', '-V2', '--vbr-new', '--tt', 'Mandagstrening', '--ta',
        'NTNUI Telemark-Alpint', '--ty', str(datetime.now().year), '--tc',
        'Generert %s' % datetime.now().strftime('%Y-%m-&d %H:%M'), '--tl', 'Best of I-bygget',
        source, dest])
    return dest


def get_new_filename():
    todays_date = datetime.now().strftime('%Y.%m.%d')
    return '%s.wav' % todays_date


def write_metadata(filename, urls):
    song_meta_filename = path.splitext(filename)[0] + '.json'
    creation_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    # The file used to recreate the file, or see songs it contains
    song_meta = {
        'created': creation_time,
        'filename': filename,
        'songs': [{'filename': path.splitext(url)[0]} for url in urls],
    }
    # The file used by the web site to find the latest song and update time
    top_meta = {
        'last_updated': creation_time,
        'filename': filename,
    }
    with open(song_meta_filename, 'w') as song_meta_fh:
        json.dump(song_meta, song_meta_fh, indent=2)
    with open('top_meta.json', 'w') as top_meta_fh:
        json.dump(top_meta, top_meta_fh, indent=2)
