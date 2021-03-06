import re
import os
import csv
import json
import shelve
import requests
from bs4 import BeautifulSoup

class Corpus:
    def __init__(self):
        self._characters = self._load('./dicts/characters.json')
        self._homophones = self._load('./dicts/homophones.json')
        self._words = self._load('./dicts/words.txt')
        self._idioms1 = self._load('./dicts/idiom.txt')
        self._idioms2 = self._load('./dicts/idiom2.txt')

    def _load(self, filename):
        if '.' not in filename:
            data = {}
            with shelve.open(filename) as db:
                for key, val in db.items():
                    data[key] = val
            return data

        with open(filename, encoding='utf-8') as filein:
            if filename.endswith('.csv'):
                reader = csv.reader(filein, delimiter=',')
                return list(reader)
            if filename.endswith('.json'):
                return json.load(filein)
            if filename.endswith('.txt'):
                return filein.readlines()

    def search(self, query):
        return [word.strip('\n') for word in self._words if query in word]

    def search_idioms(self, query):
        return [idiom.strip('\n') for idiom in self._idioms1 if query in idiom]


    def get_char(self, char):
        return self.characters.get(char, None)

    def get_words(self, char):
        words = [w.strip('\n') for w in self.words if char in w]
        return sorted(words, key=len)

    def get_homophones(self, char):
        result = ''
        for jp in char.jyutpings:
            homophones = f"{jp} : {''.join(self.homophones.get(jp))}\n"
            result += homophones
        return result

    def get_idioms(self, char, long=False):
        if long:
            return [i.strip('\n') for i in self.idioms2 if char in i]
        return [i.strip('\n') for i in self.idioms1 if char in i]


corpus = Corpus()


class Character:
    def __init__(self, char):
        self._data = corpus.get_char(char)
        if not self._data:
            raise ValueError(f'Can not create character: {char}')
        self._character = char
        self._jyutpings = self._data.get('jyutpings')
        self._syllables = self._data.get('syllables')
        self._tones = self._data.get('tones')

    def __str__(self):
        return f'Character: {self._character} \
                Jyutpings: {self.jyutpings} \
                Syllables: {self.syllables} \
                Tones: {self.tones}'

    def __repr__(self):
        return f'Character(char={self._character})'

    def __eq__(self, other):
        """
        param: Character
        return: True or False

        compare two characters to see if they have a matching tone
        char1 == char2 returns True if they have at least 1 common tone
        """
        if not isinstance(other, Character):
            raise ValueError(f'Can not compare Character type to {type(other)}')

        if set(other.tones).intersection(set(self.tones)):
            return True
        return False

    @property
    def character(self):
        return self._character

    @property
    def jyutpings(self):
        return self._jyutpings

    @property
    def syllables(self):
        return self._syllables

    @property
    def tones(self):
        return self._tones

    def words(self):
        return corpus.get_words(self.character)

    def homophones(self):
        return corpus.get_homophones(self)

    def idioms(self):
        idioms = corpus.get_idioms(self.character)
        idioms2 = corpus.get_idioms(self.character,long=True)
        idioms.extend(idioms2)
        idioms = sorted(idioms, key=len)
        return idioms


class Word:
    def __init__(self, chars):
        self.word = chars
        self.characters = [Character(c) for c in chars]

    def __str__(self):
        tones = [char.__str__() for char in self.characters]
        return '\n'.join(tones)

    def __repr__(self):
        return f'Word(chars={self.characters})'

    def __eq__(self, other):
        for a, b in zip(self.characters, other.characters):
            if a != b:
                print(f'{a.character} != {b.character}')
                return False


class Mojim:
    def __init__(self, artist='', song=''):
        self._artist = artist
        self._song = song

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, artist):
        self._artist = artist

    @property
    def song(self):
        return self._song

    @song.setter
    def song(self, song):
        self._song = song

    def _make_soup(self, url):
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, 'html5lib')
        return soup

    def _find_lyrics(self, url):
        soup = self._make_soup(url)
        spans = soup.findAll('span', {'class': 'mxsh_ss4'})
        pattern = re.compile(r'(.*?) ')
        url = ''
        for s in spans:
            link = s.find('a', {'title': pattern})
            if link:
                if self.artist in link.get('title'):
                    url = link.get('href')
        soup = self._make_soup(f'http://mojim.com{url}')
        return soup.find('dl', {'id': 'fsZx1'})

    def _clean(self, lyrics):
        cleaned = ''
        lyrics = [str(line) for line in lyrics.contents]
        for i in lyrics:
            if 'br' in i:
                i = '\n'
            if '[' in i or ':' in i or '：' in i or '<' in i or 'Mojim' in i:
                continue
            if self.artist in i or self.song in i:
                continue
            cleaned += i
        return cleaned.strip()

    def save(self, artist=None, song=None):
        self.artist = artist
        self.song = song
        simplified_url = f'https://mojim.com/{song}.html?g3'
        traditional_url = f'https://mojim.com/{song}.html?t3'
        lyrics = self._find_lyrics(simplified_url) or self._find_lyrics(traditional_url)
        if not lyrics:
            return None
        lyrics = self._clean(lyrics)
        with open(f'{artist} - {song}.txt', 'w', encoding='utf-8') as fout:
            fout.write(lyrics)
        return lyrics


    # def archive(self, artist_page):
    #     if not os.path.exists('lyrics'):
    #         os.makedirs('lyrics')
    #     soup = self._make_soup(artist_page)
    #     album_blocks = soup.findAll('dd', 'hb2')
    #     album_blocks.extend(soup.findAll('dd', 'hb3'))

    #     for block in album_blocks:
    #         songs = block.findAll('span', 'hc3')
    #         songs.extend(block.findAll('span', 'hc4'))
    #         for s in songs:
    #             url_list = s.findAll('a')
    #             for i in url_list:
    #                 href = i.get('href')
    #                 title = i.get('title').strip(' 歌词')
    #                 url = f'http://mojim.com{href}'
    #                 soup = self._make_soup(url)
    #                 lyrics = soup.find('dl', {'id': 'fsZx1'})
    #                 lyrics = self._clean(lyrics)
    #                 with open(f'./lyrics/{title}_{href[1:]}.txt', 'w', encoding='utf-8') as fout:
    #                     fout.write(lyrics)
    #                 print(f'{self.artist} - {s} lyrics saved.')
    #     return None


if __name__ == '__main__':
    char = Character('好')
    words = char.words()
    idioms = char.idioms()
    homophones = char.homophones()

    print(words, '\n')
    print(idioms, '\n')
    print(homophones, '\n')
