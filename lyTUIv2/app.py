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
from messages.MusicSelection import MusicSelection
from widgets.MusicPanel import MusicPanel



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
        self.music_panel = MusicPanel()
        yield LyHeader("lyTUI")
        yield Static('test', id='test')
        with Horizontal():
            yield Option(id="option")
            yield self.results
            yield self.music_panel
            

    def on_mount(self):
        self.state = PlayerState()
        self.audio = AudioEngine()
        self.biblio = MusicLoader()
        self.biblio.load_music_from_dir(".")
        self.set_interval(0.3, self.refresh_ui)
        

        
    @on(LibrarySelection)
    def on_library_selection(self, event: LibrarySelection):
        results = []
        if event.id  == "all" :
            self.biblio.musics
            self.log(self.biblio.musics)
            self.query_one("#test").update(f'{self.biblio.musics}')
        
        self.results.show_results("all" ,self.biblio.musics)

    @on(MusicSelection)
    def on_music_selection( self, event : MusicSelection):
        selected_track = None
        for track in self.biblio.musics :
            if event.id == self.biblio.musics.index(track) :
                selected_track = track
                break
        
        self.music_panel.show_music_selected(selected_track)
        self.state.elapsed_time = 0
        self.state.playing = True
        self.state.song = selected_track.title

    
    def refresh_ui( self) :
        return
    

lyTUI().run()