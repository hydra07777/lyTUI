from textual.app import App
from player import PlayerState
from audio.audio import AudioEngine
from counter import Counter
from textual.widgets import Label, ListView, ListItem, Static
from widgets.option import Option
from widgets.lyHeader import LyHeader
from textual.containers import Horizontal, Vertical
from widgets.musicViews import MusicView
from widgets.ResultsPanel import ResultsPanel
from messages.LibrarySelection import LibrarySelection
from audio.MusicLoader import MusicLoader
from textual import on



class lyTUI(App):

    BINDINGS = [
        ("p", "play", "play"),
        ("m", "pause", "pause"),
        ("s", "stop", "stop")
    ]

    CSS = """
        Option {
            width: 20;
            margin-top: 2;
        }
        LyHeader{
            align: center middle;
            height: 3;
            background: red
        }
        ResultsPanel {
            background: green;
            width: 20;
        }
    """

    def compose(self):
        self.results = ResultsPanel()
        yield LyHeader("lyTUI")
        yield Static('test', id='test')
        with Horizontal():
            yield Option(id="option")
            yield self.results
            

    def on_mount(self):
        self.state = PlayerState()
        self.audio = AudioEngine()
        self.biblio = MusicLoader()
        self.biblio.load_music_from_dir(".")
        self.query_one("#test").update(f'{self.biblio.musics}')

        
    @on(LibrarySelection)
    def on_library_selection(self, event: LibrarySelection):
        results = []
        if event.id  == "all" :
            self.biblio.musics
            self.log(self.biblio.musics)
            self.query_one("#test").update(f'{self.biblio.musics}')
        
        self.results.show_results("all", self.biblio.musics)
    
    

lyTUI().run()