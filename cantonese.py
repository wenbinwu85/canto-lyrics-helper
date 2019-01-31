import json
from functools import reduce
from itertools import permutations


def _load_dict(dict_name):
    if '.json' in dict_name:
        return json.load(open(f'./dicts/{dict_name}', encoding='utf-8'))
    if '.txt' in dict_name:
        filein = open(f'./dicts/{dict_name}', encoding='utf-8')
        mydict = filein.readlines()
        filein.close()
        return mydict

characters_dict = _load_dict('characters.json')
homophones_dict = _load_dict('homophones.json')
# words_dict = _load_dict('simplified.txt')
words_dict = _load_dict('traditional.txt')


class Character:
    def __init__(self, char):   
        try:
            self._data = characters_dict.get(char, None)
        except KeyError:
            print(f'Can not find such character: {char}')  
        self._character = char
        self._juytpings = self._data.get('jyutpings')
        self._tones = self._data.get('tones')


    def jyutpings(self):
        return self._juytpings


    def tones(self):
        return self._tones


    def words(self):
        return [word.strip('\n') for word in words_dict if self._character in word]


    def homophones(self):
        return  {jp: homophones_dict.get(jp) for jp in self._juytpings}


    def compare(self, other):
        if not isinstance(other, Character):
            raise ValueError(f'Can not compare Character type to {type(other)}')
        for tone in other.tones():
            if tone in self._tones:
                return True
            else:
                return False


class Word:
    def __init__(self, chars):
        self._word = chars
        self._chars = []  # list of character objects
        self._tones = []  # list of tones combinations
        try:
            for c in chars:
                self._chars.append(Character(c))
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
        tones_lists = [char.tones() for char in self._chars]
        tones_combos = reduce(self._make_tones_combos, tones_lists)
        self._tones = [self._flatten(t) for t in tones_combos]
        return None


    def jyutpings(self):
        result = {c.character: c.jyutpings() for c in self._chars}
        return result


def homonyms_by_word(word):
    words_pool = [w.strip('\n') for w in words_dict if len(w)-1 == len(word)]
    word_obj = Word(word)
    result = {}

    for t in word_obj.tones:
        matched_words = []
        for w in words_pool:
            if t in Word(w).tones:
                matched_words.append(w)
        result[t] = matched_words

    with open('homonyms_by_words.txt', 'w', encoding='utf-8') as fout:
        for i in result:
            fout.write(i + '\n' + ' '.join(result[i]) + '\n')
        print('file saved.')
    return None


def homonyms_by_tones(tones):
    words_pool = [w.strip('\n') for w in words_dict if len(w)-1 == len(tones)]
    result = [w.strip('\n') for w in words_pool if tones in Word(w.strip('\n')).tones]

    with open('homonyms_by_tones.txt', 'w', encoding='utf-8') as fout:
        fout.write(' '.join(result))
        print('file saved.')
    return None


if __name__ == '__main__':
    # homonyms_by_tones('33')
    # homonyms_by_word('對不起')
    
    x = Character('好')
    y = Character('對')
    print(x.tones())
    print(y.tones())
    if x.compare(y):
        print('they sound the same!')
    else:
        print('they do not sound the same')