import re
import os
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
            title = link.get('title')
            href = link.get('href')
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

def download_all(artist_page):
    """
    download all lyrics from an artist page on mojim.com
    """
    if not os.path.exists('lyrics'):
        os.makedirs('lyrics')
    soup = _make_soup(artist_page)
    album_blocks = soup.findAll('dd', 'hb2')
    album_blocks.extend(soup.findAll('dd', 'hb3'))

    for block in album_blocks:
        songs = block.findAll('span', 'hc3')
        songs.extend(block.findAll('span', 'hc4'))
        for s in songs:
            url_list = s.findAll('a')
            for i in url_list:
                href = i.get('href')
                title = i.get('title').strip(' 歌詞')
                url = f'http://mojim.com{href}'
                soup = _make_soup(url)
                lyrics = soup.find('dl', {'id': 'fsZx1'})
                lyrics = _clean_lyrics(lyrics)
                with open(f'./lyrics/{title}_{href[1:]}.txt', 'w') as fout:
                    fout.write(lyrics)
                print(f'{title} lyrics saved.')
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
        browser = webbrowser.get('safari')
        browser.open(url)
    return None


if __name__ == "__main__":
    # search_mojim('體面', 'song')
    # save_lyrics('于文文', '體面')

    # use search_mojim('于文文', 'artist') to find artist page
    artist_page = 'https://mojim.com/twh135268.htm'
    download_all(artist_page)