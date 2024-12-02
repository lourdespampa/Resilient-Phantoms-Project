from dataclasses import dataclass

@dataclass
class Track:
    name: str              
    disc: int              
    number: int            
    time_millis: int      
    preview_url: str | None = None  

    def to_dict(self):
        return {
            "name": self.name,           
            "disc": self.disc,
            "number": self.number,
            "time_millis": self.time_millis,
            "preview_url": self.preview_url,
        }

