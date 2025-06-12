# AI Podcast Speaker Separation Tool

A Python-based tool for automated speaker separation and voice activity detection in AI-generated podcast audio files. This tool is specifically designed to process podcasts created with AI platforms like NotebookLM, enabling precise separation of individual speaker tracks.

## Overview

This tool leverages deep learning models to automatically segment AI-generated podcast audio by speaker, creating clean, separated audio tracks for each voice. The tool is optimized for processing high-quality AI-generated content where speaker separation and individual track extraction are required.

**Key Features:**
- Automated speaker detection and classification for AI-generated voices
- Voice activity detection with silence/noise filtering  
- Multiple output formats for different processing needs
- Preservation of original timing and conversational structure
- Batch processing capabilities for multiple AI-generated episodes
- Optimized for clean AI-generated audio (NotebookLM, etc.)

## Use Cases

- **AI Podcast Processing**: Clean separation of AI-generated speaker tracks from platforms like NotebookLM
- **Audio Post-Processing**: Extract individual speaker channels for further audio manipulation
- **Content Modification**: Enable speaker-specific audio processing and enhancement
- **Technical Audio Analysis**: Generate precise speaker segmentation data with timestamps
- **Automated Workflows**: Integrate into larger audio processing pipelines

## Installation

### Prerequisites

- Python 3.10-3.12 (Note: Python 3.13 has compatibility issues with some dependencies)
- ffmpeg (system-level installation required)

### System Dependencies

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

### Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv podcast-env
source podcast-env/bin/activate  # On Windows: podcast-env\Scripts\activate

# Install required packages
pip install inaSpeechSegmenter pandas pydub resampy

# For Python 3.13 users, also install:
pip install pyaudioop
```

## Usage

### Basic Usage

1. **Prepare your audio file**: Place your audio file (supported formats: .wav, .mp3, .m4a, .flac) in the project directory

2. **Update the script**: Edit `podcast_speaker_separation.py` and modify the file path:
   ```python
   audio_file_path = "your_audio_file.wav"
   ```

3. **Run the analysis**:
   ```bash
   python podcast_speaker_separation.py
   ```

### Advanced Usage

```python
from podcast_speaker_separation import PodcastSpeakerSeparator

# Initialize the separator
separator = PodcastSpeakerSeparator("your_podcast.wav")

# Run complete workflow
results = separator.process_complete_workflow(
    create_concatenated=True,    # Speaker-only audio (no timing)
    create_synchronized=True,    # Timing-preserved audio
    create_stereo=True,         # Stereo mix for comparative listening
    create_archives=False       # Individual segment files
)

# Access individual methods for custom workflows
separator.segment_audio()  # Just perform segmentation
separator.create_synchronized_tracks()  # Just create synchronized tracks
```

## Output Files

The tool generates several output files optimized for different analytical approaches:

### Core Outputs

- **`segmentation_output.csv`**: Detailed segmentation data with timestamps, speaker labels, and confidence scores
- **`male_voice_concatenated.wav`**: All male speech segments joined sequentially (removes timing gaps)
- **`female_voice_concatenated.wav`**: All female speech segments joined sequentially (removes timing gaps)
- **`male_voice_synced.wav`**: Male speech with silence during female segments (preserves original timing)
- **`female_voice_synced.wav`**: Female speech with silence during male segments (preserves original timing)
- **`stereo_mix.wav`**: Stereo audio with male voice on left channel, female on right channel

### Segmentation Data Structure

The CSV output contains the following columns:
- `labels`: Speaker classification ('male', 'female', 'noEnergy')
- `start`: Segment start time in seconds
- `stop`: Segment end time in seconds

### Choosing the Right Output

**For Individual Speaker Processing:**
- Use concatenated files (`*_concatenated.wav`) when you need pure speaker content without timing gaps

**For Timing-Preserved Processing:**
- Use synchronized files (`*_synced.wav`) when you need to maintain the original conversational timing and structure
- Use the segmentation CSV for precise timestamp data and automated processing

**For Audio Comparison:**
- Use the stereo mix for side-by-side speaker comparison and quality control

## Technical Details

### Speaker Segmentation Model

The tool uses the inaSpeechSegmenter library, which employs:
- **Voice Activity Detection (VAD)**: Identifies speech vs. non-speech segments
- **Speaker Classification**: Gender-based classification using deep neural networks
- **Segmentation**: Temporal boundary detection for speaker changes

### Performance Considerations

- **Processing Speed**: Approximately 2-3x real-time on modern hardware
- **Memory Usage**: Scales with audio file length; 8GB RAM recommended for files >2 hours
- **Accuracy**: Gender classification accuracy >95% on clean audio; performance may vary with poor audio quality

### Supported Audio Formats

- Primary: WAV (recommended for best quality)
- Secondary: MP3, M4A, FLAC, OGG
- Automatic format conversion handled internally

## Technical Integration

### Integration with R

For users working in R environments, you can call this tool from R:

```r
# Using reticulate
library(reticulate)
py_run_file("podcast_speaker_separation.py")

# Or using system calls
system("python podcast_speaker_separation.py")

# Read results into R for further processing
segmentation_data <- read.csv("segmentation_output.csv")
```

### Batch Processing

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

If you use this tool in your work, please cite:

```bibtex
@software{ai_podcast_speaker_separation,
  title={AI Podcast Speaker Separation Tool},
  author={Eduardo Ryo Tamaki and Levente Littvay},
  year={2025},
  url={https://github.com/ertamaki/ai-podcast-speaker-separation},
  note={Python tool for automated speaker separation in AI-generated podcast audio}
}
```

Also cite the underlying segmentation model:
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

- **Gender Classification**: The model classifies speakers as 'male' or 'female' based on acoustic features, which may not align with gender identity
- **Multiple Speakers**: Currently optimized for two-speaker scenarios; additional speakers may be misclassified
- **Audio Quality**: Performance degrades with poor audio quality, background noise, or overlapping speech
- **Language**: Trained primarily on English; performance on other languages may vary

## Contributing

Contributions are welcome! Please consider the following:

### Technical Contributions
- Support for additional AI-generated audio platforms
- Performance optimizations for large file processing
- Integration with additional speaker identification models
- Better handling of overlapping speech in AI-generated content
- Support for additional audio formats and codecs

### Feature Requests
- Enhanced batch processing capabilities
- Integration with popular audio processing libraries
- Command-line interface improvements
- Docker containerization for deployment

### Submitting Issues
Please include:
- Audio file characteristics (duration, format, source platform)
- Error messages and full traceback
- Expected vs. actual behavior
- System information (OS, Python version)

## License

[Choose appropriate license - MIT, GPL, Apache 2.0, etc.]

## Acknowledgments

- Built on the [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) library
- Developed for AI-generated podcast processing applications
- Optimized for high-quality AI-generated audio content

## Contact

Eduardo Ryo Tamaki and Levente Littvay  
eduardo@tamaki.ai  

---

**Note**: This tool is optimized for AI-generated podcast content and may require parameter adjustments for other audio sources.
