from textual.app import App
from textual.widgets import Label, Static, ListItem, ListView


class MyApp(App):
    
    def compose(self):
        yield Static('0', id="counter")

        yield ListView(
            ListItem(Label("song 1")),
            ListItem(Label('song 2')),
            ListItem(Label('song 3'))
        )

    def on_mount(self):
        self.counter = 0
        self.selected_song = None
        self.timer = self.set_interval(1, self.trick)
        self.timer.pause()

    def on_list_view_selected(self, event: ListView.Selected ):
        self.selected_song = event.item.query_one(Label).render()
        self.counter = 0
        self.timer.resume()

    def trick(self):
        if not self.selected_song :
            return
        self.counter += 1
        self.query_one("#counter").update(f"{self.selected_song} - {self.counter % 60:2d}")
MyApp().run()