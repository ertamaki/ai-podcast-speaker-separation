# AI Podcast Speaker Diarization Tool

A Python-based tool for automated speaker diarization and audio segmentation in AI-generated podcast audio files. This tool processes clean, single-channel audio to identify speaker segments and create organized output files for further analysis.

This tool is specifically designed to process podcasts created with AI platforms like NotebookLM, where speakers typically alternate without overlap, enabling precise temporal segmentation of individual speaker contributions.

## What This Tool Actually Does

This tool leverages the inaSpeechSegmenter library to automatically segment AI-generated podcast audio by speaker through:

- **Voice Activity Detection (VAD)**: Identifies speech vs. non-speech segments
- **Gender-based Speaker Classification**: Distinguishes between male and female voices using acoustic features
- **Temporal Segmentation**: Creates time-stamped speaker segments
- **Multiple Output Formats**: Generates various file formats for different analytical needs

**Important Note**: This tool performs speaker **diarization** (who spoke when) rather than speaker **separation** (isolating mixed voices). It works best with clean, single-channel audio where speakers alternate without significant overlap.

## Key Features

- Automated speaker diarization for clean AI-generated audio
- Voice activity detection with silence/noise filtering
- Gender-based speaker classification (male/female)
- Multiple output formats for different processing needs
- Preservation of original timing and conversational structure
- Batch processing capabilities for multiple episodes
- Optimized for clean AI-generated audio (NotebookLM, etc.)

## Use Cases

- **AI Podcast Analysis**: Segment AI-generated speaker tracks for temporal analysis
- **Audio Organization**: Create speaker-specific audio files from clean recordings
- **Content Analysis**: Generate precise speaker segmentation data with timestamps
- **Research Applications**: Enable speaker-level analysis of conversational data
- **Automated Workflows**: Integrate into larger audio processing pipelines

## Requirements

- Python 3.10-3.12 (Note: Python 3.13 has compatibility issues with some dependencies)
- ffmpeg (system-level installation required)

### Installing ffmpeg

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Install ffmpeg
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html and add to PATH
```

## Installation

```bash
# Create virtual environment (recommended)
python -m venv podcast-env
source podcast-env/bin/activate  # On Windows: podcast-env\Scripts\activate

# Install required packages
pip install inaSpeechSegmenter pandas pydub resampy

# For Python 3.13 users, also install:
pip install pyaudioop
```

## Quick Start

1. **Prepare your audio file**: Place your audio file (supported formats: .wav, .mp3, .m4a, .flac) in the project directory

2. **Update the script**: Edit `podcast_speaker_separation.py` and modify the file path:
   ```python
   audio_file_path = "your_audio_file.wav"
   ```

3. **Run the analysis**:
   ```bash
   python podcast_speaker_separation.py
   ```

## Usage

### Basic Usage
```python
from podcast_speaker_separation import PodcastSpeakerSeparator

# Initialize the diarization tool
separator = PodcastSpeakerSeparator("your_podcast.wav")

# Run complete workflow
results = separator.process_complete_workflow(
    create_concatenated=True,  # Speaker-only audio (no timing gaps)
    create_synchronized=True,  # Timing-preserved audio
    create_stereo=True,        # Stereo mix for comparative listening
    create_archives=False      # Individual segment files
)

