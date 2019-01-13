import re
import json

import requests
from bs4 import BeautifulSoup

song = '龍舌蘭'

def make_soup(url):
    """
    make soup!
    """
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html5lib')
    return soup


def parse_song_id(song):
    """
    parse song id for the given song name from Mojim.com
    """
    try:
        soup = make_soup(f'https://mojim.com/{song}.html?t3')
    except:
        print('unable to make soup :(')

    spans = soup.findAll('span', {'class': 'mxsh_ss4'})
    pattern = re.compile(r'(.*?) ')
    for s in spans:
        link = s.find('a', {'title': pattern})
        if link is not None:
            return link.attrs['href']
    return None


def fetch_lyrics(song):
    """
    fetch and save lyrics from Mojim.com
    output: song_name.txt
    """
    cleaned_lyrics = ''
    song_id = parse_song_id(song)
    soup = make_soup(f'http://mojim.com{song_id}')
    lyrics = soup.find('dl', {'id': 'fsZx1'})
    if lyrics is None:
        print(f'unable to fetch lyrics for: {song}')
        return None

    lyrics = [str(line) for line in lyrics.contents]
    for i in lyrics:
        if 'br' in i:
            i = '\n'
        if '[' in i or ':' in i or '：' in i or '<' in i or 'Mojim' in i:
            continue
        cleaned_lyrics += i

    cleaned_lyrics = cleaned_lyrics.strip()
    with open(song + '.txt', 'w') as fout:
        fout.write(cleaned_lyrics)
    print(f'{song} lyrics saved.')
    return None


if __name__ == "__main__":
    fetch_lyrics(song)