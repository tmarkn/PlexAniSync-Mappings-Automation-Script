# PlexAniSync-Mappings Automation Script

This is a web-scraping script for [custom-mappings](https://github.com/RickDB/PlexAniSync#custom-anime-mapping "custom-mappings") for the [PlexAniSync](https://github.com/RickDB/PlexAniSync "PlexAniSync") plex addon for [Anilist.co](https://anilist.co). Since there were no other automated tools to create custom mappings, I decided to create my own so I would not need to start from scratch every season.

The script is not 100% accurate with mappings and each mapping may need to be adjusted. This is meant to be a baseline to start from.

The script uses Selenium and BeautifulSoup4 to retrieve info from [Anilist.co](https://anilist.co).

## Requirements

The program has only been tested on Python 3.11.0. Other versions may have varying levels of success.

* Dependencies can be found in requirements.txt.
* install using either ```pip install -U -r requirements.txt``` or ```python -m pip install -U -r requirements.txt```.

## How to use

First, clone the repository with the green button in the top right hand side where it says ```<> Code```. Then install the requirements above.

Single Entry:

* Run the script by using ```python getAni.py``` then follow the prompts.
* The script will automatically retrieve prequels ***seasons*** if it can detect them.
* This can be disabled by setting ```getPrequel=False``` in the main function.

Entire Season:

* Run the script by using ```python getAniSeason.py``` then following the prompts.
* The script will automatically retrieve prequels ***seasons*** if it can detect them.
* This can be disabled by setting ```getPrequel=False``` at the end of ```getAniSeasonData()``` function.

## How to contribute

Recommmendations are welcome, however, I will not be accepting pull requests at the moment. Feel free to add a suggestion by raising an Issue.
