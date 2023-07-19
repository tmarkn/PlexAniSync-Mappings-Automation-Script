import os
import yaml

from getAni import AnilistEntry, SeasonEntry

def mergeYaml(directory: str) -> None:
    ## read all yaml files
    yamlList = []
    for filename in os.listdir(directory):
        if filename.endswith('.yaml'):
            f = os.path.join(directory, filename)
            with open(f, 'r', encoding='utf-8') as file:
                yamlList.append(yaml.safe_load(file))

    ## process entries
    anilistEntries = {}

    for yamlObj in yamlList:
        entries = yamlObj['entries']
        for entry in entries:
            ## get id
            baseId = entry['seasons'][0]['anilist-id']
            print(baseId)
            ## seasons
            newSeasons = {}
            for season in entry['seasons']:
                ## look for start value
                start = 1
                if 'start' in season:
                    start = season['start']
                ## make new season entry
                seaEntry = SeasonEntry(season['anilist-id'], season['season'], start=start)
                ## add to season dictionary
                ## dictionary entry uses (seasonNum, anilist-id) as the key
                ## this is for anilist entries that span multiple seasons as one
                newSeasons[(season['season'], season['anilist-id'])] = seaEntry
            
            ## already exists
            if baseId in anilistEntries:
                ## synonyms
                if 'synonyms' in entry:
                    anilistEntries[baseId].synonyms |= set(entry['synonyms'])
                ## combine synonyms
                anilistEntries[baseId].synonyms.add(entry['title'])
                ## add seasons
                anilistEntries[baseId].seasons |= newSeasons
            ## doesn't exist ## create entry
            else:
                ## synonymns
                newEntry = AnilistEntry(entry['title'])
                if 'synonyms' in entry:
                    newEntry.synonyms = set(entry['synonyms'])
                ## add seasons
                newEntry.seasons = newSeasons
                anilistEntries[baseId] = newEntry

    anilist = []
    ## sort seasons of titles
    for title in anilistEntries:
        alEntry = anilistEntries[title]
        ## discard duplicate title in synonyms
        alEntry.synonyms.discard(alEntry.title)
        ## sort seasons
        newSeasons = {k:v for k, v in sorted(alEntry.seasons.items(), key=lambda x:(x[1].seasonNum, x[1].start, x[1].id))}
        ## replace and append
        alEntry.seasons = newSeasons
        anilist.append(alEntry)

    ## sort entire Titles
    sortedYaml = sorted(anilist, key=lambda x: (x.title.casefold(), x.title))
    return sortedYaml

if __name__ == '__main__':
    while True:
        print('This script takes every yaml file in the ./yamlFiles/ folder and create a custom_mappings.yaml file from those files.')
        print('It is recommended that you name the files by date, with the most recent entries being last.')
        print('WARNING: THIS WILL OVERRIDE YOUR custom_mappings.yaml file in this directory. \nDo you wish to proceed? Y/N')
        resp = input().strip().lower()
        if resp == 'n':
            exit(0)
        elif resp == 'y':
            break

    anilist = mergeYaml('./yamlFiles')

    ## export output
    output = 'entries:\n'
    output += ''.join([str(a) for a in anilist])

    ## write to file
    with open('custom_mappings.yaml', 'w', encoding='utf-8') as f:
        f.write(output)
    
    exit(1)