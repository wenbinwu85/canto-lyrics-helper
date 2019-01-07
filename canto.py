import re
import os
import json
import webbrowser

import requests
from bs4 import BeautifulSoup

song = '龍舌蘭'

def search_dictionary(characters):
    dictionary = json.load(open('./data/characters.json'))
    result = ''
    for character in characters:
        try:
            jyutping = dictionary[character]
            result += character
            for i in jyutping:
                result += i
        except KeyError:
            continue
        result += ' '
    return result


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
    for k, v, in homonyms.items():
        if sound in k:
            print(k + ' : ', ' '.join(v))
    return None


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


def fetch_lyrics(song):
    cleaned_lyrics = ''
    song_id = parse_song_id(song)
    soup = make_soup(f'http://mojim.com{song_id}')
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


def get_jyutpin(song):
    marked_lyrics = ''
    with open(song + '.txt', 'r') as fin:
        for line in fin:
            marked_line = search_dictionary(line)
            marked_lyrics += marked_line + '\n'
    
    with open(song + '2.txt', 'w') as fout:
        fout.write(marked_lyrics)


if __name__ == "__main__":
    search_homonyms('aa2')
    fetch_lyrics(song)
    get_jyutpin(song)