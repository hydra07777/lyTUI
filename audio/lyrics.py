from mutagen.id3 import ID3

def parse_lrc_text(text):
    import re
    pattern = re.compile(r"\[(\d+):(\d+\.\d+)\](.*)")
    lines = []
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            m, s, lyric = m.groups()
            time_sec = int(m) * 60 + float(s)
            lines.append((time_sec, lyric.strip()))
    return lines

def load_lrc_from_mp3(path):
    """
    Retourne un dict : {lang: [(time_sec, line), ...]}
    Toujours un dict, jamais une liste vide.
    """
    audio = ID3(path)
    lyrics_dict = {}

    for tag in audio.getall("USLT"):
        lang = tag.lang or "XXX"
        lines = parse_lrc_text(tag.text)
        lyrics_dict[lang] = lines

    # Si aucun USLT, renvoyer une clé vide pour ne pas planter LyricsView
    if not lyrics_dict:
        lyrics_dict["XXX"] = []

    return lyrics_dict
