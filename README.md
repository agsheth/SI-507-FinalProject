# SI-507-FinalProject

My final project scrapes the top 50 most popular (most favorited by users) films from letterboxd.com. Then using the titles of those top 50 films, I access the Open Movie Database API using API Key provided in secrets.py and return info: (title, year, director, genre, runtime) and ratings: (title, metacritic, rotten tomatoes and imdb rating) from each title. These are stored into two relational databases that can be queried according to user input. 

First, the user chooses a genre of film, then a year. Finally they choose how they want the results to be displayed - by metacritic score, by runtime, by imdb rating or by all 3.

The user is shown a graph of all ratings compared with one another for the 50 films in the selected year and genre. 

Required python packages:
beautifulsoup
sqlite3
plotly