import logging
import requests
from model.artist import Artist
from model.album import Album
from model.track import Track
from service.filecache import cache_artist

logger = logging.getLogger(__name__)

# Map album data from iTunes API to Album model
def map_album(data) -> Album:
    return Album(
        id=data.get("collectionId", None),
        title=data.get("collectionName", "Unknown Album"),
        image_url=data.get("artworkUrl100", "")
    )

# Map track data from iTunes API to Track model
def map_track(data) -> Track:
    logger.debug(f"Mapping track data: {data}")  # Debug log
    return Track(
        name=data.get("trackName", "Unidentified Track"),
        disc=data.get("discNumber", 1),
        number=data.get("trackNumber", 1),
        time_millis=data.get("trackTimeMillis", 0),
        preview_url=data.get("previewUrl", None),
        album=data.get("collectionName", "Unknown Album"),
        artist=data.get("artistName", "Unknown Artist")
    )

# Fetch artist and albums from iTunes API
def get_artist(artist_name: str, limit: int) -> Artist:
    params = {
        "term": artist_name,
        "entity": "album",
        "limit": limit
    }
    try:
        res = requests.get("https://itunes.apple.com/search", params=params)
        res.raise_for_status()
        data = res.json()
        albums = data.get("results", [])
        if albums:
            artist_name = albums[0].get("artistName", "Unknown Artist")
        logger.info(f"Loaded {len(albums)} albums for {artist_name} from iTunes")
        return Artist(
            name=artist_name,
            albums=[map_album(album) for album in albums]
        )
    except requests.RequestException as e:
        logger.error(f"Failed to fetch artist '{artist_name}': {e}")
        return Artist(name=artist_name, albums=[])

# Fetch tracks for a specific album
def get_tracks(album: Album) -> None:
    params = {
        "id": album.id,
        "entity": "song"
    }
    try:
        res = requests.get("https://itunes.apple.com/lookup", params=params)
        res.raise_for_status()
        data = res.json()
        tracks = data.get("results", [])[1:]  # Skip the first result (album details)
        logger.info(f"Loaded {len(tracks)} tracks for album '{album.title}' from iTunes")
        album.tracks = [map_track(track) for track in tracks]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch tracks for album '{album.title}': {e}")
        album.tracks = []

# Search for an artist and their albums
@cache_artist
def search_artist(artist_name: str, limit: int) -> Artist:
    artist = get_artist(artist_name, limit)
    for album in artist.albums:
        get_tracks(album)
    return artist

# Search for songs by title
def search_song_by_title(title: str, limit: int = 10) -> list[Track]:
    params = {
        "term": title,
        "entity": "song",
        "limit": limit
    }
    try:
        res = requests.get("https://itunes.apple.com/search", params=params)
        res.raise_for_status()
        data = res.json()
        tracks = data.get("results", [])
        logger.info(f"Loaded {len(tracks)} songs for title '{title}' from iTunes")
        return [map_track(track) for track in tracks]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch songs for title '{title}': {e}")
        return []
