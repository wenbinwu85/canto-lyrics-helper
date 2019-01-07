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


def fetch_lyrics(id):
    cleaned_lyrics = ''
    soup = make_soup(f'http://mojim.com{id}')
    lyrics = soup.find('dl', {'id': 'fsZx1'})
    lyrics = [str(line) for line in lyrics.contents]

    for i in lyrics:
        if 'br' in i:
            i = '\n'
        if '[' in i or '<' in i or 'Mojim' in i:
            continue
        cleaned_lyrics += i

    cleaned_lyrics = cleaned_lyrics.strip()
    with open(song + '.txt', 'w') as fout:
        fout.write(cleaned_lyrics)
    print(song + ' lyrics saved.')


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
        fetch_lyrics(song_id)
