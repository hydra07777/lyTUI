from textual.app import App
from textual.widgets import Header, Static, Button, Footer
from textual.containers import Horizontal

class MyApp(App) :

    BINDINGS = [
        ("q", "quit", "Quitter"),
        ("p", "play", "jouer")
    ]

    CSS = """
        #title {
            color: #ffff00;
            text-align: center;
            padding-top: 2;
        }

        Button {
            margin: 2;
        }

        Horizontal {
            align: center middle;
        }
    """

    def compose(self):
        yield Header()
        yield Static("lyTUI", id="title")

        with Horizontal() :
            yield Button('play', id="play")
            yield Button("pause", id="pause")
            yield Button('Stop', id="stop")
        
        yield Footer()

MyApp().run()