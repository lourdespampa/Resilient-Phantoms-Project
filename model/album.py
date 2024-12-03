from typing import List
from dataclasses import dataclass, field
from model.track import Track

@dataclass
class Album:
    id: int
    title: str
    image_url: str
    tracks: List[Track] = field(default_factory=list)  # Mutable list of tracks

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url,
            "tracks": [track.to_dict() for track in self.tracks]
        }

