from textual.app import App
from player import PlayerState
from audio.audio import AudioEngine
from counter import Counter
from textual.widgets import Label, ListView, ListItem, Static, Footer, Log
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
from widgets.AudioDeviceModal import AudioDeviceModal
from messages.AudioDeviceSelected import AudioDeviceSelected
from messages.TrackActionsRequested import TrackActionsRequested
from messages.FetchLyricsRequested import FetchLyricsRequested
from messages.LyricsResultSelected import LyricsResultSelected
from widgets.TrackActionsModal import TrackActionsModal
from widgets.LyricsSearchModal import LyricsSearchModal
from widgets.LyricsWarningModal import LyricsWarningModal
from services import lrclib_client
from services.lyrics_writer import write_lyrics_to_file

class lyTUI(App):

    BINDINGS = [
        ("p", "play", "play"),
        ("m", "pause", "pause"),
        ("a", "select_audio", "Sortie Audio")
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
        #modal_container {
            width: 60;
            height: 40%;
            background: $surface;
            border: thick $primary;
            padding: 1;
            align: center middle;
        }

        #modal_title {
            text-align: center;
            width: 100%;
            text-style: bold;
            margin-bottom: 1;
        }

        #device_list {
            border: none;
            background: transparent;
        }
    """

    def _find_track(self, track_id: int):
        for track in self.biblio.musics:
            if track._id == track_id:
                return track
        return None

    def compose(self):
        self.results = ResultsPanel()
        self.music_panel = MusicPanel()
        self.ui_log = Log()
        # yield self.ui_log
        yield LyHeader("lyTUI")
        yield Static('test', id='test')
        with Horizontal() :
            yield Option(id="option")
            yield self.results
            yield self.music_panel
        
        
        yield Footer()

    def on_mount(self):
        self.state = PlayerState()
        self.audio = AudioEngine()
        self.biblio = MusicLoader()
        self.biblio.load_music_from_dir(".")
        self.set_interval(0.1, self.refresh_ui)
        

        
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
        if selected_track :
            self.music_panel.show_music_selected(selected_track)
            self.state.elapsed_time = 0
            self.state.playing = True
            self.state.song = selected_track.title
            
            self.audio.load(selected_track.path)
            self.audio.play()
    
    @on(AudioDeviceSelected)
    def handle_audio_change(self, message: AudioDeviceSelected):
        """Ce gestionnaire s'active quand la modale poste le message."""
        self.audio.set_output_device(message.device_id)
        self.notify(f"Sortie audio mise à jour !")

    def action_select_audio(self):
        devices = self.audio.get_output_devices()
        # On affiche juste la modale, pas besoin de callback ici
        self.push_screen(AudioDeviceModal(devices))

    @on(TrackActionsRequested)
    def on_track_actions_requested(self, event: TrackActionsRequested):
        self.push_screen(TrackActionsModal(event.track_id))

    @on(FetchLyricsRequested)
    def on_fetch_lyrics_requested(self, event: FetchLyricsRequested):
        track = self._find_track(event.track_id)
        if not track:
            return
        self.run_worker(self._fetch_lyrics(track), exclusive=True)

    async def _fetch_lyrics(self, track):
        try:
            results = await lrclib_client.search(track.title, track.artist)
        except Exception:
            self.notify("Erreur lors de la récupération des paroles", severity="error")
            return
        self.push_screen(LyricsSearchModal(results, track._id))

    @on(LyricsResultSelected)
    def on_lyrics_result_selected(self, event: LyricsResultSelected):
        track = self._find_track(event.track_id)
        if not track:
            return

        if event.synced_lyrics:
            self._write_lyrics(track, event.synced_lyrics)
        elif event.plain_lyrics:
            self.push_screen(
                LyricsWarningModal(track._id, event.plain_lyrics, self._write_lyrics_by_id)
            )
        else:
            self.notify("Aucunes paroles disponibles pour ce résultat", severity="warning")

    def _write_lyrics_by_id(self, track_id: int, lyrics_text: str):
        track = self._find_track(track_id)
        if track:
            self._write_lyrics(track, lyrics_text)

    def _write_lyrics(self, track, lyrics_text: str):
        try:
            write_lyrics_to_file(track.path, lyrics_text)
        except Exception:
            self.notify("Erreur lors de l'écriture des paroles", severity="error")
            return

        if self.state.song == track.title:
            self.music_panel.lyrics.load_lyrics_from_path(track.path)

        self.notify("Paroles enregistrées !")

    def refresh_ui( self) :
        
        if not self.state.playing :
            return
        
        self.state.elapsed_time = self.audio.get_time()
        self.music_panel.on_refresh_lyrics(self.state.elapsed_time)
        self.music_panel.update_progress_bar(int(self.state.elapsed_time))
        
    
    def action_play(self):
        if self.state.playing :
            return
        self.state.playing = True
        
        self.audio.un_pause()

    def action_pause(self):
        if not self.state.playing:
            return
        self.state.playing = False
        self.audio.pause()
        self.audio.debug_status()
    
    def action_list(self):
        devices = self.audio.get_output_devices()
        # self.ui_log.write("--- Périphériques Audio Disponibles ---")
        # for d in devices:
        #     self.ui_log.write(f"[{d['id']}] {d['name']}")
        
    def change_device(self, device_id):
        # self.ui_log.write(f"Changement vers le périphérique ID: {device_id}")
        self.audio.set_output_device(device_id)
    
    def log_ui(self, msg):
        self.log(msg)
        self.query_one(Log).write(msg)

    

lyTUI().run()