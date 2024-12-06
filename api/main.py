import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating
from pydantic import BaseModel
from typing import Optional, List
from model.artist import Artist
from service.itunes import search_artist, search_song_by_title

"""
This is the main entry point for the application.  

Features:
- Searching songs by title.
- Searching albums or songs by artist.
- Adding songs to a favorites list.
- Displaying favorite songs on a separate page or section.

Here we configure app-level services and routes, 
like logging and the template engine used to render the HTML pages.
"""

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(name)s - %(message)s')

# Jinja2 template engine
templates = templating.Jinja2Templates(directory="templates")

# FastAPI app
app = FastAPI()

# In-memory storage for favorite songs
favorite_songs = []

# Model for favorite songs
class FavoriteSong(BaseModel):
    title: str
    artist: str
    album: str
    preview_url: Optional[str] = None

# Home route
@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Search albums or songs by artist
@app.get("/artist/{name}")
def get_artist(name: str):
    if match := re.search(r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()):
        artist_name = " ".join(match.groups())
        artist = search_artist(artist_name, 3)
        return artist
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid artist name: {name}"
        )

# Search songs by title
@app.get("/song/{title}")
def search_song(title: str, limit: int = 10):
    try:
        songs = search_song_by_title(title, limit)
        if not songs:
            raise HTTPException(
                status_code=404, detail=f"No songs found for title '{title}'."
            )
        return {"songs": songs}
    except Exception as e:
        logging.error(f"Error searching for songs: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while searching for songs."
        )

# Add a song to favorites
@app.post("/favorites")
def add_to_favorites(song: FavoriteSong):
    if any(
        fav["title"] == song.title and fav["artist"] == song.artist
        for fav in favorite_songs
    ):
        raise HTTPException(status_code=400, detail="Song is already in favorites.")
    favorite_songs.append(song.dict())
    return {"message": "Song added to favorites", "favorites": favorite_songs}

# Get favorite songs
@app.get("/favorites")
def get_favorites():
    return {"favorites": favorite_songs}

