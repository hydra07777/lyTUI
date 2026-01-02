"""
Playlist widget for displaying and selecting MP3 files.
"""

from textual.widgets import ListView, ListItem, Label
import os

class Playlist(ListView):
    """
    ListView widget that loads and displays MP3 files from a directory.

    Allows selection of songs for playback.
    """

    def load_folder(self, folder):
        self.clear()
        for file in sorted(os.listdir(folder)):
            if file.lower().endswith(".mp3"):
                item = ListItem(Label(file))
                item.song = file   # 🔥 on attache la donnée
                self.append(item)
