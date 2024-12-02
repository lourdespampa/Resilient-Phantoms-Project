class Song:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

class User:
    def __init__(self, name):
        self.name = name
        self.favorites = []

    def add_favorite(self, song):
        self.favorites.append(song)

    def view_favorites(self):
        return self.favorites