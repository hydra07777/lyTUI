<div>
    <img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/python.svg" width="40" />
</div>

# lyTUI

A Terminal User Interface (TUI) music player with synchronized lyrics display, inspired by btop's design.

## Features

- Play MP3 files with Pygame
- Display synchronized lyrics from MP3 metadata (USLT tags)
- Karaoke-style highlighting of current line
- Playlist management
- Modern TUI design with colors

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/lyTUI.git
   cd lyTUI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your MP3 files in the `music/` directory.
2. Run the application:

   ```bash
   python main.py
   ```

3. Use the keyboard shortcuts:
   - `↑↓` : Select song
   - `Enter` : Play selected song
   - `Space` : Play/Pause
   - `Q` : Quit

## Requirements

- Python 3.8+
- MP3 files with synchronized lyrics (USLT tags)

## License

MIT License
