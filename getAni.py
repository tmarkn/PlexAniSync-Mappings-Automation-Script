import re
import requests
import roman

from thefuzz import fuzz
from urllib import parse

anilistExp = re.compile(r'\/?anime\/([0-9]+)', re.IGNORECASE)
seasonExp = re.compile(r'(?:([0-9]+)(?:st|nd|rd|th) Season)|(?:Season ([0-9]+))|(?:Part ([0-9])+)|(?:Cour ([0-9]+))', re.IGNORECASE)
endNumExp = re.compile(r'[a-z0-9 ]+ ((?:(?:[0-9]+)$)|(?:(?=[MDCLXVI])M*(?:C[MD]|D?C{0,3})(?:X[CL]|L?X{0,3})(?:I[XV]|V?I{0,3})$))', re.IGNORECASE)
romajiExp = re.compile(r'([aeiou]|[bkstgzdnhpmr]{1,2}[aeiou]|(?:sh|ch|j|ts|f|y|w|k)(?:y[auo]|[aeiou])|n|\W|[0-9])+', re.IGNORECASE)

MATCH_PERCENTAGE = 30

class SeasonEntry:
    def __init__(self, id: int, seasonNum: int, episodes: int = 0, start: int = 1):
        self.id = id
        self.seasonNum = seasonNum
        self.episodes = episodes
        self.start = start

class AnilistEntry:
    def __init__(self, title: str) -> None:
        self.title = title
        self.synonyms = set()
        self.seasons = {}
    def __repr__(self) -> str:
        ## title
        title = self.title.replace('"', '\\"')
        string = f'  - title: "{title}"\n'
        ## synonyms
        if len(self.synonyms):
            ## sort
            synonyms = sorted(self.synonyms, key=lambda x: (x.casefold(), x))
            ## write string
            string += '    synonyms:\n'
            for syn in synonyms:
                synonym = syn.replace('"', '\\"')
                string += f'      - "{synonym}"\n'
        # seasons
        string += '    seasons:\n'
        for seasonId in self.seasons:
            season = self.seasons[seasonId]
            string += f'      - season: {season.seasonNum}\n'
            string += f'        anilist-id: {season.id}\n'
            if season.start != 1:
                string += f'        start: {season.start}\n'
        
        return string

def first(iterable, func=lambda L: L is not None, **kwargs):
    it = (el for el in iterable if func(el))
    if 'default' in kwargs:
        return next(it, kwargs['default'])
    return next(it) # no default so raise `StopIteration`

def makeEntryFromAnilistData(anilistDict: dict, id: int) -> AnilistEntry:
    season = 1
    endNum = None
    entry = anilistDict[id]
    romajiName = entry['title']['romaji']
    engName = entry['title']['english'] or entry['title']['romaji']

    ## check for season number in title
    search = seasonExp.search(engName)
    if search is not None:
        season = max(int(first(search.groups())), season)
    search = seasonExp.search(romajiName)
    if search is not None:
        season = max(int(first(search.groups())), season)
    ## check for ending number
    search2 = endNumExp.search(engName)
    if search2 is not None:
        try:
            endNum = int(first(search2.groups())) or endNum
        except ValueError:
            ## roman numeral
            endNum = roman.fromRoman(first(search2.groups()).upper()) or endNum
    search2 = endNumExp.search(romajiName)
    if search2 is not None:
        try:
            endNum = int(first(search2.groups())) or endNum
        except ValueError:
            ## roman numeral
            endNum = roman.fromRoman(first(search2.groups()).upper()) or endNum

    if season == 1 and endNum:
        season = endNum

    ## create new entry 
    alEntry = AnilistEntry(engName)

    ## remove unicode ’ (\u2019) and replace with ' apostrophe
    if '’' in engName:
        alEntry.synonyms.add(engName)
        engName = engName.replace('’', "'")
        alEntry.title = engName

    ## find synoynms
    synList = entry['synonyms']

    for syn in synList:
        synTitle = syn.strip()
        # check fuzzy match or romaji (only ascii characters)
        if synTitle.isascii() and (fuzz.ratio(synTitle, engName) > MATCH_PERCENTAGE or fuzz.ratio(synTitle, romajiName) > MATCH_PERCENTAGE or romajiExp.fullmatch(synTitle)):
            alEntry.synonyms.add(synTitle)
        
        # check for season number in synonyms
        search = seasonExp.search(synTitle)
        if search is not None:
            season = max(int(first(search.groups())), season)

    ## remove duplicate
    alEntry.synonyms.discard(engName)

    ## add Romaji as synonym
    ## check if different from English name
    if romajiName != engName:
        alEntry.synonyms.add(romajiName)

    ## number of episodes
    numEpisodes = 0
    if entry['episodes']:
        numEpisodes = int(entry['episodes']) 

    ## add new season
    newSeason = SeasonEntry(id, season, episodes=numEpisodes)
    alEntry.seasons[id] = newSeason

    return alEntry

