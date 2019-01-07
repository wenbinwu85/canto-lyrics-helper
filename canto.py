import re
import os
import json
import webbrowser

import requests
from bs4 import BeautifulSoup

songs = ['龍舌蘭', '體面', '突然好想你']

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


def make_soup(url):
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html5lib')
    return soup


def parse_song_id(song):
    soup = make_soup(f'https://mojim.com/{song}.html?t3')
    spans = soup.findAll('span', {'class': 'mxsh_ss4'})
    pattern = re.compile(r"(.*?) ")
    for s in spans:
        link = s.find('a', {'title': pattern})
        if link is not None:
            return link.attrs['href']
    return None


def save_lyrics(id):
    soup = make_soup(f'http://mojim.com{id}')
    lyrics = soup.find('dl', {'id': 'fsZx1'})
    with open(song + '.htm', 'w', encoding='utf-8') as fout:
        fout.write(lyrics.prettify())
    print(song + ' lyrics saved.')


def clean_lyrics(song):
    cleaned_lyrics = ''
    with open(song + '.htm') as lyrics:
        for line in lyrics:
            if 'br' in line:
                line = '\n'
            elif ('Mojim.com' in line) or ('[' in line) or ('<' in line):
                continue
            cleaned_lyrics += line

    cleaned_lyrics = cleaned_lyrics.replace('\n\n', '\n')
    cleaned_lyrics = cleaned_lyrics.strip()

    with open(song + '.txt', 'w') as fout:
        for line in cleaned_lyrics:
            fout.write(line)
    print('lyrics is clean!')


if __name__ == "__main__":
    # example use
    # search_dictionary('笨')
    # print()
    # search_dictionary('你好世界')
    # print()
    # search_homonyms('paang4')
    # print()
    # search_words('飛')

    for song in songs:
        song_id = parse_song_id(song)
        save_lyrics(song_id)
        clean_lyrics(song)