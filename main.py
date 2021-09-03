import os
import re
import sys
import yaml
import json
import shutil
import hashlib
import requests
import ncmdump
from os import path


def md5(text, encoding='utf-8'):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode(encoding))
    return md5_hash.hexdigest()


def filename_filter(name):
    name = re.sub(r'[\/\\\:\*\?"\<\>\|]', '', name)
    return name


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

    # playlist
    res = session.get(api_root + '/playlist/detail', params={"id": str(id)})
    data = json.loads(res.text)
    playlist = []
    playlist_name = data['playlist']['name']
    print('[PLAYLIST]', playlist_name)

    # music
    for it in data['playlist']['tracks']:
        id = it['id']
        name = it['name']
        if len(it['ar']) > 3:
            it['ar'] = it['ar'][:3]
        artist = ','.join(map(lambda r: str(r['name']), it['ar']))
        if not name or not artist:
            continue
        file = artist + ' - ' + name
        print(f'<{id}> {artist} - {name}')

        # download music
        exist_music = True
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
            exist_music = False
            print('music not found:', file)

        # download lyric
        if not exist_music:
            pass
        elif (file + '.lrc') in distlib:
            pass
        else:
            res = session.get(api_root + '/lyric', params={"id": id})
            data = res.json()
            filedir = path.join(dist, file + '.lrc')
            file = open(filedir, 'w+', encoding='utf-8')
            if 'lrc' in data and data['lrc']:
                print('downloaded lyric', name)
                file.write(data['lrc']['lyric'])
            else:
                file.write('No Lyrics found.')
            file.close()

    # m3u playlist
    filedir = path.join(dist, filename_filter(playlist_name) + '.m3u')
    file = open(filedir, 'w+', encoding='utf-8')
    file.write('\n'.join(map(lambda n: path.join(dist, n), playlist)))
    file.close()


if __name__ == '__main__':
    config = yaml.load(open(path.join(sys.path[0], 'config.yml')),
                       yaml.BaseLoader)
    for playlist in config['playlist']:
        crawl_playlist(config, playlist, config['dist_dir'])