import re
import os
import csv
import json
import shelve
import webbrowser
import requests
from bs4 import BeautifulSoup

class Corpus:
    def __init__(self):
        self.characters = self._load('./dicts/characters.json')
        self.homophones = self._load('./dicts/homophones.json')
        self.words = self._load('./dicts/words.txt')
        self.idioms1 = self._load('./dicts/idiom.txt')
        self.idioms2 = self._load('./dicts/idiom2.txt')

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

    def get_char(self, char):
        return self.characters.get(char, None)

    def get_words(self, char):
        words = [w.strip('\n') for w in self.words if char in w]
        return sorted(words, key=len)

    def get_homophones(self, char):
        return {jp:self.homophones.get(jp) for jp in char.jyutpings}

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
        jyutpings = ''.join
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
        return corpus.get_homophones(self.character)

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
    def __init__(self, artist=''):
        self._artist = artist
        self._lang = 0
        self._tag = ['g3', 't3']

    def _make_soup(self, url):
        resp = requests.get(url).text
        soup = BeautifulSoup(resp, 'html5lib')
        return soup

    def _clean(self, lyrics):
        cleaned = ''
        lyrics = [str(line) for line in lyrics.contents]
        for i in lyrics:
            if 'br' in i:
                i = '\n'
            if '[' in i or ':' in i or '：' in i or '<' in i or 'Mojim' in i:
                continue
            cleaned += i
        return cleaned.strip()

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, name):
        self._artist = name

    @property
    def lang(self):
        return self._lang
    
    @lang.setter
    def lang(self, lang):
        self._lang = lang

    def save(self, song):
        soup = self._make_soup(f'https://mojim.com/{song}.html?{self._tag[self._lang]}')
        spans = soup.findAll('span', {'class': 'mxsh_ss4'})
        pattern = re.compile(r'(.*?) ')
        result = []
        for s in spans:
            link = s.find('a', {'title': pattern})
            if link:
                title = link.get('title')
                href = link.get('href')
                if self.artist in title:
                    result.append(href)
        if not result:
            return False
        for url in result:
            soup = self._make_soup(f'http://mojim.com{url}')
            lyrics = soup.find('dl', {'id': 'fsZx1'})
            lyrics = self._clean(lyrics)
            with open(f'{self.artist} - {song}.txt', 'w', encoding='utf-8') as fout:
                fout.write(lyrics)
        return True  

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
    mj = Mojim()
    mj.artist = '陳奕迅'
    mj.save('讓我留在你身邊')
