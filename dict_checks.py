import json

# characters dictionary 
# number of entries: 15080
characters_dictionary = json.load(open('./data/characters.json'))
for character in characters_dictionary:
    print(character, characters_dictionary[character])
print(f'total characters: {len(characters_dictionary)}')

# words dictionary, this contain too many words, can run for while
# number of entries: 919783
with open('./data/dictionary.txt') as dictionary:
    for i in dictionary.readlines():
        print(i)
    print(f'total words: {len(dictionary.readlines())}')

# homonyms dictionary
# number of entries: 1893
homonyms_dictionary = json.load(open('./data/homonyms.json'))
for homonym in homonyms_dictionary:
    print(homonym, homonyms_dictionary[homonym])
print(f'total entries: {len(homonyms_dictionary)}')