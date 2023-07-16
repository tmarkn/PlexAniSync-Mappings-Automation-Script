import requests

import getAni

VALIDSEASONS = {
    0: 'WINTER',
    1: 'SPRING',
    2: 'SUMMER',
    3: 'FALL'
}

def getAniSeasonData(year: int, season: str) -> list:
    url = 'https://graphql.anilist.co/'
    query = '''
    query q($season: MediaSeason!, $year: Int){
        Page(page: 1, perPage: 500) {
            media(season: $season, seasonYear: $year, type: ANIME, format: TV) {
                id
                title {
                    romaji
                    english
                }
            }
        }
    }'''
    variables = {'season': season, 'year': year}

    resp = requests.post(url=url, json={"query": query, 'variables': variables})
    if resp.status_code == 200:
        data = resp.json()['data']['Page']['media']
    else:
        raise Exception(f'{resp.status_code}: {resp.reason}')

    ## get each anilist entry
    entries = []
    for entry in data:
        id = entry['id']
        entries.append(id)
    
    print(entries)
    ## too many requests ## split into seperate queries
    first = entries[:len(entries)//2]
    second = entries[len(entries)//2:]
    final = getAni.getAniData(first, getPrequels=True) + getAni.getAniData(second, getPrequels=True)
    ## sort by English title
    finalSorted = sorted(final, key=lambda x: (x.title.casefold(), x.title))
    return finalSorted


if __name__ == '__main__':
    year = None
    while year == None:
        yearIn = input('Please input a year of anime you want (ie. 2023)\n')
        try:
            year = int(yearIn)
        except ValueError:
            print('Please input a number')
            continue

    seasonNum = None
    while seasonNum == None:
        print('Please select a season of anime (0-3):')
        for s in VALIDSEASONS:
            print(f' - {s}: {VALIDSEASONS[s]}')

        seasonIn = input()
        try:
            seasonIn = int(seasonIn)
        except ValueError:
            print('Please input a number')
            continue

        if seasonIn in VALIDSEASONS:
            seasonNum = int(seasonIn)

    ## run script
    anilist = getAniSeasonData(year=year, season=VALIDSEASONS[seasonNum])

    ## export output
    output = 'entries:\n'
    output += ''.join([str(a) for a in anilist])
    print(output)
    ## write to file
    with open(f'yamlFiles/{year}-{seasonNum}-{VALIDSEASONS[seasonNum]}-Anime.yaml', 'w', encoding='utf-8') as f:
        f.write(output)
    
    exit(1)