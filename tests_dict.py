import json

# characters dictionary 
# number of entries: 15080
# characters_dictionary = json.load(open('./data/characters.json'))
# for character in characters_dictionary:
#     print(character, characters_dictionary[character])
# print(f'total characters: {len(characters_dictionary)}')

# # simplified words dictionary
# # entries: 800876
with open('./data/simplified.txt') as dictionary:
    for i in dictionary.readlines():
        print(i)
# # traditional words dictionary
# # entries: 978719
with open('./data/traditional.txt') as dictionary:
    for i in dictionary.readlines():
        print(i)
# # chengyu dictionary:
# # entries: 49453
with open('./data/chengyu.txt') as dictionary:
    for i in dictionary.readlines():
        print(i)

# # homonyms dictionary
# # number of entries: 1893
homonyms_dictionary = json.load(open('./data/homonyms.json'))
for homonym in homonyms_dictionary:
    print(homonym, homonyms_dictionary[homonym])
print(f'total entries: {len(homonyms_dictionary)}')