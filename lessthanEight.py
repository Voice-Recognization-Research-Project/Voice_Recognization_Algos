import os
import shutil
import pandas as pd
from pydub import AudioSegment
import warnings

# Suppress pydub warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

hf_clips = r"C:\Nik\VIT\projects\asr_new\datasets\huggingface_dataset\clips"
hf_transcriptions = r"C:\Nik\VIT\projects\asr_new\datasets\huggingface_dataset\transcriptions.csv"

combined_clips = r"C:\Nik\VIT\projects\asr_new\combined_dataset"
combined_transcriptions = r"C:\Nik\VIT\projects\asr_new\combined_dataset.csv"

new_dataset = r"C:\Nik\VIT\projects\asr_new\dataset_new"
new_clips = os.path.join(new_dataset, "clips")
new_transcriptions_path = os.path.join(new_dataset, "transcriptions.csv")

os.makedirs(new_clips, exist_ok=True)
def get_audio_duration(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert to seconds
    except:
        print(f"  Error processing: {os.path.basename(file_path)}")
        return None

# ======== PROCESS DATASETS ========
def process_dataset(clips_folder, csv_path, dataset_name, col1, col2):
    """Process a single dataset and return valid entries"""
    print(f"\nProcessing {dataset_name} dataset...")
    
    # Read transcriptions
    if dataset_name == "Combined":
        # Combined dataset has no header
        df = pd.read_csv(csv_path, header=None, names=['filename', 'transcription'])
    else:
        # Hugging Face dataset has header
        df = pd.read_csv(csv_path)
    
    valid_entries = []
    total, valid = 0, 0
    
    for _, row in df.iterrows():
        total += 1
        filename = row[col1]
        transcription = row[col2]
        
        audio_path = os.path.join(clips_folder, filename)
        
        # Check if file exists
        if not os.path.exists(audio_path):
            # Try common filename patterns
            alt_path = os.path.join(clips_folder, os.path.basename(filename))
            if os.path.exists(alt_path):
                audio_path = alt_path
            else:
                continue
        
        # Check duration (≤8 seconds)
        duration = get_audio_duration(audio_path)
        if duration is None or duration > 8.0:  # >8 means skip, we want ≤8
            continue
        
        valid += 1
        valid_entries.append({
            'filename': os.path.basename(filename),
            'transcription': transcription,
            'source_path': audio_path
        })
    
    print(f"  Found {valid}/{total} valid clips (≤8s)")
    return valid_entries

# Process both datasets with correct columns
all_entries = []
all_entries += process_dataset(hf_clips, hf_transcriptions, "Hugging Face", 'filename', 'transcription')
all_entries += process_dataset(combined_clips, combined_transcriptions, "Combined", 'filename', 'transcription')

# ======== COPY FILES & HANDLE DUPLICATES ========
print("\nCopying files to new dataset...")
new_records = []
filename_counter = {}
copied_count = 0

for entry in all_entries:
    src = entry['source_path']
    orig_name = entry['filename']
    base, ext = os.path.splitext(orig_name)
    
    # Handle duplicate filenames
    if orig_name in filename_counter:
        filename_counter[orig_name] += 1
        new_name = f"{base}_{filename_counter[orig_name]}{ext}"
    else:
        filename_counter[orig_name] = 0
        new_name = orig_name
    
    # Copy file to new location
    dst = os.path.join(new_clips, new_name)
    shutil.copy2(src, dst)
    copied_count += 1
    
    # Add to records
    new_records.append({'filename': new_name, 'transcription': entry['transcription']})

# ======== SAVE TRANSCRIPTIONS ========
df_new = pd.DataFrame(new_records)
df_new.to_csv(new_transcriptions_path, index=False)

# ======== FINAL REPORT ========
print("\nOperation completed successfully!")
print(f"Total clips processed: {len(all_entries)}")
print(f"Clips copied: {copied_count}")
print(f"New dataset location: {new_dataset}")
print(f"  - Audio clips: {new_clips}")
print(f"  - Transcriptions: {new_transcriptions_path}")