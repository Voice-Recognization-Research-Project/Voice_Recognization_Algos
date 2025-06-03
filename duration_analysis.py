import os
from pydub import AudioSegment
import pandas as pd

# ======== CONFIGURATION ========
clips_folder = r"C:\Nik\VIT\projects\asr_new\dataset_new\clips"
transcriptions_file = r"C:\Nik\VIT\projects\asr_new\dataset_new\transcriptions.csv"

def analyze_audio_durations():
    # Initialize variables to track min/max durations
    min_duration = float('inf')
    max_duration = 0
    min_file = ""
    max_file = ""
    total_duration = 0
    file_count = 0
    
    # Create a list to store durations for analysis
    durations = []
    
    # Read transcriptions for later reference
    transcriptions_df = pd.read_csv(transcriptions_file)
    transcriptions_dict = dict(zip(transcriptions_df['filename'], transcriptions_df['transcription']))
    
    print(f"Analyzing audio clips in: {clips_folder}")
    print(f"Found {len(os.listdir(clips_folder))} files...\n")
    
    for filename in os.listdir(clips_folder):
        file_path = os.path.join(clips_folder, filename)
        
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000.0  # Convert to seconds
            durations.append(duration)
            total_duration += duration
            file_count += 1
            
            # Check for min duration
            if duration < min_duration:
                min_duration = duration
                min_file = filename
                
            # Check for max duration
            if duration > max_duration:
                max_duration = duration
                max_file = filename
                
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
    
    # Calculate statistics
    avg_duration = total_duration / file_count if file_count > 0 else 0
    sorted_durations = sorted(durations)
    median_duration = sorted_durations[len(durations)//2] if durations else 0
    
    # Print results
    print("\n" + "="*50)
    print("AUDIO DURATION ANALYSIS RESULTS")
    print("="*50)
    print(f"Total files processed: {file_count}")
    print(f"Files with errors: {len(os.listdir(clips_folder)) - file_count}")
    print(f"Average duration: {avg_duration:.2f} seconds")
    print(f"Median duration: {median_duration:.2f} seconds")
    print(f"Total audio duration: {total_duration/60:.2f} minutes")
    
    print("\nSHORTEST CLIP:")
    print(f"  File: {min_file}")
    print(f"  Duration: {min_duration:.3f} seconds")
    if min_file in transcriptions_dict:
        print(f"  Transcription: {transcriptions_dict[min_file][:100]}...")
    
    print("\nLONGEST CLIP:")
    print(f"  File: {max_file}")
    print(f"  Duration: {max_duration:.3f} seconds")
    if max_file in transcriptions_dict:
        print(f"  Transcription: {transcriptions_dict[max_file][:100]}...")
    
    # Duration distribution analysis
    print("\nDURATION DISTRIBUTION:")
    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    dist = {f"{b}-{b+1}s": 0 for b in bins if b < 8}
    dist["0-1s"] = 0  # Ensure we have this bin
    
    for duration in durations:
        for bin_start in bins:
            if bin_start <= duration < bin_start + 1:
                key = f"{bin_start}-{bin_start+1}s"
                dist[key] = dist.get(key, 0) + 1
                break
    
    # Print distribution
    for bin_range, count in dist.items():
        percentage = (count / file_count) * 100 if file_count > 0 else 0
        print(f"  {bin_range}: {count} files ({percentage:.1f}%)")
    
    # Find files exactly at 8 seconds
    exactly_8s = [f for d, f in zip(durations, os.listdir(clips_folder)) if 7.999 <= d <= 8.001]
    print(f"\nFiles exactly 8 seconds: {len(exactly_8s)}")

# Run the analysis
if __name__ == "__main__":
    analyze_audio_durations()