# Access individual methods for custom workflows
separator.segment_audio()                    # Just perform diarization
separator.create_synchronized_tracks()       # Just create synchronized tracks
```

## Output Files

The tool generates several output files optimized for different analytical approaches:

- **`segmentation_output.csv`**: Detailed segmentation data with timestamps, speaker labels, and confidence scores
- **`male_voice_concatenated.wav`**: All male speech segments joined sequentially (removes timing gaps)
- **`female_voice_concatenated.wav`**: All female speech segments joined sequentially (removes timing gaps)
- **`male_voice_synced.wav`**: Male speech with silence during female segments (preserves original timing)
- **`female_voice_synced.wav`**: Female speech with silence during male segments (preserves original timing)
- **`stereo_mix.wav`**: Stereo audio with male voice on left channel, female on right channel

### CSV Output Structure

The segmentation CSV contains the following columns:
- **`labels`**: Speaker classification ('male', 'female', 'noEnergy')
- **`start`**: Segment start time in seconds
- **`stop`**: Segment end time in seconds

## When to Use Each Output Format

**For Individual Speaker Analysis**:
- Use concatenated files (`*_concatenated.wav`) when you need pure speaker content without timing gaps

**For Timing-Preserved Analysis**:
- Use synchronized files (`*_synced.wav`) when you need to maintain the original conversational timing and structure
- Use the segmentation CSV for precise timestamp data and automated processing

**For Audio Comparison**:
- Use the stereo mix for side-by-side speaker comparison and quality control

## Technical Details

### Underlying Technology
The tool uses the inaSpeechSegmenter library, which employs:
- **Voice Activity Detection (VAD)**: Identifies speech vs. non-speech segments
- **Gender Classification**: Binary classification using deep neural networks trained on acoustic features
- **Temporal Boundary Detection**: Identifies speaker change points

### Performance Characteristics
- **Processing Speed**: Approximately 2-3x real-time on modern hardware for diarization
- **Memory Usage**: Scales with audio file length; 8GB RAM recommended for files >2 hours
- **Classification Accuracy**: Gender classification performance depends on audio quality and speaker characteristics

### Supported Audio Formats
- **Primary**: WAV (recommended for best quality)
- **Secondary**: MP3, M4A, FLAC, OGG
- Automatic format conversion handled internally

## Integration with R

For users working in R environments, you can call this tool from R:

```r
# Using reticulate
library(reticulate)
py_run_file("podcast_speaker_separation.py")

# Or using system calls
system("python podcast_speaker_separation.py")

# Read results into R for further processing
segmentation_data <- read.csv("segmentation_output.csv")

# Basic analysis example
library(dplyr)
speaker_stats <- segmentation_data %>%
  filter(labels %in% c("male", "female")) %>%
  group_by(labels) %>%
  summarise(
    total_time = sum(stop - start),
    segment_count = n(),
    avg_segment_length = mean(stop - start)
  )
```

## Batch Processing

For processing multiple AI-generated podcast files:

```python
import glob

audio_files = glob.glob("*.wav")
for audio_file in audio_files:
    separator = PodcastSpeakerSeparator(audio_file)
    results = separator.process_complete_workflow()
    print(f"Processed: {audio_file}")
```

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{ai_podcast_speaker_diarization,
  title={AI Podcast Speaker Diarization Tool},
  author={Eduardo Ryo Tamaki and Levente Littvay},
  year={2025},
  url={https://github.com/ertamaki/ai-podcast-speaker-separation},
  note={Python tool for automated speaker diarization in AI-generated podcast audio}
}
```

Also cite the underlying diarization model:

```bibtex
@inproceedings{lavechin2020ina,
  title={End-to-end domain-adversarial voice activity detection},
  author={Lavechin, Marvin and Gill, Marie-Philippe and Bousbib, Ruben and Bredin, Hervé and Garcia-Perera, Leibny Paola},
  booktitle={Proc. Interspeech 2020},
  pages={3685--3689},
  year={2020}
}
```

## Limitations and Considerations

- **Binary Gender Classification**: The model classifies speakers as 'male' or 'female' based on acoustic features, which may not align with actual gender identity or accommodate non-binary speakers
- **Single-Gender Scenarios**: Performance degrades when multiple speakers share similar gender classifications
- **Audio Quality Dependency**: Performance requires clean, high-quality audio; degrades with background noise, overlapping speech, or poor recording conditions
- **Language Limitations**: Trained primarily on English; performance on other languages may vary
- **Two-Speaker Optimization**: Currently optimized for two-speaker scenarios; additional speakers may be misclassified
- **Clean Audio Requirement**: Designed for clean AI-generated audio, not mixed or overlapping speech

## Troubleshooting

When reporting issues, please include:
- Audio file characteristics (duration, format, source platform)
- Error messages and full traceback
- Expected vs. actual behavior
- System information (OS, Python version)

## Contributing

Contributions are welcome! Areas for improvement include:
- Support for additional AI-generated audio platforms
- Performance optimizations for large file processing
- Better handling of multi-speaker scenarios beyond binary gender classification
- Enhanced batch processing capabilities
- Command-line interface improvements
- Docker containerization for deployment

## Acknowledgments

- Built on the [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) library
- Developed for AI-generated podcast processing applications
- Optimized for high-quality AI-generated audio content

## Authors

Eduardo Ryo Tamaki and Levente Littvay  
[eduardo@tamaki.ai](mailto:eduardo@tamaki.ai)

---

**Note**: This tool is optimized for clean AI-generated podcast content and performs speaker diarization rather than source separation. It may require parameter adjustments for other audio sources or overlapping speech scenarios.
