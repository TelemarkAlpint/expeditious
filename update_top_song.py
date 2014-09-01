"""
    This script is run on the studorg fileserver to update the song read by slingsby, which can be
    found at ntnuita.no/musikk/top, use that for finding the newest song.
"""

import datetime
import json
import nansen
import os
import shutil

def main():
    mp3, metadata = nansen.main()
    print('Moving files...')
    move_files(mp3, metadata)
    update_top_meta(mp3)


def move_files(mp3, metadata):
    target_dir = '/home/groupswww/telemark/media/musikk/compilations'
    shutil.move(mp3, target_dir)
    os.chmod(os.path.join(target_dir, mp3), 0664)
    shutil.move(metadata, target_dir)
    os.chmod(os.path.join(target_dir, metadata), 0664)
    update_top_meta(mp3)


def update_top_meta(new_song_name):
    print('Updating top_meta.json...')
    creation_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    top_meta = {
        'last_updated': creation_time,
        'url': 'http://org.ntnu.no/telemark/media/musikk/compilations/' + new_song_name,
    }
    with open('/home/groupswww/telemark/media/musikk/top_meta.json', 'w') as top_meta_fh:
        json.dump(top_meta, top_meta_fh, indent=2)


if __name__ == '__main__':
    main()
