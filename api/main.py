import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating
from model.artist import Artist
from service.itunes import search_artist  # Assuming search_artist is synchronous

"""
This is the main entry point for the application.

Here we configure app-level services and routes, 
like logging and the template engine used to render the HTML pages.
"""

# Configure logging to show info level and above to the console, using our custom format
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(name)s - %(message)s')

# Configure the Jinja2 template engine
templates = templating.Jinja2Templates(directory="templates")

# Configure the FastAPI app to serve the API and the home page
app = FastAPI()

# Serves the home page at / using the Jinja2 template engine
@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API route to get a list of albums for an artist
@app.get("/artist/{name}")
def get_artist(name: str):  # This function is now synchronous
    if match := re.search(r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()):
        artist_name = " ".join(match.groups())
        artist = search_artist(artist_name, 3)  # Call search_artist synchronously
        return artist
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid artist name: {name}"
        )

# API route to get a list of albums for a genre
@app.get("/genre/{genre}")
def get_albums_by_genre(genre: str):
    albums = [
        {"title": "Album1", "artist": "Artist1", "genre": "Rock"},
        {"title": "Album2", "artist": "Artist2", "genre": "Pop"},
    ]
    filtered_albums = [album for album in albums if album["genre"] == genre]
    return filtered_albums

# API route to get a list of albums for a year
@app.get("/year/{year}")
def get_albums_by_year(year: int):
    albums = [
        {"title": "Album1", "artist": "Artist1", "year": 2020},
        {"title": "Album2", "artist": "Artist2", "year": 2021},
    ]
    filtered_albums = [album for album in albums if album["year"] == year]
    return filtered_albums

# API route to get a list of albums for a decade
@app.get("/decade/{decade}")
def get_albums_by_decade(decade: int):
    albums = [
        {"title": "Album1", "artist": "Artist1", "year": 2020},
        {"title": "Album2", "artist": "Artist2", "year": 2021},
    ]
    filtered_albums = [album for album in albums if (album["year"] // 10) == (decade // 10)]
    return filtered_albums

# Get a random song 
@app.get("/random-song")
async def get_random_song():
    songs = [
        {"title": "Song1", "artist": "Artist1"},
        {"title": "Song2", "artist": "Artist2"},
        {"title": "Song3", "artist": "Artist3"},
    ]
    import random
    return random.choice(songs)

# Add a favorite song
@app.post("/favorites")
async def add_to_favorites(song: dict):
    favorites = []
    favorites.append(song)
    return {"message": "Song added to favorites"}

# To get a song lyrics
@app.get("/lyrics/{title}")
async def get_lyrics(title: str):
    lyrics = {
        "Song1": "These are the lyrics to Song1",
        "Song2": "These are the lyrics to Song2",
    }
    return lyrics.get(title, "Lyrics not found")

# Search for a song
@app.get("/search/songs")
async def search_songs(title: str):
    songs = [
        {"title": "Song1", "artist": "Artist1"},
        {"title": "Song2", "artist": "Artist2"},
        {"title": "Song3", "artist": "Artist3"},
    ]
    return songs
