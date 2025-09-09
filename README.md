# Rick Roll LED Controller

Arduino LED controller that syncs to audio. Comes with Rick Roll data pre-loaded, but works with any song.

## What it does

- LED brightness changes based on audio volume
- Rick Roll data already included 
- Python script converts any audio file to Arduino data
- Single LED setup, easy to wire

## Hardware needed

- Arduino Uno
- 1 LED (any color)
- 1 Push button  
- 1 Resistor (220Ω)
- Breadboard + wires

## Setup

### Quick Rick Roll Setup
Just want Rick Roll? Skip the Python stuff:
1. Grab `arduino/audio_led.ino` and `arduino/brightness_data.h`
2. Upload both to your Arduino Uno
3. Follow the wiring guide below
4. Press button and enjoy

### Custom Song Setup

### Step 1: Install Python dependencies
```bash
cd analyzer
pip install -r requirements.txt
```

### Step 2: Audio data
Rick Roll data is already included. To use your own song:
```bash
python audio_analyzer.py your_song.mp3
```

### Step 3: Upload to Arduino
1. If you generated new data, copy `brightness_data.h` into your Arduino sketch folder
2. Open `arduino/audio_led.ino` in Arduino IDE
3. Upload to your Arduino

### Step 4: Wire and test
Press the button to start the sequence.

## Wiring

```
Arduino Pin 9  → LED positive (through 220Ω resistor)
Arduino Pin 10 → Button (other side to ground)
Arduino GND    → LED negative & button
```

## How it works

1. Loads audio file
2. Analyzes volume every 100ms
3. Maps volume to brightness (0-255)
4. Smooths data to prevent flickering
5. Exports as Arduino header file

## Project structure

```
├── analyzer/                 # Python audio analysis tools
│   ├── audio_analyzer.py     # Main script to convert audio
│   └── requirements.txt      # Python dependencies
├── arduino/                  # Arduino code
│   ├── audio_led.ino        # LED controller code
│   └── brightness_data.h    # Pre-loaded with Rick Roll data
└── README.md                # You're reading it!
```

## Files explained

- **`audio_analyzer.py`** - Converts any audio file to LED data
- **`audio_led.ino`** - Arduino code that controls the LED
- **`brightness_data.h`** - LED brightness data (comes pre-loaded with Rick Roll, gets replaced when you analyze new songs)

## License

###Created by NujabesDev

Open source - use it!