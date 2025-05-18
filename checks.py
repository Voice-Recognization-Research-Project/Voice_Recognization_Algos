import os
import shutil
import pandas as pd
from datasets import load_dataset
import subprocess

# Check disk space
def check_disk_space():
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    print("Available disk space:")
    print(result.stdout)
    
check_disk_space()