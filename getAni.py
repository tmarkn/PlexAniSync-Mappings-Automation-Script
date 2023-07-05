import json
import re
import requests
from bs4 import BeautifulSoup as bs
from thefuzz import fuzz
from urllib import parse

anilistExp = re.compile(r'\/?anime\/([0-9]+)', re.IGNORECASE)
seasonExp = re.compile(r'(?:([0-9]+)(?:st|nd|rd|th) Season)|(?:Season ([0-9]+))|(?:Part ([0-9])+)|(?:Cour ([0-9]+))', re.IGNORECASE)
romajiExp = re.compile(r'([aeiou]|[bkstgzdnhpmr]{1,2}[aeiou]|(?:sh|ch|j|ts|f|y|w|k)(?:y[auo]|[aeiou])|n|\W|[0-9])+', re.IGNORECASE)

class anilistEntry:
    def __init__(self, title: str) -> None:
        self.title = title
        self.synonyms = []
        self.seasons = []
    def __repr__(self) -> str:
        string = f'  - title: {json.dumps(self.title)}\n'
        if len(self.synonyms):
            string += '    synonyms:\n'
            for syn in self.synonyms:
                string += f'      - {json.dumps(syn)}\n'
        string += '    seasons:\n'
        for season in self.seasons:
            string += f'      - season: {season[0]}\n'
            string += f'        anilist-id: {season[1]}\n'
        return string

def first(iterable, func=lambda L: L is not None, **kwargs):
    it = (el for el in iterable if func(el))
    if 'default' in kwargs:
        return next(it, kwargs['default'])
    return next(it) # no default so raise `StopIteration`

def getAniData(url: str, getPrequel: bool = False) -> anilistEntry:
    season = 1
    anilistId = None
    ## check valid link
    parsed_uri = parse.urlparse(url)
    
    ## check url for ######
    if url.isnumeric():
        anilistId = int(url)
    ## check url for anilist.co/anime/######
    elif parsed_uri.netloc == 'anilist.co':
        splitPath = parsed_uri.path[1:].split('/')
        if splitPath[0] != 'anime':
            raise Exception('provided url does not contain an anime')
        
        if not splitPath[1].isnumeric():
            raise Exception('provided url does not contain an anime entry')
        anilistId = int(splitPath[1])
    ## check url for /anime/######/
    else:
        anilistExpSearch = anilistExp.search(url)
        if anilistExpSearch is not None:
            anilistId = int(anilistExpSearch.group(1))
    ## not valid url
    if not anilistId:
        raise Exception('provided url is not of anilist.co')
    
    ## new url
    newUrl = f'https://anilist.co/anime/{anilistId}'

    ## get link
    r = requests.get(newUrl)

    ## check valid status code
    if r.status_code != 200:
        raise Exception('provided url does not lead to a valid location')
    
    ## parse html
    soup = bs(r.content, 'html.parser')

    ## find Romaji title
    romajiParent = soup.find('div', {'class': 'type'}, string="Romaji").parent
    romajiName = romajiParent.find('div', {'class': 'value'}).text.strip()

    ## find English title
    engHeader = soup.find('div', {'class': 'type'}, string="English")
    if engHeader:
        engName = engHeader.parent.find('div', {'class': 'value'}).text.strip()
    else:
        engName = romajiName

    ## check for season number in title
    search = seasonExp.search(engName)
    if search is not None:
        season = max(int(first(search.groups())), season)
    search = seasonExp.search(romajiName)
    if search is not None:
        season = max(int(first(search.groups())), season)

    ## create new entry 
    alEntry = anilistEntry(engName)

    ## find synoynms
    synHeader = soup.find('div', {'class': 'type'}, string='Synonyms')
    if synHeader:
        synList = synHeader.parent.find_all('span')
    
        for syn in synList:
            synTitle = syn.text.strip()
            # check fuzzy match or romaji
            if fuzz.ratio(synTitle, engName) > 50 or fuzz.ratio(synTitle, romajiName) > 50 or romajiExp.fullmatch(synTitle):
                alEntry.synonyms.append(synTitle)
            
            # check for season number in synonyms
            search = seasonExp.search(synTitle)
            if search is not None:
                season = max(int(first(search.groups())), season)

    ## add Romaji as synonym
    ## check if different from English name
    if romajiName != engName:
        alEntry.synonyms.append(romajiName)

    alEntry.seasons.append((season, anilistId))

    ## recursively find the prequels until the first season
    if getPrequel == True:
        if season > 1:
            ## find link of prequel
            link = soup.find('div', string="Prequel").find_parent('a', {'class': 'cover'}, href=True)['href']
            fullLink = 'https://anilist.co' + link
            ## get prequel entry and append
            newAlEntry = getAniData(url=fullLink, getPrequel=True) 
            newAlEntry.seasons.extend(alEntry.seasons)

            return newAlEntry

    ## no prequels
    return alEntry

if __name__ == '__main__':
    url = input('Please input the url of the anilist page you are trying to get:\n')
    print(getAniData(url=url, getPrequel=True))
