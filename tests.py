import json
from canto import *

print('--- search jyutping ---')
print('single character search: ')
print(search_jyutping('笨'))
print('multi cahracter search: ') 
print(search_jyutping('你好世界'))
print('failed search:')
print(search_jyutping('xyz'))
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
