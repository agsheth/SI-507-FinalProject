# SI-507-FinalProject

My final project scrapes the top 50 most popular (most favorited by users) films from letterboxd.com. Then using the titles of those top 50 films, I access the Open Movie Database API using API Key provided in secrets.py and return info: (title, year, director, genre, runtime) and ratings: (title, metacritic, rotten tomatoes and imdb rating) from each title. These are stored into two relational databases that can be queried according to user input. 

First, the user chooses a genre of film, then a year. Finally they choose how they want the results to be displayed - by metacritic score, by runtime, by imdb rating or by all 3.

The user is shown a graph of all ratings compared with one another for the 50 films in the selected year and genre. They have to run the program again to input another query. 

Required python packages:<br>
beautifulsoup<br>
sqlite3<br>
plotly<br>

<h2>Code Structure:<h2><br>
1. Scrape list of top 50 most popular films given a genre and year.<br>
2. Crawl into each film on the list and return title of the film.<br>
3. Use OMDB API to find director, runtime, metacritic, rotten tomato and imdb rating of each film according to its title and imdb id.<br>
4. Create database schema and store data into SQLite.<br>
5. Write a query that returns the films and their associated ratings.<br>
6. Display the ratings of each film using plotly according to user inputs.<br>