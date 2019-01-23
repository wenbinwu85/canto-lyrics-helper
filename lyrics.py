import re
import json
import webbrowser
import requests
from bs4 import BeautifulSoup


def _make_soup(url):
    """
    make soup!
    """
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html5lib')
    return soup


def _find_song_urls(artist, song):
    """
    find song urls from mojim.com for the given song name.
    """
    try:
        soup = _make_soup(f'https://mojim.com/{song}.html?t3')
    except:
        print('unable to make soup :(')

    spans = soup.findAll('span', {'class': 'mxsh_ss4'})
    pattern = re.compile(r'(.*?) ')
    result = []
    for s in spans:
        link = s.find('a', {'title': pattern})
        if link is not None:
            title = link.attrs.get('title')
            href = link.attrs.get('href')
            if artist in title:
                result.append(href)
    return result


def _clean_lyrics(lyrics):
    """
    remove junk from the lyrics
    """
    cleaned_lyrics = ''
    lyrics = [str(line) for line in lyrics.contents]
    for i in lyrics:
        if 'br' in i:
            i = '\n'
        if '[' in i or ':' in i or '：' in i or '<' in i or 'Mojim' in i:
            continue
        cleaned_lyrics += i
    return cleaned_lyrics.strip()


def save_lyrics(artist, song):
    """
    fetch and save lyrics from Mojim.com
    """
    song_urls = _find_song_urls(artist, song)
    for url in song_urls:
        soup = _make_soup(f'http://mojim.com{url}')
        lyrics = soup.find('dl', {'id': 'fsZx1'})
        if lyrics is None:
            print(f'unable to fetch lyrics for: {song}')
            return None
        lyrics = _clean_lyrics(lyrics)
        with open(f'{song}_{url[1:]}.txt', 'w') as fout:
            fout.write(lyrics)
        print(f'{artist} - {song} lyrics saved.')
    return None


def search_mojim(query, param):
    """
    search query on mojim.com and open the result page in a broswer
    """
    url_dict = {
        'artist': f'https://mojim.com/{query}.html?t1',
        'album': f'https://mojim.com/{query}.html?t2',
        'song': f'https://mojim.com/{query}.html?t3',
        'lyrics': f'https://mojim.com/{query}.html?t4',
    }
    try:
        url = url_dict[param]
    except KeyError:
        print('No such param!')
    else:
        browser = webbrowser.get('Chrome')
        browser.open(url)
    return None


if __name__ == "__main__":
    search_mojim('于文文', 'artist')
    save_lyrics('于文文', '體面')