def getAnilistId(id: str | int) -> int:
    if isinstance(id, int):
        return id
    if id.isnumeric():
        return int(id)
    
    ## check valid link
    parsed_uri = parse.urlparse(id)

    ## check url for anilist.co/anime/######
    if parsed_uri.netloc == 'anilist.co':
        splitPath = parsed_uri.path[1:].split('/')
        if splitPath[0] != 'anime':
            raise Exception(f'provided url does not contain an anime: {id}')
        
        if not splitPath[1].isnumeric():
            raise Exception(f'provided url does not contain an anime entry: {id}')
        
        return int(splitPath[1])
    ## check url for /anime/######/
    anilistExpSearch = anilistExp.search(id)
    if anilistExpSearch is not None:
        return int(anilistExpSearch.group(1))
    raise Exception('provided url is not of anilist.co')

def getAniData(ids: str | int | list, getPrequels: bool = False) -> list:
    anilistIds = []
    ## check valid link
    if isinstance(ids, int) or isinstance(ids, str):
        anilistIds = [getAnilistId(ids)]
    else:
        for seasonId in ids:
            anilistIds.append(getAnilistId(seasonId))

    ## do requests 
    anilistDict = {}
    queue = anilistIds
    while len(queue):
        url = 'https://graphql.anilist.co/'
        q1 = 'query q { '

        for seasonId in queue:
            q1 += f'id{seasonId}: Media(id: {seasonId}) '
            q1 += '''
                {
                    id
                    title {
                        romaji
                        english
                    }
                    episodes
                    format
                    synonyms
                    relations {
                        nodes {
                            id
                            type
                            format
                        } 
                        edges {
                            relationType(version: 2)
                        }
                    }
                }
            '''

        q1 += '}'

        resp = requests.post(url=url, json={'query': q1})
        if resp.status_code != 200:
            raise Exception(f'{resp.status_code}: {resp.reason}')
        
        data = resp.json()['data']
        newDict = {}
        queue = []
        ## fix relations
        for x in data:
            entry = data[x]
            id = entry['id']

            relationNodes = entry['relations']['nodes']
            relationsEdges = entry['relations']['edges']
            newRelations = []
            for relNum in range(len(relationsEdges)):
                newRelations.append(relationNodes[relNum] | relationsEdges[relNum])
            entry['relations'] = newRelations
            newDict[id] = entry

            ## add prequels
            if getPrequels:
                for rel in entry['relations']:
                    # print(rel)
                    if rel['relationType'] == 'PREQUEL':
                        if rel['id'] not in anilistDict:
                            queue.append(rel['id'])
        
        anilistDict |= newDict       

    anis = []

    for id in anilistIds:
        print(id)
        alEntry = makeEntryFromAnilistData(anilistDict, id)

        ## find the prequels until the first season
        if getPrequels == True:
            visited = set()
            currentId = id
            prequelID = None
            while True:
                visited.add(currentId)
                entry = anilistDict[currentId]
                prequelID = None
                ## find link of prequel
                ## search for TV prequel
                for rel in entry['relations']:
                    ## found TV prequel entry
                    if rel['relationType'] == 'PREQUEL' and rel['format'] == 'TV':
                        prequelID = rel['id']
                        break
                ## search for MOVIE prequel
                if not prequelID:
                    for rel in entry['relations']:
                        ## found Movie prequel entry
                        if rel['relationType'] == 'PREQUEL' and (rel['format'] == 'MOVIE' or rel['format'] == 'SPECIAL' or rel['format'] == 'OVA'):
                            prequelID = rel['id']
                            break
                ## get prequel entry and append
                if prequelID:
                    ## prevent circular references
                    if prequelID in visited:
                        break
                    if anilistDict[prequelID]['format'] == "TV":
                        print(prequelID)
                        ## new entry for prequel
                        newAlEntry = makeEntryFromAnilistData(anilistDict, prequelID)
                        newAlEntry.seasons |= alEntry.seasons
                        alEntry = newAlEntry
                    currentId = prequelID
                else:
                    break
        
        ## update season numbers and start numbers
        oldSeasonNum = 0
        previousId = None
        for seasonId in alEntry.seasons:
            if alEntry.seasons[seasonId].seasonNum <= oldSeasonNum:
                ## update season numbers
                alEntry.seasons[seasonId].seasonNum = oldSeasonNum
                ## update start numbers
                alEntry.seasons[seasonId].start = alEntry.seasons[previousId].start + alEntry.seasons[previousId].episodes
            oldSeasonNum = alEntry.seasons[seasonId].seasonNum
            previousId = seasonId

        ## no prequels
        anis.append(alEntry)
    return anis

if __name__ == '__main__':
    ids = []
    print('Please input the ids/urls of the anilist page you are trying to get (one at a time):')
    print('enter an empty string to process request')
    while True:
        idIn = input()
        if idIn.strip() == '':
            break
        ids.append(idIn)
    print(getAniData(ids=ids, getPrequels=True))
    
    exit(1)