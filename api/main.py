from fastapi import FastAPI, HTTPException, Request, responses, templating
from pydantic import BaseModel
from typing import Optional, List
from service.itunes import search_song_by_title
import os
import pygame

# Inicializar pygame mixer para manejar audio
pygame.mixer.init()

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

# Variable global para rastrear el estado actual
current_song = None

@app.post("/play")
def play_song(song: FavoriteSong):
    """
    Play a song by its preview URL. Stops any currently playing song.
    """
    global current_song_file

    try:
        if not song.preview_url:
            raise HTTPException(status_code=400, detail="Song has no preview URL.")

        # Detener y reiniciar el mixer para asegurarnos de que no se reproduzcan varias canciones
        pygame.mixer.quit()
        pygame.mixer.init()

        # Descargar la canción temporalmente
        response = requests.get(song.preview_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch the song preview.")

        # Eliminar el archivo temporal anterior si existe
        if current_song_file and os.path.exists(current_song_file):
            os.remove(current_song_file)

        # Guardar el archivo temporalmente
        temp_file = "temp_song.mp3"
        with open(temp_file, "wb") as file:
            file.write(response.content)
        current_song_file = temp_file

        # Cargar y reproducir la canción
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        print(f"Now playing: {song.title} by {song.artist}")

        return {"message": f"Playing {song.title} by {song.artist}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
def stop_song():
    """
    Stop the currently playing song.
    """
    global current_song_file

    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("Playback stopped.")
            return {"message": "Playback stopped."}
        else:
            return {"message": "No song is currently playing."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))