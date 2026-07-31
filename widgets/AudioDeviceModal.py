from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical
from textual.widgets.option_list import Option
from messages.AudioDeviceSelected import AudioDeviceSelected # Import du message

class AudioDeviceModal(ModalScreen):
    BINDINGS = [
        ("escape", "dismiss", "Fermer"),
    ]

    def __init__(self, devices):
        super().__init__()
        self.devices = devices

    def compose(self):
        options = [Option(d['name'], id=str(d['id'])) for d in self.devices]
        options.append(Option("Fermer", id="close"))
        with Vertical(id="modal_container"):
            yield Label("🔊 Sortie Audio", id="modal_title")
            yield OptionList(*options, id="device_list")

    def on_option_list_option_selected(self, event):
        if event.option.id == "close":
            self.dismiss()
            return
        # On envoie le message à l'application parente
        device_id = int(event.option.id)
        self.post_message(AudioDeviceSelected(device_id))
        # On ferme la modale
        self.dismiss()