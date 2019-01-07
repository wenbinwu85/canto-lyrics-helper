import re
import os
import json
import webbrowser

import requests
from bs4 import BeautifulSoup


def search_dictionary(characters):
    dictionary = json.load(open('./data/characters.json'))
    for character in characters:
        jyutping = dictionary[character]
        print(f'{character}', end=' ')
        for i in jyutping:
            print(i, end=' ')
    print()


def search_words(character):
    matches = ''
    print(f'{character} 字詞組：')
    with open('./data/dictionary.txt') as wordlist:
        for word in wordlist:
            if character in word:
                matches += word.strip('\n') + ' '
    print(matches)
    print()


def search_homonyms(sound):
    homonyms = json.load(open('./data/homonyms.json'))
    print(f'{sound} 同音字:')
    for character in homonyms[sound]:
        print(character, end=' ')
    print()


def parse_song_id(song):
    search_url = f'https://mojim.com/{song}.html?t3'
    resp = requests.get(search_url).text
    soup = BeautifulSoup(resp, 'html5lib')
    spans = soup.findAll('span', {'class': 'mxsh_ss4'})

    pattern = re.compile(r"(.*?) ")
    for s in spans:
        link = s.find('a', {'title': pattern})
        if link is not None:
            return link.attrs['href']
    return None


def save_lyrics(id):
    url = f'http://mojim.com{id}'
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html5lib')
    lyrics = soup.find('dl', {'id': 'fsZx1'})
    ad = '更多更詳盡歌詞 在 ※ Mojim.com　魔鏡歌詞網'

    with open(song + '.htm', 'w', encoding='utf-8') as fout:
        fout.write(lyrics.prettify().replace(ad, ''))
    webbrowser.open('file://' + os.path.realpath(song + '.htm'))


if __name__ == "__main__":
    # example use
    # search_dictionary('笨')
    # print()
    # search_dictionary('你好世界')
    # print()
    # search_homonyms('paang4')
    # print()
    # search_words('飛')

    song = '其實其實'
    song_id = parse_song_id(song)
    save_lyrics(song_id)
    print(song + ' lyrics saved.')
