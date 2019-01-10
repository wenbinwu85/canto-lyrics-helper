import re
import json

import requests
from bs4 import BeautifulSoup

song = '龍舌蘭'


def search(characters, attribute='jyutpings'):
    """
    return jyutpings or tones for each character
    example usages:
        search('笨', 'jyutpings')
        search('你好世界', 'tones')
    """
    if not attribute in ('jyutpings', 'tones'):
        raise AttributeError('can only search for "jyutpings" or "tones".')

    dictionary = json.load(open('./data/characters.json'))
    result = ''

    if characters == '\n':
        return ''
    for character in characters:
        try:
            data = dictionary[character][attribute]
            data = ' '.join(data)
            result += ' '.join((character, data))
        except KeyError:
            continue
        result += ' '

    if not result:
        print(f'{characters} is not in the dictionary.')
    return result


def search_words(character, dictionary='fanti'):
    """
    return words that contain a specific character
    example usage:
        search_words('笨', 'jianti')
        search_words('蛋', 'fanti')
    """

    if dictionary == 'fanti':
        file = './data/traditional.txt'
    elif dictionary == 'jianti':
        file = './data/simplified.txt'
    elif dictionary == 'chengyu':
        file = './data/chengyu.txt'
    else:
        raise AttributeError('No such dictionary!')

    result = []
    with open(file) as wordlist:
        for word in wordlist:
            if character in word:
                result.append(word.strip('\n'))
    if not result:
        print(f'no words found for: {character}')
    
    result = ' '.join(sorted(result, key=len))
    return result


def search_homonyms(jyutping):
    """
    return homonym characters for the jyutping sound, input can be partial or whole jyutping
    example usage:
        search_homonyms('baang2')
        search_homonyms('aang')
    """

    homonyms = json.load(open('./data/homonyms.json'))
    result = ''
    for k, v, in homonyms.items():
        if jyutping in k:
            result += k + ' : ' + ' '.join(v) + '\n'
    if not result:
        print('no homonyms found!')
    return result


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


def mark_lyrics(song):
    """
    mark each word in the lyrics with jyutping
    output: song_name_marked.txt
    """

    marked_lyrics = ''
    try:
        with open(song + '.txt', 'r') as fin:
            for line in fin:
                marked_line = search(line, 'tones')
                marked_lyrics += marked_line + '\n'
    except FileNotFoundError:
        print(f'{song}.txt. does not exist!')
        return None
    
    with open(song + '_marked.txt', 'w') as fout:
        fout.write(marked_lyrics)
    print(f'{song} lyrics is marked with jyutping.')
    return None


if __name__ == "__main__":
    print('cantonese lyrics helper')
    print('by wenbin wu')

    fetch_lyrics(song)