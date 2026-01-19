from mutagen import File
from mutagen.id3 import APIC
import os

def get_metadata(path: str):
    audio = File(path)
    
    if audio is None:
        return {"title": os.path.basename(path), "album": "Unknown", "artist": "Unknown", "cover": None}

    # Extraction des textes avec gestion des clés multiples
    def get_tag(keys):
        for key in keys:
            if key in audio:
                val = audio[key]
                # Certains tags retournent une liste, d'autres une valeur brute
                if isinstance(val, list) and len(val) > 0:
                    return str(val[0])
                return str(val)
        return "Unknown"

    title = get_tag(['TIT2', 'title', '©nam'])
    artist = get_tag(['TPE1', 'artist', '©ART'])
    album = get_tag(['TALB', 'album', '©alb'])

    cover = None

    # --- LOGIQUE D'EXTRACTION DE COVER ---

    # 1. Cas MP3 (ID3) - On vérifie le type de l'objet directement
    if hasattr(audio, 'tags') and audio.tags is not None:
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                cover = tag.data
                break

    # 2. Cas FLAC / Ogg / Opus
    if cover is None and hasattr(audio, 'pictures') and audio.pictures:
        cover = audio.pictures[0].data

    # 3. Cas M4A / MP4 (Apple)
    if cover is None and 'covr' in audio:
        cover = audio['covr'][0]

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "cover": cover
    }

# Test
