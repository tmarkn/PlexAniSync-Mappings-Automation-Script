import re
import requests
from bs4 import BeautifulSoup as bs
from thefuzz import fuzz
from urllib import parse

anilistExp = re.compile(r'\/anime\/([0-9]+)')
seasonExp1 = re.compile(r'([0-9]+)(?:st|nd|rd|th) Season')
seasonExp2 = re.compile(r'Season ([0-9]+)')
romajiExp = re.compile(r'([aeiou]|[bkstgzdnhpmr]{1,2}[aeiou]|(?:sh|ch|j|ts|f|y|w|k)(?:y[auo]|[aeiou])|n|\W|[0-9])+', re.IGNORECASE)

class anilistEntry:
    def __init__(self, title: str) -> None:
        self.title = title
        self.synonyms = []
        self.seasons = dict()
    def __repr__(self) -> str:
        string = f'- title: "{self.title}"\n'
        if len(self.synonyms):
            string += '  synonyms:\n'
            for syn in self.synonyms:
                string += f'    - "{syn}"\n'
        string += '  seasons:\n'
        for season in self.seasons:
            string += f'    - season: {season}\n'
            string += f'      anilist-id: {self.seasons[season]}\n'
        return string


def getAniData(url: str, getPrequel: bool = False) -> anilistEntry:
    season = 1
    anilistId = None
    ## check valid link
    parsed_uri = parse.urlparse(url)
    ## check url for /anime/######/
    
    if url.startswith('/anime/'):
        search = anilistExp.search(url)
        if search is not None:
            anilistId = int(search.group(1))
    ## check url for anilist.co/anime/######
    elif parsed_uri.netloc == 'anilist.co':
        splitPath = parsed_uri.path[1:].split('/')
        if splitPath[0] != 'anime':
            raise Exception('provided url does not contain an anime')
        
        if not splitPath[1].isnumeric():
            raise Exception('provided url does not contain an anime entry')
        anilistId = int(splitPath[1])

    ## not valid url
    else:
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
    search = seasonExp1.search(engName)
    if search is not None:
        season = max(int(search.group(1)), season)
    search2 = seasonExp2.search(engName)
    if search2 is not None:
        season = max(int(search2.group(1)), season)
    search = seasonExp1.search(romajiName)
    if search is not None:
        season = max(int(search.group(1)), season)
    search2 = seasonExp2.search(romajiName)
    if search2 is not None:
        season = max(int(search2.group(1)), season)

    ## create new entry 
    alEntry = anilistEntry(engName)

    ## find synoynms
    synHeader = soup.find('div', {'class': 'type'}, string='Synonyms')
    if synHeader:
        synList = synHeader.parent.find_all('span')
    
        for syn in synList:
            synTitle = syn.text.strip()
            # check if is english characters
            if not synTitle.isascii():
                continue
            # check fuzzy match or romaji
            if fuzz.ratio(synTitle, engName) > 30 or fuzz.ratio(synTitle, romajiName) > 30 or romajiExp.fullmatch(synTitle):
                alEntry.synonyms.append(synTitle)

            # check for season number in synonyms
            search = seasonExp1.search(synTitle)
            if search is not None:
                season = max(int(search.groups()[0]), season)
            search2 = seasonExp2.search(synTitle)
            if search2 is not None:
                season = max(int(search2.groups()[0]), season)

    ## add Romaji as synonym
    ## check if different from English name
    if romajiName != engName:
        alEntry.synonyms.append(romajiName)

    alEntry.seasons[season] = anilistId

    ## recursively find the prequels until the first season
    if getPrequel == True:
        if season > 1:
            ## find link of prequel
            link = soup.find('div', string="Prequel").find_parent('a', {'class': 'cover'}, href=True)['href']
            fullLink = 'https://anilist.co' + link
            ## get prequel entry and append
            newAlEntry = getAniData(url=fullLink, getPrequel=True) 
            newAlEntry.seasons.update(alEntry.seasons)

            return newAlEntry

    ## no prequels
    return alEntry

if __name__ == '__main__':
    url = input('Please input the url of the anilist page you are trying to get:\n')
    print(getAniData(url=url, getPrequel=True))
