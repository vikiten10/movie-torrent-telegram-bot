# movie-torrent-telegram-bot

A python3 telegram bot to search torrents via name of the movies, This bot does not require any external telegram bot framework.

Place your telegram bot's api in the 'api_token' variable in the 'telegram_functions.py' file.
Place your omdb api in the 'apikey' variable in the 'web_scraping_functions.py' file.
This bot uses 'yts.mx' site to scrape the torrent and requires internet connection, please contain all the three files in the same directory and only run the 'main.py'.

Once the 'main.py' is ran , 2 json files, 1 csv file and 1 directory will be created.
They contain your json responses and movie torrents.

External requesities :
  * telegram bot api
  * omdb api
  * requests module
  * beautifulsoup module
  
Built-in requesities :
  * os module
  * re module
  * json module
  * csv module
  * datetime module
  * dateutil module

P.S : This is my first project , there might be efficient ways to execute processes and some unknown bugs.
