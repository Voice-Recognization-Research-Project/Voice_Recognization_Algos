import os
os.environ["TMPDIR"] = "/workspace/tmp"

import shutil
import pandas as pd
from datasets import load_dataset

os.environ["HF_DATASETS_CACHE"] = "/workspace/hf_cache/datasets"


base_dir = base_dir = "/workspace/datasets/zsy12345"
clips_dir = os.path.join(base_dir, "clips")

# Create directories
os.makedirs(clips_dir, exist_ok=True)

# Load the dataset from HF
print("Loading dataset...")
dataset = load_dataset("zsy12345/telugu-asr", split="train")
print(f"Dataset loaded with {len(dataset)} samples")


target_duration_sec = 40 * 3600  # 40 hours in seconds
selected_samples = []
accumulated_duration = 0.0

print("Selecting samples up to 40 hours...")
for sample in dataset:
    dur = sample.get("duration", 0)
    if accumulated_duration + dur > target_duration_sec:
        break
    selected_samples.append(sample)
    accumulated_duration += dur

print(f"Selected {len(selected_samples)} samples totaling {accumulated_duration / 3600:.2f} hours")

# Copy audio files and prepare transcription CSV
rows = []
success_count = 0
error_count = 0

print("Copying audio files and preparing transcriptions...")
for i, sample in enumerate(selected_samples):
    try:
        # Get audio file path - this line ensures the audio is downloaded
        audio_path = sample["audio"]["path"]
        if not os.path.exists(audio_path):
            # If path doesn't exist, try to download the file
            audio_array = sample["audio"]["array"]
            sample_rate = sample["audio"]["sampling_rate"]
            # Now audio_path should be available after loading the array
            audio_path = sample["audio"]["path"]
            
        filename = os.path.basename(audio_path)
        
        # Copy audio file to clips folder
        dest_path = os.path.join(clips_dir, filename)
        shutil.copy(audio_path, dest_path)
        
        # Store transcription with filename
        rows.append({"file": filename, "transcription": sample["text"]})
        success_count += 1
        
        # Print progress every 100 files
        if success_count % 100 == 0:
            print(f"Processed {success_count} files...")
            
    except Exception as e:
        print(f"Error processing sample {i}: {str(e)}")
        error_count += 1

# Save transcriptions to CSV
df = pd.DataFrame(rows)
csv_path = os.path.join(base_dir, "transcriptions.csv")
df.to_csv(csv_path, index=False)

print(f"Processing complete!")
print(f"Successfully copied {success_count} audio clips to: {clips_dir}")
print(f"Failed to process {error_count} files")
print(f"Saved transcriptions CSV to: {csv_path}")
print(f"Total dataset duration: {accumulated_duration / 3600:.2f} hours")