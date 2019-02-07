import json
from functools import reduce
from itertools import permutations


def _load_dict(dict_name):
    if '.json' in dict_name:
        return json.load(open(f'./dicts/{dict_name}', encoding='utf-8'))
    if '.txt' in dict_name:
        with open(f'./dicts/{dict_name}', encoding='utf-8') as file:
            return file.readlines()

characters_dict = _load_dict('characters.json')
homophones_dict = _load_dict('homophones.json')
words_dict = _load_dict('traditional.txt') # or use 'simplified.txt'


class Character:
    def __init__(self, char):
        try:
            self._data = characters_dict.get(char, None)
        except KeyError:
            print(f'Can not find such character: {char}')
        self._character = char
        self._jyutpings = self._data.get('jyutpings')
        self._syllables = self._data.get('syllables')
        self._tones = self._data.get('tones')


    def __str__(self):
        return f'{self._character}\tjyutpings: {self._jyutpings}\tsyllables: {self._syllables}\ttones: {self._tones}'


    def __eq__(self, other):
        """
        compare two character to see if they have a matching tone. return true or false.
        """
        if not isinstance(other, Character):
            raise ValueError(f'Can not compare Character type to {type(other)}')
        match = True
        for tone in other.tones():
            if tone in self._tones:
                return True
            else:
                match = False
        return match


    def character(self):
        return self._character


    def jyutpings(self):
        return self._jyutpings


    def syllables(self):
        return self._syllables


    def tones(self):
        return self._tones


    def words(self):
        """
        return a list of words containing the character.
        """
        return [word.strip('\n') for word in words_dict if self._character in word]


    def homophones(self):
        """
        return homophones for each tone of the character.
        """
        return {jp:homophones_dict.get(jp) for jp in self._jyutpings}


class Word:
    def __init__(self, chars):
        self._word = chars
        self._characters = []  # list of character objects
        self._tones = []  # list of tones combinations
        try:
            for c in chars:
                self._characters.append(Character(c))
            self._tones = self._get_tones_combos()
        except ValueError:
            print('something is wrong!')


    def __str__(self):
        return f'{self._word}\t{self.jyutpings()}\t{self._tones}'


    def __eq__(self, other):
        if not isinstance(other, Word):
            raise ValueError(f'Can not compare Word type to {type(other)}')
        match = True
        for tone in other.tones():
            if tone in self._tones:
                return True
            else:
                match = False
        return match


    def _make_tones_combos(self, list1, list2):
        return [(i, p[0]) for i in list1 for p in permutations(list2, r=1)]


    def _flatten(self, iterable):
        if isinstance(iterable, str):
            return iterable
        return str(self._flatten(iterable[0]) + iterable[1])


    def _get_tones_combos(self):
        tones_lists = [char.tones() for char in self._characters]
        tones_combos = reduce(self._make_tones_combos, tones_lists)
        return [self._flatten(t) for t in tones_combos]


    def jyutpings(self):
        return [c.jyutpings() for c in self._characters]


    def tones(self):
        return self._tones


def homonyms_by_word(word):
    words_pool = [w.strip('\n') for w in words_dict if len(w)-1 == len(word)]
    word_obj = Word(word)
    result = {}

    for t in word_obj._tones:
        matched_words = []
        for w in words_pool:
            if t in Word(w)._tones:
                matched_words.append(w)
        result[t] = matched_words

    with open('homonyms_by_words.txt', 'w', encoding='utf-8') as fout:
        for i in result:
            fout.write(i + '\n' + ' '.join(result[i]) + '\n')
        print('file saved.')
    return None


def search_words_by_tone(tone, filter=None):
    for word in words_dict:
        try:
            w = Word(word.strip('\n'))
        except:
            continue
        if tone in w.tones() and filter is None:
            print(w)
            continue
        if tone in w.tones() and word.strip('\n')[-1] == filter:
            print(w)


def compare_phrases(phrase1, phrase2):
    phrase1_characters = [Character(c) for c in phrase1 if not c in ' []?']
    phrase2_characters = [Character(c) for c in phrase2 if not c in ' []?']
    zipped = zip(phrase1_characters, phrase2_characters)

    match = True
    for (a, b) in zipped:
        if a == b:
            continue
        else:
            print(a.character(), a.jyutpings())
            print(b.character(), b.jyutpings())
            print('-'*30)
            match = False
    return match


def cantonize(phrase):
    for i in phrase:
        c = Character(i)
        print(c.character(), c.jyutpings())
        print('-'*30)
    return None


if __name__ == '__main__':
    cantonize('這一雙手卑鄙到抱著你')
    search_words_by_tone('')