import json
from canto import *

print('--- search jyutping ---')
print('single character search: ')
print(search('笨','jyutpings'))
print('multi cahracter search: ') 
print(search('你好世界', 'jyutpings'))
print('failed search:')
print(search('xyz', 'jyutpings'))
print()

print('--- search tones ---')
print('single character search: ')
print(search('笨', 'tones'))
print('multi cahracter search: ') 
print(search('你好世界', 'tones'))
print('failed search:')
print(search('xyz', 'tones'))
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
