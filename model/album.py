from typing import List
from dataclasses import dataclass, field

@dataclass
class Track:
    title: str
    artist: str

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
        }

@dataclass
class Album:
    id: int
    title: str
    image_url: str
    tracks: List[Track] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,  # Returning the album's id
            "title": self.title,
            "image_url": self.image_url,
            "tracks": [track.to_dict() for track in self.tracks]
        }
