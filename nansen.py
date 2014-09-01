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
import pwd
import sys
import os

# Perform sanity check that sox and lame is acessible
current_user = pwd.getpwuid(os.getuid())[0]
sox = 'sox' # Does not need to be compiled locally since it's available on stud
lame = '/home/vagrant/local/bin/lame' if current_user == 'vagrant' else '/home/groups/telemark/local/bin/lame'
try:
    sox_version = subprocess.check_output([sox, '--version'])
    print('Found sox: ' + ' '.join(sox_version.split()[1:]))
except OSError:
    print("Failed to find sox, make sure it's installed and on PATH, and try again")
    sys.exit(1)
try:
    lame_version = subprocess.check_output([lame, '--version'])
    print('Lame found: ' + lame_version.split('\n')[0])
except OSError:
    print("Failed to find lame, tried path '%s', make sure it's there and try again." % lame)
    sys.exit(1)


def main():
    """ CLI entrypoint.

    Returns a tuple of (generated_mp3, mp3_metadata) filenames.
    """
    temp_dir = tempfile.mkdtemp()
    print('temp_dir is %s' % temp_dir)
    silence_file = generate_silence_file(temp_dir)
    urls = get_song_urls()
    files = fetch_songs(temp_dir, urls)
    wav = merge_files(files, silence_file)
    mp3 = convert_to_mp3(wav)
    metadata = write_metadata(mp3, urls)
    print('Done. Completed mp3 is here: %s' % mp3)
    os.remove(wav)
    shutil.rmtree(temp_dir)
    return mp3, metadata


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
    song_data = requests.get('http://ntnuita.no/musikk/top/list/').json()
    song_list = song_data['songs']
    url_list = [song['filename'] + '.ogg' for song in song_list]
    print('%d songs found.' % len(url_list))
    return url_list


def merge_files(files, silence_file):
    print('Merging files...')
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
    subprocess.check_call(command)
    return target


def convert_to_mp3(source):
    print('Converting merged file to mp3...')
    dest = path.splitext(source)[0] + '.mp3'
    subprocess.check_call([lame, '-V2', '--vbr-new', '--tt', 'Mandagstrening', '--ta',
        'NTNUI Telemark-Alpint', '--ty', str(datetime.now().year), '--tc',
        'Generert %s' % datetime.now().strftime('%Y-%m-&d %H:%M'), '--tl', 'Best of I-bygget',
        source, dest])
    return dest


def get_new_filename():
    todays_date = datetime.now().strftime('%Y.%m.%d')
    return '%s.wav' % todays_date


def write_metadata(filename, urls):
    """ Write file used to recreate the file, or see the songs it contains. """
    song_meta_filename = path.splitext(filename)[0] + '.json'
    creation_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    song_meta = {
        'created': creation_time,
        'filename': filename,
        'songs': [{'filename': path.splitext(url)[0]} for url in urls],
    }
    with open(song_meta_filename, 'w') as song_meta_fh:
        json.dump(song_meta, song_meta_fh, indent=2)
    return song_meta_filename


if __name__ == '__main__':
    main()
