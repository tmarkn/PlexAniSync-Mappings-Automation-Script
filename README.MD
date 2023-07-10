# PlexAniSync-Mappings Automation Script

This is a web-scraping script for [custom-mappings](https://github.com/RickDB/PlexAniSync#custom-anime-mapping "custom-mappings") for the [PlexAniSync](https://github.com/RickDB/PlexAniSync "PlexAniSync") plex addon for [Anilist.co](https://anilist.co). Since there were no other automated tools to create custom mappings, I decided to create my own so I would not need to start from scratch every season.

The script is not 100% accurate with mappings and each mapping may need to be adjusted. This is meant to be a baseline to start from.

The script uses the [Anilist.co](https://anilist.co) API. [API Documentation can be found here.](https://anilist.gitbook.io/anilist-apiv2-docs/)

## Requirements

The program has only been tested on Python 3.11.0. Other versions may have varying levels of success.

* Dependencies can be found in requirements.txt.
* install using either ```pip install -U -r requirements.txt``` or ```python -m pip install -U -r requirements.txt```.

## How to use

### Running manually

First, clone the repository with the green button in the top right hand side where it says ```<> Code```. Then install the requirements above.

Single Entry:

* Run the script by using ```python getAni.py``` then follow the prompts.
* The script will automatically retrieve prequels ***seasons*** if it can detect them.
* This can be disabled by setting ```getPrequel=False``` in the main function.

Entire Season:

* Run the script by using ```python getAniSeason.py``` then following the prompts.
* The script will automatically retrieve prequels ***seasons*** if it can detect them.
* This can be disabled by setting ```getPrequel=False``` at the end of ```getAniSeasonData()``` function.

### Importing

For full information, [read this section](https://github.com/RickDB/PlexAniSync#community-mappings).

Example `custom_mappings.yaml` with [The Movie Database](https://www.themoviedb.org/), which is the default provider using the built-in Plex agent:

```yaml notranslate position-relative overflow-auto
remote-urls:
  - https://raw.githubusercontent.com/tmarkn/PlexAniSync-Mappings-Automation-Script/main/yaml/2023-0-WINTER-Anime.yaml
  - https://raw.githubusercontent.com/tmarkn/PlexAniSync-Mappings-Automation-Script/main/yaml/2023-1-SPRING-Anime.yaml
  - https://raw.githubusercontent.com/tmarkn/PlexAniSync-Mappings-Automation-Script/main/yaml/2023-2-SUMMER-Anime.yaml
```


## How to contribute

Recommmendations are welcome, however, I will not be accepting pull requests at the moment. Feel free to add a suggestion by raising an Issue.
