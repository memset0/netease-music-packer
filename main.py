import os
import re
import sys
import yaml
import shutil
import hashlib
import requests
import ncmdump
from os import path


def md5(text, encoding='utf-8'):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode(encoding))
    return md5_hash.hexdigest()


def crawl_playlist(config, id, dist):
    api_root = config['netease_music_api']['root']
    session = requests.session()
    musiclib = {}
    for localdir in config['local_dir']:
        for file in os.listdir(localdir):
            musiclib[file] = path.join(localdir, file)
    distlib = os.listdir(dist)

    # login
    params = {
        'phone': str(config['netease_music_api']['phone']),
        'md5_password': md5(config['netease_music_api']['password']),
    }
    res = session.get(api_root + '/login/cellphone', params=params)

    # music
    res = session.get(api_root + '/playlist/detail', params={"id": str(id)})
    json = res.json()
    playlist = []
    playlist_name = json['playlist']['name']
    for it in json['playlist']['tracks']:
        name = it['name']
        artist = ','.join(map(lambda r: str(r['name']), it['ar']))
        if not name or not artist:
            continue
        file = (artist + ' - ' + name).replace('.', '')
        if (file + '.mp3') in distlib:
            playlist.append(file + '.mp3')
        elif (file + '.flac') in distlib:
            playlist.append(file + '.flac')
        elif (file + '.mp3') in musiclib:
            shutil.copy(musiclib[file + '.mp3'], dist)
            playlist.append(file + '.mp3')
        elif (file + '.flac') in musiclib:
            shutil.copy(musiclib[file + '.flac'], dist)
            playlist.append(file + '.flac')
        elif (file + '.ncm') in musiclib:
            print('ncm dump:', file)
            outpath = ncmdump.dump(
                musiclib[file + '.ncm'],
                lambda _, meta: path.join(dist, file + '.' + meta['format']))
            playlist.append(outpath)
        else:
            print('music not found:', file)

    # m3u playlist
    file = open(path.join(
        dist,
        re.sub(r'[\/\\\:\*\?"\<\>\|]', '', playlist_name) + '.m3u'),
                'w+',
                encoding='utf-8')
    file.write('\n'.join(map(lambda n: path.join(dist, n), playlist)))
    file.close()


if __name__ == '__main__':
    config = yaml.load(open(path.join(sys.path[0], 'config.yml')),
                       yaml.BaseLoader)
    for playlist in config['playlist']:
        crawl_playlist(config, playlist, config['dist_dir'])