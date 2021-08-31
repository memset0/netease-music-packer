import os
import sys
import yaml
import shutil
import hashlib
import requests
from os import path


def md5(text, encoding='utf-8'):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode(encoding))
    return md5_hash.hexdigest()


def crawl_playlist(config, id, dist):
    api_root = config['netease_music_api']['root']
    session = requests.session()
    musiclib = os.listdir(config['localdir'])

    # login
    params = {
        'phone': str(config['netease_music_api']['phone']),
        'md5_password': md5(config['netease_music_api']['password']),
    }
    res = session.get(api_root + '/login/cellphone', params=params)

    # playlist
    res = session.get(api_root + '/playlist/detail', params={"id": str(id)})
    playlist = []
    for it in res.json()['playlist']['tracks']:
        playlist.append({
            'name': it['name'],
            'id': it['id'],
            'artist': it['ar'][0]['name']
        })

    # copy local file
    for music in playlist:
        if music['name'] and music['artist']:
            filename = music['artist'] + ' - ' + music['name']
            if (filename + '.mp3') in musiclib:
                shutil.copy(path.join(config['localdir'], filename + '.mp3'),
                            dist)
            elif (filename + '.flac') in musiclib:
                shutil.copy(path.join(config['localdir'], filename + '.flac'),
                            dist)
            else:
                print('music not found:', filename)

    # print('config:', config)
    # print('playlist:', playlist)
    # print('musiclib:', musiclib)


config = yaml.load(open(path.join(sys.path[0], 'config.yml')), yaml.BaseLoader)
# crawl_playlist(config, 6855490486, 'D:\\Temp\\1')
