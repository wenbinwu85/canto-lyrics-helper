import re
import json

import requests
from bs4 import BeautifulSoup

song = '龍舌蘭'


def search_jyutpin(characters):
    """
    return jyutpin for one or more traditional chinese characters
    example usage:
        search_jyutpin('笨')
        search_jyutpin('你好世界')
    """

    dictionary = json.load(open('./data/characters.json'))
    result = ''

    if characters == '\n':
        return ''
    for character in characters:
        try:
            jyutpin = dictionary[character]
            result += character + ' ' + ' '.join(jyutpin)
        except KeyError:
            continue
        result += ' '

    if not result:
        print(f'{characters} is not in the dictionary.')
    return result


def search_words(character):
    """
    return words that contain a specific character
    example usage:
        search_words('笨')
    """

    result = []
    with open('./data/dictionary.txt') as wordlist:
        for word in wordlist:
            if character in word:
                result.append(word.strip('\n'))
    if not result:
        print(f'no words found for: {character}')
    
    result = ' '.join(sorted(result, key=len))
    return result


def search_homonyms(jyutpin):
    """
    return homonym characters for the jyutpin sound, input can be partial or whole jyutpin
    example usage:
        search_homonyms('baang2')
        search_homonyms('aang')
    """

    homonyms = json.load(open('./data/homonyms.json'))
    result = ''
    for k, v, in homonyms.items():
        if jyutpin in k:
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
    mark each word in the lyrics with jyutpin
    """

    marked_lyrics = ''
    try:
        with open(song + '.txt', 'r') as fin:
            for line in fin:
                marked_line = search_jyutpin(line)
                marked_lyrics += marked_line + '\n'
    except FileNotFoundError:
        print(f'{song}.txt. does not exist!')
        return None
    
    with open(song + '_marked.txt', 'w') as fout:
        fout.write(marked_lyrics)
    print(f'{song} lyrics is marked with jyutpin.')
    return None


if __name__ == "__main__":
    # tests
    print('--- search jyutpin ---')
    print('single character search: ')
    print(search_jyutpin('笨'))
    print('multi cahracter search: ') 
    print(search_jyutpin('你好世界'))
    print('failed search:')
    print(search_jyutpin('xyz'))
    print()

    print('--- search words ---')
    print('words containing 笨')
    print(search_words('笨'))
    print('failed search:')
    print(search_words('xyz'))
    print()

    print('--- search homonyms -- ')
    print(search_homonyms('aang'))
    print('failed search:')
    print(search_homonyms('xyz'))
    print()

    print('--- fetch / mark lyrics ---')
    fetch_lyrics(song)
    mark_lyrics(song)
    print()

    print('--- failed fetch / mark lyrics ---')
    fetch_lyrics('你好世界')
    mark_lyrics('你好世界')