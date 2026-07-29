from mutagen.id3 import ID3, USLT


def write_lyrics_to_file(path: str, lyrics_text: str, lang: str = "eng"):
    audio = ID3(path)
    audio.delall("USLT")
    audio.add(USLT(encoding=3, lang=lang, desc="", text=lyrics_text))
    audio.save()
