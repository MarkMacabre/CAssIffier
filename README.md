# CAssIffier

**CAssIffier** is a local, offline, cross-platform audio sample organization system that scans chaotic audio sample folders and reorganizes them into a clean, unified library categorized by sound type, sub-type, and genre.

## Features

- 🎯 **Hybrid Classification**: Rule-based + ML for accurate categorization
- 🔍 **Context-Aware**: Uses folder names and filenames as classification hints
- 🎵 **Genre Detection**: Automatic genre detection for drums and bass
- 🔐 **Duplicate Detection**: SHA-256 hash-based duplicate detection
- 📊 **Confidence Scoring**: Low-confidence samples flagged for review
- 💾 **SQLite Database**: Track all files, classifications, and history
- ⚡ **Incremental Processing**: Skip already-processed files
- 🎓 **ML Training**: Train custom models on your own samples

## Supported Formats

- WAV
- MP3

## Platform Support

- Linux
- Windows
- macOS (not explicitly tested but should work)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Install from source

```bash
git clone https://github.com/MarkMacabre/CAssIffier.git
cd CAssIffier
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Usage

### Basic Usage

Organize audio samples from a directory:

```bash
python -m cassiffier.main /path/to/samples -o organized_library
```

Or if installed:

```bash
cassiffier /path/to/samples -o organized_library
```

### Incremental Mode

Only process new files not already in the database:

```bash
cassiffier /path/to/samples -o organized_library --incremental
```

### Create Library Structure

Create the empty folder structure without processing files:

```bash
cassiffier --create-structure -o organized_library
```

### Verbose Mode

Enable detailed logging:

```bash
cassiffier /path/to/samples -o organized_library -v
```

### Custom Configuration

Use a custom configuration file:

```bash
cassiffier /path/to/samples -o organized_library -c config.json
```

Example configuration file:

```json
{
  "confidence_threshold": 0.7,
  "max_duration": 30.0,
  "min_duration": 0.01,
  "use_ml_classifier": true,
  "ml_model_path": "models/classifier.joblib",
  "database_path": "cassiffier.db",
  "review_folder_name": "⚠_Review",
  "scan_extensions": [".wav", ".mp3"],
  "enable_genre_detection": true,
  "genre_confidence_threshold": 0.6,
  "duplicate_action": "ask"
}
```

## Output Structure

CAssIffier organizes samples into this structure:

```
organized_library/
├── Drums/
│   ├── Kicks/
│   ├── Snares/
│   ├── Claps/
│   ├── HiHats/
│   ├── Cymbals/
│   └── Percussion/
├── Bass/
│   ├── Synth/
│   ├── Acoustic/
│   └── 808/
├── Synths/
│   ├── Leads/
│   ├── Pads/
│   ├── Plucks/
│   └── Arps/
├── Instruments/
│   ├── Piano/
│   ├── Guitar/
│   ├── Strings/
│   └── Brass/
├── FX/
├── Vocals/
├── Unknown/
└── ⚠_Review/
```

For genre-aware categories (Drums, Bass), samples may be further organized by genre:

```
Drums/
├── Techno/
│   ├── Kicks/
│   └── Snares/
├── Hip-Hop/
│   ├── Kicks/
│   └── Snares/
```

## Training Custom Models

CAssIffier can learn from your manually organized samples to improve classification accuracy.

### 1. Organize Training Samples

Create a directory with samples organized by category and subcategory:

```
data/training/
├── Drums/
│   ├── Kicks/
│   │   ├── kick1.wav
│   │   └── kick2.wav
│   └── Snares/
│       ├── snare1.wav
│       └── snare2.wav
├── Bass/
│   ├── 808/
│   │   └── 808_bass.wav
│   └── Synth/
│       └── synth_bass.wav
└── ...
```

### 2. Train the Model

```bash
python train_model.py data/training -o models/classifier.joblib
```

### 3. Use the Trained Model

The model will automatically be loaded if it exists at the configured path (default: `models/classifier.joblib`).

## Duplicate Detection

When a duplicate is detected, you'll be prompted:

```
⚠️  Duplicate file detected!
  Original: /path/to/original.wav
  New:      /path/to/duplicate.wav

What would you like to do?
  [s] Skip this file
  [k] Keep both files
  [d] Delete duplicate
  [a] Skip all future duplicates

Your choice:
```

You can also set a default action in the configuration file with `duplicate_action`.

## Low Confidence Review

Samples classified with confidence below the threshold (default: 0.7) are:
1. Placed in the predicted category
2. **Also** copied to the `⚠_Review/` folder

This allows you to verify classifications before committing to the organization.

## Design Principles

- **Determinism over cleverness**: Predictable, reproducible results
- **Transparency over automation**: Clear logging and user control
- **Trust over magic**: No hidden behaviors or "smart" features
- **Local-first**: No cloud dependencies, all processing offline

## Architecture

```
cassiffier/
├── main.py          - CLI entry point
├── scanner.py       - Filesystem scanning
├── hasher.py        - SHA-256 hashing & duplicate detection
├── features.py      - Audio feature extraction (librosa)
├── context.py       - Folder/filename context parsing
├── classifier.py    - Hybrid rule-based + ML classification
├── organizer.py     - File organization & moving
├── database.py      - SQLite persistence
├── config.py        - Configuration management
├── categories.py    - Category definitions
└── training.py      - ML model training utilities
```

## Database Schema

CAssIffier uses SQLite to track all files:

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    file_hash TEXT UNIQUE,
    original_path TEXT,
    organized_path TEXT,
    category TEXT,
    subcategory TEXT,
    genre TEXT,
    confidence REAL,
    features TEXT,
    timestamp TEXT,
    status TEXT
);
```

## Troubleshooting

### librosa not available

If you see "librosa not available", install dependencies:

```bash
pip install librosa soundfile
```

### Feature extraction fails

Some audio files may be corrupted or in unsupported formats. These are automatically skipped with error messages.

### ML model not found

If no ML model exists, CAssIffier falls back to rule-based classification only. Train a model to improve accuracy.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [librosa](https://librosa.org/) for audio analysis
- Uses [scikit-learn](https://scikit-learn.org/) for machine learning
- Inspired by the chaos of sample pack management