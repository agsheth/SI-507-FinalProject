import requests
import json
from bs4 import BeautifulSoup
from secrets import API_KEY
import sqlite3
import plotly
import plotly.graph_objs as go

OMDB_API = f'http://www.omdbapi.com/?apikey={API_KEY}&'

year = str(input("Enter a Year [1910-2020]: "))
genre = str(input("Enter a Genre [Action, Drama, Comedy etc.]: ")).lower()
sortby = str(input("Display Ratings [Rotten Tomatoes, IMDB Rating, Metacritic Score or All]: ")).lower()

page_url_year_genre = f"https://letterboxd.com/films/ajax/popular/year/{year}/genre/{genre}/size/small/" 

conn = sqlite3.connect("movies.db")
cur = conn.cursor()

CACHE_DICT = {}
CACHE_FILE_NAME = 'cache.json'

def load_cache():
    ''' Opens a cache file if it exists and loads its contents into
    CACHE_DICT.
    If the cache file doesn't exist, it creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache: dict

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_cache_request(url, cache):
    '''Make a request to the Web page using the baseurl and cache
    
    Parameters
    ----------
    baseurl: string
        The URL for the web page
    cache: dictionary
        A dictionary of cached data
    
    Returns
    -------
    str
        the data returned from making the request in a string
    '''
    if url in cache.keys(): 
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

CACHE_DICT = load_cache()
url_text = make_cache_request(page_url_year_genre, CACHE_DICT)
r = requests.get(page_url_year_genre)
soup = BeautifulSoup(r.text, 'html.parser')

### CLASS DEFS ###
class MovieInfo:
    '''a Movie Information class

    Instance Attributes
    -------------------
    title: string
        the title of the movie
    
    year: string
        the year the movie was released

    director: string
        the director of the movie

    genre: string
        the genre of the movie, as provided by the search parameters

    runtime: integer
        the runtime of the film
    '''
    def __init__(self, title="No Title", year=None,
     director=None, genre=genre, runtime=None):
        self.title = title
        self.year = year
        self.director = director
        self.genre = genre
        self.runtime = runtime

    def get_movie_title(self):
        return str(self.title)

    def get_movie_info(self):
        return f'''{self.title}, {self.year}, {self.director}, {self.genre}, {self.runtime}'''

    def get_movie_dict(self):
        movie_dict = {'title': self.title, 'year': self.year, 'director': self.director,
        'genre': self.genre, 'runtime': self.runtime}
        return movie_dict

class MovieRatings:
    '''a Movie Ratings class

    Instance Attributes
    -------------------
    title: string
        the title of the movie
    
    metacritic: string
        the metacritic score of the movie

    tomato: string
        the rotten tomato score of the movie

    imdb: string
        the imdb rating of the movie
    '''
    def __init__(self, title="No Title", metacritic=None, tomato=None, imdb=None):
        self.title = title
        self.metacritic = metacritic
        self.tomato = tomato
        self.imdb = imdb
    
    def get_rating_info(self):
        return f'''{self.title}, {self.metacritic}, {self.tomato}, {self.imdb}'''
    
    def get_movie_info_dict(self):
        movie_dict = {'title': self.title,'metacritic': self.metacritic, 'tomato': self.tomato, 'imdb': self.imdb}
        return movie_dict

### FUNCTIONS ###
def get_title(url):
    '''Scrapes the web page associated with a movie URL and returns the title 
    
    Parameters
    ----------
    url: string
        The URL for the web page
    
    Returns
    -------
    MovieInfo(title): class
        a class instance of MovieInfo with a provided title
    '''
    r = requests.get(url, allow_redirects=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        for tag in soup.find_all('meta'):
            if tag.get('property', None) == 'og:title':
                title = str(tag.get('content', None))[:-7]
    except:
        title = "Title: None Available"
    
    return MovieInfo(title)

def get_imdb_info(title):
    '''Accesses the OMDB API and returns the associated imdb_id
    
    Parameters
    ----------
    title: string
        Title provided by the get_title() function, scraped from webpage. 
    
    Returns
    -------
    imdb_id: string
        the imdb assocaited with the title used to get more detailed information
    '''
    title = title.replace("+", '&')
    if title == "Twelve Monkeys":
        title = "12 Monkeys"
    try:
        params = {'s': title}
        results = requests.get(OMDB_API, params=params).json()
        search_results = results['Search']
        for result in search_results:
            if result['Year'] == year:
                imdb_id = result['imdbID']
                return imdb_id
    except:
        return "Movie Info Not Found"

def format_movie_data(info):
    '''Formats the information from the OMDB API for the MovieInfo Class
    
    Parameters
    ----------
    info: string
        imdb_id associated with the film
    
    Returns
    -------
    MovieInfo(title, year, director, genre, runtime): class
        the MovieInfo class associated with the imdb_id, and the provided data from the returned json in the correct order.  
    '''
    params = {'i': info}
    results = requests.get(OMDB_API, params=params).json()
    try:
        title = results['Title']
    except:
        title = "No Title"
    try:
        year = results['Year']
    except:
        year = None
    try:
        director = results['Director']
    except:
        director = "No Director"
    try:
        runtime = results['Runtime'][:3] 
    except:
        runtime = None 
    return MovieInfo(title, year, director, genre, runtime).get_movie_dict() 

def format_rating_rata(info):
    '''Formats the information from the OMDB API for the MovieRatings Class
    
    Parameters
    ----------
    info: string
        imdb_id associated with the film
    
    Returns
    -------
    MovieRatings(title, metacritic, tomato, imdb): class
        the MovieInfo class associated with the imdb_id, and the provided data from the returned json in the correct order.  
    '''
    params = {'i': info}
    results = requests.get(OMDB_API, params=params).json()
    try:
        title = results['Title']
    except:
        title = "No Title"
    try:
        ratings = results['Ratings']
        vals = []
        for rating in ratings:
            for key, val in rating.items():
                vals.append(val)
    except:
        metacritic = None
        tomato = None
        imdb_rating = None
    try:
        metacritic = vals[5][:2]
    except:
        metacritic = None
    try:
        tomato = vals[3]
        if len(tomato) < 3:
            tomato = vals[3][:1]
        else:
            tomato = vals[3][:2]
    except:
        tomato = None
    try:
        imdb_rating = vals[1][:3]
    except:
        imdb_rating = None
    return MovieRatings(title, metacritic, tomato, imdb_rating).get_movie_info_dict()

def create_info_tables(year, genre):
    '''Creates the info table in SQL 
    
    Parameters
    ----------
    year: string
        The year the table is associated with
    
    genre: string
        The genre the table is associated with
    
    Returns
    -------
    None
    ''' 
    drop_table = f'''
    DROP TABLE IF EXISTS "Film_Info_{year}_{genre}";
    '''
    create_table = f'''
        CREATE TABLE IF NOT EXISTS "Film_Info_{year}_{genre}" (
        "Rank"      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"     TEXT,
        "Year"      TEXT,
        "Director"  TEXT,
        "Genre"     TEXT,
        "Runtime(min)"   INT
        );
    '''
    cur.execute(drop_table)
    cur.execute(create_table)

def create_rating_tables(year, genre): 
    '''Creates the rating table in SQL 
    
    Parameters
    ----------
    year: string
        The year the table is associated with
    
    genre: string
        The genre the table is associated with
    
    Returns
    -------
    None
    '''
    drop_table = f'''
    DROP TABLE IF EXISTS "Film_Ratings_{year}_{genre}";
    '''
    create_table = f'''
        CREATE TABLE IF NOT EXISTS "Film_Ratings_{year}_{genre}" (
        "Rank"      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Title"     TEXT,
        "Metacritic" TEXT,
        "Rotten_Tomato_Rating" TEXT,
        "IMDB_Rating" TEXT 
        );
    '''  
    cur.execute(drop_table)
    cur.execute(create_table)

def create_command_results(year, genre):
    '''Creates the appropriate command for results for the visualization.
    
    Parameters
    ----------
    year: string
        The year the table is associated with
    
    genre: string
        The genre the table is associated with
    
    Returns
    -------
    None
    '''
    connection = sqlite3.connect("movies.db")
    cur = connection.cursor()
    
    command =  f'''
    SELECT Film_Info_{year}_{genre}.Rank, Film_Info_{year}_{genre}.Title, Film_Ratings_{year}_{genre}.Metacritic, Film_Ratings_{year}_{genre}.Rotten_Tomato_Rating, Film_Ratings_{year}_{genre}.IMDB_Rating
    FROM Film_Info_{year}_{genre}
    JOIN Film_Ratings_{year}_{genre} ON
    Film_Ratings_{year}_{genre}.Rank = Film_Info_{year}_{genre}.Rank
    '''
    result = cur.execute(command).fetchall()
    connection.close()

    return result

def load_graph(xvals, yvals):
    '''Creates a bar graph for the associated rating category
    
    Parameters
    ----------
    xvals: list
        A list of strings for the x values
    
    yvlas: list
        A list of strings for the y values
    
    Returns
    -------
    None
    '''
    bar_data = go.Bar(x=xvals, y=yvals)
    fig = go.Figure(data=bar_data)
    fig.update_layout(xaxis_title = "Film Title", yaxis_title = "Rating")
    fig.show() 

def load_na_graph(xvals, y_mc, y_rt, y_im):
    '''Creates a bar graph for all rating categories
    
    Parameters
    ----------
    xvals: list
        A list of strings for the x values
    
    y_mc: list
        A list of strings for the y values
    
    y_rt: list
        A list of strings for the y values
    
    y_im: list
        A list of strings for the y values
    
    Returns
    -------
    None
    '''
    fig = go.Figure(data=[
    go.Bar(name='Metacritic', x=xvals, y=y_mc),
    go.Bar(name='Rotten Tomatoes', x=xvals, y=y_rt),
    go.Bar(name='IMDB', x=xvals, y=y_im)])
    fig.update_layout(xaxis_title = "Film Title", yaxis_title = "Rating")
    fig.show()


###MAIN###
if __name__=="__main__":
    urls = []
    for link in soup.find('ul').find_all('a'):
        urls.append("https://letterboxd.com" + link.get('href'))

    imdb_info = []
    for url in urls[:50]:
        try:
            title = get_title(url).get_movie_title()
            imdb_info.append(get_imdb_info(title))
        except:
            break
        
    database_movie_dicts = []
    for num in imdb_info:
        database_movie_dicts.append(format_movie_data(num))

    database_rating_dicts = []
    for num in imdb_info:
        database_rating_dicts.append(format_rating_rata(num))

    final_movie_list = []
    for item in database_movie_dicts:
        film_list = []
        for key, val in item.items():
            film_list.append(val)
        final_movie_list.append(film_list)

    final_rating_list = []
    for item in database_rating_dicts:
        rating_list = []
        for key, val in item.items():
            rating_list.append(val)
        final_rating_list.append(rating_list)

    create_info_tables(year, genre)
    create_rating_tables(year, genre)

    insert_info_data = f'''
    INSERT INTO "Film_Info_{year}_{genre}"
    VALUES (NULL, ?,?,?,?,?)
    '''

    insert_ratings_data = f'''
    INSERT INTO "Film_Ratings_{year}_{genre}"
    VALUES (NULL, ?,?,?,?)
    '''

    delete_empty_info = f'''
    DELETE FROM Film_Info_{year}_{genre} 
    WHERE Title = "No Title"
    '''

    delete_empty_ratings = f'''
    DELETE FROM Film_Ratings_{year}_{genre} 
    WHERE Title = "No Title"
    '''

    for film in final_movie_list:
        cur.execute(insert_info_data, film)

    for film in final_rating_list:
        cur.execute(insert_ratings_data, film)

    cur.execute(delete_empty_info)
    cur.execute(delete_empty_ratings)
    conn.commit()

    cmd_result = create_command_results(year, genre)

    if sortby == "metacritic score":
        xvals = []
        for item in cmd_result:
            xvals.append(item[1])
        yvals = []
        for item in cmd_result:
            if item[2] == 'None':
                yvals.append(0)
            else:
                try:
                    yvals.append(int(item[2]))
                except:
                    yvals.append(0)
        load_graph(xvals, yvals)

    if sortby == "rotten tomatoes":
        xvals = []
        for item in cmd_result:
            xvals.append(item[1])
        yvals = []
        for item in cmd_result:
            if item[3] == 'None':
                yvals.append(0)
            else:
                try:
                    yvals.append(int(item[3]))
                except:
                    yvals.append(0)    
        load_graph(xvals, yvals)

    if sortby == "imdb rating":
        xvals = []
        for item in cmd_result:
            xvals.append(item[1])  
        yvals = []
        for item in cmd_result:
            if item[4] == 'None':
                yvals.append(0)
            else:
                try:
                    yvals.append(float(item[4]))
                except:
                    yvals.append(0)    
        load_graph(xvals, yvals)

    if sortby == "all":
        xvals = []
        for item in cmd_result:
            xvals.append(item[1])
        y_mc = []
        for item in cmd_result:
            if item[2] == 'None':
                y_mc.append(0)
            else:
                try:
                    y_mc.append(int(item[2]))
                except:
                    y_mc.append(0)
        y_rt = []
        for item in cmd_result:
            if item[3] == 'None':
                y_rt.append(0)
            else:
                try:
                    y_rt.append(int(item[3]))
                except:
                    y_rt.append(0)
        y_im = []
        for item in cmd_result:
            if item[4] == 'None':
                y_im.append(0)
            else:
                try:
                    y_im.append((float(item[4])) * 10)
                except:
                    y_im.append(0)
        
        load_na_graph(xvals, y_mc, y_rt, y_im) 

