"""
Podcast Speaker Separation Tool

This script processes audio files to separate speakers using voice activity detection
and speaker segmentation. It creates separate audio tracks for each identified speaker
while preserving the original timing and structure.

Requirements (install via pip):
- inaSpeechSegmenter
- pandas
- pydub
- resampy (may be required for some audio processing)

System Requirements:
- ffmpeg (install via system package manager)

Author: [Your Name]
Version: 1.0
"""

import os
import subprocess
import glob
import zipfile
from pathlib import Path
import pandas as pd
from pydub import AudioSegment
from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.export_funcs import seg2csv


class PodcastSpeakerSeparator:
    """
    A class to handle podcast speaker separation using inaSpeechSegmenter.
    
    This class provides methods to:
    1. Segment audio by speaker
    2. Extract individual speaker tracks
    3. Create concatenated speaker audio files
    4. Preserve timing with silence between speakers
    """
    
    def __init__(self, audio_file_path):
        """
        Initialize the speaker separator with an audio file.
        
        Args:
            audio_file_path (str): Path to the input audio file
        """
        self.audio_file_path = Path(audio_file_path)
        self.segmenter = None
        self.segments_df = None
        self.audio = None
        
        # Validate input file exists
        if not self.audio_file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    def initialize_segmenter(self):
        """
        Initialize the inaSpeechSegmenter model.
        
        This loads the pre-trained neural network models for:
        - Voice activity detection
        - Gender classification
        - Speaker segmentation
        """
        print("Initializing speech segmenter...")
        self.segmenter = Segmenter()
        print("Segmenter initialized successfully.")
    
    def segment_audio(self, output_csv_path="segmentation_output.csv"):
        """
        Perform speaker segmentation on the audio file.
        
        This process:
        1. Analyzes the audio for voice activity
        2. Classifies speakers by gender (male/female)
        3. Identifies non-speech segments (noEnergy)
        
        Args:
            output_csv_path (str): Path to save segmentation results
            
        Returns:
            pd.DataFrame: DataFrame containing segmentation results
        """
        if self.segmenter is None:
            self.initialize_segmenter()
        
        print(f"Segmenting audio file: {self.audio_file_path}")
        
        # Perform segmentation - this is the core ML inference step
        segmentation = self.segmenter(str(self.audio_file_path))
        
        # Export segmentation results to CSV
        seg2csv(segmentation, output_csv_path)
        print(f"Segmentation results saved to: {output_csv_path}")
        
        # Load and process the CSV file
        self.segments_df = self._process_segmentation_csv(output_csv_path)
        
        return self.segments_df
    
    def _process_segmentation_csv(self, csv_path):
        """
        Process the segmentation CSV file to extract structured data.
        
        The CSV file from inaSpeechSegmenter uses tab-separated values
        in a single column, which needs to be parsed properly.
        
        Args:
            csv_path (str): Path to the segmentation CSV file
            
        Returns:
            pd.DataFrame: Processed segmentation data with separate columns
        """
        # Read the CSV file
        segments_df = pd.read_csv(csv_path)
        
        # Split the tab-delimited column into separate columns
        # Format: labels\tstart\tstop
        segments_df[['labels', 'start', 'stop']] = segments_df['labels\tstart\tstop'].str.split('\t', expand=True)
        
        # Remove the original combined column
        segments_df = segments_df.drop('labels\tstart\tstop', axis=1)
        
        # Convert time columns to float for numerical operations
        segments_df['start'] = segments_df['start'].astype(float)
        segments_df['stop'] = segments_df['stop'].astype(float)
        
        # Display segmentation statistics
        print(f"Segmentation complete:")
        print(f"- Total segments: {len(segments_df)}")
        print(f"- Speaker labels found: {segments_df['labels'].unique()}")
        
        return segments_df
    
    def extract_speaker_segments(self, speaker_label, output_filename):
        """
        Extract and concatenate all segments for a specific speaker.
        
        This method:
        1. Filters segments by speaker label
        2. Extracts each segment using ffmpeg
        3. Concatenates all segments into a single audio file
        
        Args:
            speaker_label (str): Speaker label to extract ('male', 'female', etc.)
            output_filename (str): Output filename for concatenated audio
            
        Returns:
            str: Path to the output file
        """
        if self.segments_df is None:
            raise ValueError("Must run segment_audio() first")
        
        print(f"Extracting segments for speaker: {speaker_label}")
        
        # Filter segments by speaker label
        speaker_segments = self.segments_df[self.segments_df['labels'] == speaker_label]
        
        if speaker_segments.empty:
            print(f"No segments found for speaker: {speaker_label}")
            return None
        
        segment_files = []
        
        # Extract each individual segment
        for idx, row in speaker_segments.iterrows():
            start_time = row['start']
            end_time = row['stop']
            segment_file = f"{speaker_label}_segment_{idx}.wav"
            
            # Use ffmpeg to extract the segment
            # -y: overwrite output files
            # -i: input file
            # -ss: start time
            # -to: end time
            # -c copy: copy without re-encoding (faster)
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output files
                '-i', str(self.audio_file_path),
                '-ss', str(start_time),
                '-to', str(end_time),
                '-c', 'copy',  # Copy streams without re-encoding
                segment_file
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                segment_files.append(segment_file)
            except subprocess.CalledProcessError as e:
                print(f"Error extracting segment {idx}: {e}")
                continue
        
        if not segment_files:
            print(f"No segments successfully extracted for {speaker_label}")
            return None
        
        # Create a file list for ffmpeg concatenation
        list_file = f"{speaker_label}_segments.txt"
        with open(list_file, 'w') as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")
        
        # Concatenate all segments into one file
        cmd_concat = [
            'ffmpeg',
            '-y',
            '-f', 'concat',          # Use concat demuxer
            '-safe', '0',            # Allow unsafe file names
            '-i', list_file,         # Input file list
            '-c', 'copy',            # Copy without re-encoding
            output_filename
        ]
        
        try:
            subprocess.run(cmd_concat, check=True, capture_output=True)
            print(f"Successfully created: {output_filename}")
            
            # Clean up temporary files
            self._cleanup_temp_files(segment_files + [list_file])
            
            return output_filename
            
        except subprocess.CalledProcessError as e:
            print(f"Error concatenating segments: {e}")
            return None
    
    def create_stereo_mix(self, male_file, female_file, output_filename="stereo_output.wav"):
        """
        Create a stereo audio file with male voice on one channel and female on the other.
        
        Args:
            male_file (str): Path to male voice audio file
            female_file (str): Path to female voice audio file
            output_filename (str): Output filename for stereo mix
            
        Returns:
            str: Path to the stereo output file
        """
        if not (Path(male_file).exists() and Path(female_file).exists()):
            print("Both male and female audio files must exist to create stereo mix")
            return None
        
        print("Creating stereo mix...")
        
        # Use ffmpeg to create stereo mix
        # -filter_complex: complex audio filter
        # amerge: merge audio streams
        # -ac 2: output 2 channels (stereo)
        cmd = [
            'ffmpeg',
            '-y',
            '-i', male_file,
            '-i', female_file,
            '-filter_complex', '[0:a][1:a]amerge=inputs=2[aout]',
            '-map', '[aout]',
            '-ac', '2',  # 2 channel output
            output_filename
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Stereo mix created: {output_filename}")
            return output_filename
        except subprocess.CalledProcessError as e:
            print(f"Error creating stereo mix: {e}")
            return None
    
    def create_synchronized_tracks(self, male_output="male_voice_synced.wav", 
                                 female_output="female_voice_synced.wav"):
        """
        Create synchronized audio tracks that preserve original timing with silence.
        
        This method maintains the exact timing of the original audio by:
        1. Adding silence where the other speaker is talking
        2. Preserving gaps between speech segments
        3. Ensuring both tracks have the same total duration
        
        Args:
            male_output (str): Output filename for male synchronized track
            female_output (str): Output filename for female synchronized track
            
        Returns:
            tuple: Paths to (male_track, female_track)
        """
        if self.segments_df is None:
            raise ValueError("Must run segment_audio() first")
        
        print("Creating synchronized tracks with preserved timing...")
        
        # Load the original audio file
        self.audio = AudioSegment.from_file(str(self.audio_file_path))
        
        # Initialize empty audio segments with the same properties as the original
        male_audio = AudioSegment.silent(duration=0, frame_rate=self.audio.frame_rate)
        female_audio = AudioSegment.silent(duration=0, frame_rate=self.audio.frame_rate)
        
        current_time_ms = 0
        
        # Process each segment in chronological order
        for idx, row in self.segments_df.iterrows():
            start_ms = int(row['start'] * 1000)  # Convert to milliseconds
            stop_ms = int(row['stop'] * 1000)
            duration_ms = stop_ms - start_ms
            
            # Handle gaps between segments by adding silence
            if start_ms > current_time_ms:
                gap_duration_ms = start_ms - current_time_ms
                silence_segment = AudioSegment.silent(
                    duration=gap_duration_ms, 
                    frame_rate=self.audio.frame_rate
                )
                male_audio += silence_segment
                female_audio += silence_segment
                current_time_ms = start_ms
            
            # Extract the current segment from the original audio
            segment_audio = self.audio[start_ms:stop_ms]
            
            # Add segment to appropriate track and silence to the other
            if row['labels'] == 'male':
                male_audio += segment_audio
                female_audio += AudioSegment.silent(
                    duration=duration_ms, 
                    frame_rate=self.audio.frame_rate
                )
            elif row['labels'] == 'female':
                male_audio += AudioSegment.silent(
                    duration=duration_ms, 
                    frame_rate=self.audio.frame_rate
                )
                female_audio += segment_audio
            else:
                # Handle 'noEnergy' or other labels as silence
                silence_segment = AudioSegment.silent(
                    duration=duration_ms, 
                    frame_rate=self.audio.frame_rate
                )
                male_audio += silence_segment
                female_audio += silence_segment
            
            current_time_ms = stop_ms
        
        # Handle any remaining audio at the end
        if current_time_ms < len(self.audio):
            remaining_duration_ms = len(self.audio) - current_time_ms
            male_audio += AudioSegment.silent(
                duration=remaining_duration_ms, 
                frame_rate=self.audio.frame_rate
            )
            female_audio += AudioSegment.silent(
                duration=remaining_duration_ms, 
                frame_rate=self.audio.frame_rate
            )
        
        # Verify that all tracks have the same duration
        original_duration = len(self.audio) / 1000
        male_duration = len(male_audio) / 1000
        female_duration = len(female_audio) / 1000
        
        print(f"Duration verification:")
        print(f"- Original audio: {original_duration:.3f} seconds")
        print(f"- Male track: {male_duration:.3f} seconds")
        print(f"- Female track: {female_duration:.3f} seconds")
        
        # Export the synchronized tracks
        male_audio.export(male_output, format='wav')
        female_audio.export(female_output, format='wav')
        
        print(f"Synchronized tracks created:")
        print(f"- {male_output}")
        print(f"- {female_output}")
        
        return male_output, female_output
    
    def create_segment_archive(self, speaker_label, archive_name=None):
        """
        Create a ZIP archive of all individual segments for a speaker.
        
        Args:
            speaker_label (str): Speaker label to archive
            archive_name (str): Name for the archive file (optional)
            
        Returns:
            str: Path to the created archive
        """
        if archive_name is None:
            archive_name = f"{speaker_label}_segments.zip"
        
        # Find all segment files for the speaker
        segment_files = glob.glob(f'{speaker_label}_segment*.wav')
        
        if not segment_files:
            print(f"No segment files found for {speaker_label}")
            return None
        
        print(f"Creating archive: {archive_name}")
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in segment_files:
                zipf.write(file, os.path.basename(file))
        
        print(f"Archive created with {len(segment_files)} files: {archive_name}")
        return archive_name
    
    def _cleanup_temp_files(self, file_list):
        """
        Clean up temporary files created during processing.
        
        Args:
            file_list (list): List of file paths to remove
        """
        for file_path in file_list:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as e:
                print(f"Warning: Could not remove temporary file {file_path}: {e}")
    
    def process_complete_workflow(self, create_concatenated=True, create_synchronized=True, 
                                create_stereo=True, create_archives=False):
        """
        Execute the complete speaker separation workflow.
        
        Args:
            create_concatenated (bool): Create concatenated speaker files
            create_synchronized (bool): Create synchronized tracks with timing
            create_stereo (bool): Create stereo mix
            create_archives (bool): Create ZIP archives of individual segments
            
        Returns:
            dict: Dictionary containing paths to all created files
        """
        results = {}
        
        try:
            # Step 1: Perform segmentation
            print("\n=== STEP 1: Audio Segmentation ===")
            self.segment_audio()
            
            # Step 2: Create concatenated tracks (speakers only, no timing)
            if create_concatenated:
                print("\n=== STEP 2: Creating Concatenated Tracks ===")
                male_concat = self.extract_speaker_segments('male', 'male_voice_concatenated.wav')
                female_concat = self.extract_speaker_segments('female', 'female_voice_concatenated.wav')
                
                if male_concat:
                    results['male_concatenated'] = male_concat
                if female_concat:
                    results['female_concatenated'] = female_concat
            
            # Step 3: Create synchronized tracks (preserves timing)
            if create_synchronized:
                print("\n=== STEP 3: Creating Synchronized Tracks ===")
                male_sync, female_sync = self.create_synchronized_tracks()
                results['male_synchronized'] = male_sync
                results['female_synchronized'] = female_sync
            
            # Step 4: Create stereo mix
            if create_stereo and create_synchronized:
                print("\n=== STEP 4: Creating Stereo Mix ===")
                stereo_file = self.create_stereo_mix(
                    results['male_synchronized'], 
                    results['female_synchronized'],
                    'stereo_mix.wav'
                )
                if stereo_file:
                    results['stereo_mix'] = stereo_file
            
            # Step 5: Create archives
            if create_archives:
                print("\n=== STEP 5: Creating Segment Archives ===")
                male_archive = self.create_segment_archive('male')
                female_archive = self.create_segment_archive('female')
                
                if male_archive:
                    results['male_archive'] = male_archive
                if female_archive:
                    results['female_archive'] = female_archive
            
            print("\n=== PROCESSING COMPLETE ===")
            print("Created files:")
            for key, filepath in results.items():
                print(f"- {key}: {filepath}")
            
            return results
            
        except Exception as e:
            print(f"Error during processing: {e}")
            raise


def main():
    """
    Main function to demonstrate usage of the PodcastSpeakerSeparator class.
    
    Modify the audio_file_path variable to point to your audio file.
    """
    # Configuration
    audio_file_path = "Chrono-Sampling.wav"  # Change this to your audio file path
    
    # Verify the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        print("Please update the audio_file_path variable with the correct path to your audio file.")
        return
    
    try:
        # Initialize the speaker separator
        separator = PodcastSpeakerSeparator(audio_file_path)
        
        # Run the complete workflow
        results = separator.process_complete_workflow(
            create_concatenated=True,    # Create concatenated speaker tracks
            create_synchronized=True,    # Create timing-synchronized tracks
            create_stereo=True,         # Create stereo mix
            create_archives=False       # Create ZIP archives (set to True if needed)
        )
        
        print("\nAll processing completed successfully!")
        
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except Exception as e:
        print(f"Processing error: {e}")
        raise


if __name__ == "__main__":
    main()
