import json
from functools import reduce
from itertools import permutations

characters_dict = json.load(open('./dicts/characters.json'))
homophones = json.load(open('./dicts/homophones.json'))

corpus = 'fanti'
dict_name = './dicts/traditional.txt' if corpus == 'fanti' else './dicts/simplified.txt'
words_dict = []
with open(dict_name) as file:
    words_dict = file.readlines()

class Character:
    def __init__(self, char):
        self.data = characters_dict.get(char, None)
        if not self.data:
            raise ValueError(f'Can not find such character: {char}')
        self.character = char
        self._juytpings = self.data.get('jyutpings')
        self._tones = self.data.get('tones')

    def jyutpings(self):
        return self._juytpings

    def tones(self):
        return self._tones

    def words(self):
        result = [word.strip('\n') for word in words_dict if self.character in word]
        return result

    def homophones(self):
        result = {jp: homophones.get(jp) for jp in self._juytpings}
        return result

class Word:
    def __init__(self, chars):
        self.word = chars
        self.chars = []  # list of character objects
        self.tones = []  # list of tones combinations
        try:
            for c in chars:
                self.chars.append(Character(c))
            self._get_tones_combos()
        except ValueError as e:
            pass # do not print error message

    def _make_tones_combos(self, list1, list2):
        result = [(i, p[0]) for i in list1 for p in permutations(list2, r=1)]
        return result

    def _flatten(self, iterable): 
        if isinstance(iterable, str):
            return iterable
        return str(self._flatten(iterable[0]) + iterable[1])

    def _get_tones_combos(self):
        tones_lists = [char.tones() for char in self.chars]
        tones_combos = reduce(self._make_tones_combos, tones_lists)
        self.tones = [self._flatten(t) for t in tones_combos]
        return None

    def jyutpings(self):
        result = {c.character: c.jyutpings() for c in self.chars}
        return result

    def homonyms(self):
        result = {}
        words_pool = [w.strip('\n') for w in words_dict if len(w)-1 == len(self.word)]
        for t in self.tones:
            matched_words = []
            for w in words_pool:
                try:
                    if t in Word(w).tones:
                        matched_words.append(w)
                except ValueError:
                    continue
            result[t] = matched_words
        return result