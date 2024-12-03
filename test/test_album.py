from dataclasses import dataclass, field
from typing import List
from model.track import Track  

@dataclass
class Album:
    id: int
    title: str
    image_url: str
    tracks: List[Track] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url,
            "tracks": [track.to_dict() for track in self.tracks]  # Convert each track to dict
        }

    def __str__(self):
        return f"{self.title} - {self.image_url}"
