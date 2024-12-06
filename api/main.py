from fastapi import FastAPI, HTTPException, Request, responses, templating
from pydantic import BaseModel
from typing import Optional, List
from service.itunes import search_song_by_title
import os

# Logging the current working directory
print("Current working directory:", os.getcwd())

# FastAPI app instance
app = FastAPI()

# Jinja2 template engine configuration
templates = templating.Jinja2Templates(directory="templates")

# In-memory storage for favorite songs and recently played songs
favorite_songs = []
recently_played = []

# Model for favorite songs
class FavoriteSong(BaseModel):
    title: str
    artist: str
    album: str
    preview_url: Optional[str] = None

@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    """Renders the main index page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
def search(query: str, limit: int = 10):
    """
    Search for songs by title.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        # Restricting search to songs by title
        songs = search_song_by_title(query, limit)
        if not songs:
            raise HTTPException(
                status_code=404, detail=f"No songs found for '{query}'."
            )

        # Update the recently played songs list
        for song in songs[:1]:  # Add the first result to recently played
            recently_played.insert(0, {
                "title": song.name,
                "artist": song.artist,
                "album": song.album,
                "preview_url": song.preview_url
            })

        # Keep only the last 5 recently played songs
        recently_played[:] = recently_played[:5]

        return {"type": "song", "songs": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while searching.")

@app.post("/favorites")
def add_to_favorites(song: FavoriteSong):
    """
    Adds a song to the favorites list.
    """
    if any(
        fav["title"] == song.title and fav["artist"] == song.artist
        for fav in favorite_songs
    ):
        raise HTTPException(status_code=400, detail="Song is already in favorites.")
    favorite_songs.append(song.dict())
    return {"message": "Song added to favorites", "favorites": favorite_songs}

@app.get("/favorites")
def get_favorites():
    """
    Returns the list of favorite songs.
    """
    return {"favorites": favorite_songs}

@app.get("/recently-played")
def get_recently_played():
    """
    Returns the list of recently played songs.
    """
    return {"recently_played": recently_played}
