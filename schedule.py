from bs4 import BeautifulSoup

import json
import requests
import datetime

headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }


def currtime():
    return datetime.datetime.now().strftime('[%H:%M:%S]')


def load():
    r = requests.get('https://stopgame.ru/live_schedule', headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    streamlist = {}

    list_view = soup.find('div', {'class': '_streams-list_jbt7s_100'})
    for i in list_view.find_all('div', {'data-key': True}):
        try:
            data_key = i['data-key']
        except:
            data_key = None
        streamlist[data_key] = {}

        try:
            stream_title = i.find('h2', class_='_stream-title_jbt7s_1').text
        except:
            stream_title = None
        streamlist[data_key]['stream_title'] = stream_title

        try:
            stream_poster = i.find('img', class_='_stream-poster_jbt7s_1').get('srcset').split()[1]
        except:
            stream_poster = None
        streamlist[data_key]['stream_poster'] = stream_poster

        try:
            stream_description = i.find('div', class_='_stream-description_jbt7s_1').text
            stream_description = stream_description.replace('\n', '') \
                                                   .replace('\xa0', ' ')
        except:
            stream_description = None
        streamlist[data_key]['stream_description'] = stream_description

        try:
            stream_streamer = i.find_all('a', class_='_stream-streamer_jbt7s_1')
            stream_streamers = []
            for streamer in stream_streamer:
                s = streamer.text.split()
                stream_streamers.append(' '.join(s))
            stream_streamers = ', '.join(stream_streamers)
        except:
            stream_streamers = None
        streamlist[data_key]['stream_streamers'] = stream_streamers

        stream_info = i.find_all('div', class_='_stream-info__item_jbt7s_1')

        try:
            stream_day = stream_info[0].find('span', {'class': '_stream-info__value_jbt7s_1'}).text
        except:
            stream_day = None
        streamlist[data_key]['stream_day'] = stream_day

        try:
            stream_time = stream_info[1].find('span', {'class': '_stream-info__value_jbt7s_1'}).text
        except:
            stream_time = None
        streamlist[data_key]['stream_time'] = stream_time

        try:
            stream_weekday = stream_info[0].find('span', {'class': '_stream-info__subtitle_jbt7s_1'}).text
        except:
            stream_weekday = None
        streamlist[data_key]['stream_weekday'] = stream_weekday

    return streamlist


def load_from_file(jsonfile):
    with open(jsonfile, 'r', encoding='UTF-8') as file:
        streamlist = json.load(file)
    file.close()
    return streamlist


def find_new_keys(streamlist, streamjson):
    new_keys = list(set(streamlist.keys()) - set(streamjson.keys()))
    if new_keys:
        print(currtime(), 'find new keys:', new_keys)
    return new_keys


def find_old_keys(streamlist, streamjson):
    old_keys = list(set(streamjson.keys()) ^ set(streamlist.keys()))
    if old_keys:
        print(currtime(), 'find old keys', old_keys)
    return old_keys


def find_diff_values(streamlist, streamjson):
    diff_values = []
    for i in streamlist.keys():
        if streamlist[i]['stream_title'] != streamjson[i]['stream_title']:
            print(currtime(), 'find difference value in', i, '(title)')
            print(' '*10, 'new:', streamlist[i]['stream_title'])
            print(' '*10, 'old:', streamjson[i]['stream_title'])
            if i not in diff_values:
                diff_values.append(i)

        if streamlist[i]['stream_poster'] != streamjson[i]['stream_poster']:
            print(currtime(), 'find difference value in', i, '(poster)')
            print(' '*10, 'new:', streamlist[i]['stream_poster'])
            print(' '*10, 'old:', streamjson[i]['stream_poster'])
            # if i not in diff_values:
            #     diff_values.append(i)

        if streamlist[i]['stream_description'] != streamjson[i]['stream_description']:
            print(currtime(), 'find difference value in', i, '(description)')
            print(' '*10, 'new:', streamlist[i]['stream_description'])
            print(' '*10, 'old:', streamjson[i]['stream_description'])
            if i not in diff_values:
                diff_values.append(i)

        if streamlist[i]['stream_streamers'] != streamjson[i]['stream_streamers']:
            print(currtime(), 'find difference value in', i, '(streamers)')
            print(' '*10, 'new:', streamlist[i]['stream_streamers'])
            print(' '*10, 'old:', streamjson[i]['stream_streamers'])
            if i not in diff_values:
                diff_values.append(i)

        if streamlist[i]['stream_day'] != streamjson[i]['stream_day']:
            print(currtime(), 'find difference value in', i, '(day)')
            print(' '*10, 'new:', streamlist[i]['stream_day'])
            print(' '*10, 'old:', streamjson[i]['stream_day'])
            if i not in diff_values:
                diff_values.append(i)

        if streamlist[i]['stream_time'] != streamjson[i]['stream_time']:
            print(currtime(), 'find difference value in', i, '(time)')
            print(' '*10, 'new:', streamlist[i]['stream_time'])
            print(' '*10, 'old:', streamjson[i]['stream_time'])
            if i not in diff_values:
                diff_values.append(i)

        if streamlist[i]['stream_weekday'] != streamjson[i]['stream_weekday']:
            print(currtime(), 'find difference value in', i, '(weekday)')
            print(' '*10, 'new:', streamlist[i]['stream_weekday'])
            print(' '*10, 'old:', streamjson[i]['stream_weekday'])
            if i not in diff_values:
                diff_values.append(i)
    return diff_values


def add_to_json(jsonfile, key, streamlist, streamjson):
    streamjson[key] = streamlist[key]
    with open(jsonfile, 'w', encoding='UTF-8') as file:
        file.write(json.dumps(streamjson))
    file.close()
    print(currtime(), f'{key} add to {jsonfile}')


def remove_from_json(key, streamjson, jsonfile):
    streamjson.pop(key, None)
    with open(jsonfile, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(streamjson))
    f.close()
    print(currtime(), f'{key} delete from {jsonfile}')


def get_caption(streamlist, key):
    title = streamlist[key]['stream_title']
    if not title:
        title = ''

    description = streamlist[key]['stream_description']
    if not description:
        description = ''
    else:
        description = f'\n\n{description}'

    streamers = streamlist[key]['stream_streamers']
    if not streamers:
        streamers = ''
    else:
        streamers = f'\n\n{streamers}'

    day = streamlist[key]['stream_day']
    if not day:
        day = ''
    else:
        day = f'\n\n{day}'

    weekday = streamlist[key]['stream_weekday']
    if not weekday:
        weekday = ''
    else:
        weekday = f' ({weekday})'

    time = streamlist[key]['stream_time']
    if not time:
        time = ''
    else:
        time = f'\n{time}'

    caption = f'<b>{title}</b>' \
              f'{day}{weekday}{time}' \
              f'{description}' \
              f'<em>{streamers}</em>'

    return caption
