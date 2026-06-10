# reset_all_data.py
# A standalone utility to perform a full factory reset on ALL game data files.
# This version initializes all pattern counts to 1.

import pandas as pd
import os

print("--- Factory Resetting All Game Data ---")

# Define the path to the data directory
DATA_DIR = 'datastorecsv'
if not os.path.isdir(DATA_DIR):
    print(f"Error: Data directory '{DATA_DIR}' not found. Cannot reset.")
    exit()

# --- Define the Default Data Structures for a Clean Slate ---

default_ucr = {'User': [], 'Com': []}
default_pattern = {'I1': [], 'I2': [], 'I3': [], 'I4': [], 'I5': [], 'I6': []}
default_heatmap = {
    'No.': list(range(1, 11)),
    'Predictions': [0] * 10,
    'Accuracy': [0] * 10,
    'Correct': [0] * 10,
    'Closeby': [0] * 10
}

# Define the combinations and their types
combinations = [
    "1,3,4", "1,4,3", "1,4,4", "2,3,4", "2,4,3", "2,4,4", "3,1,4", "3,2,4", "3,3,3", "3,3,4",
    "3,4,1", "3,4,2", "3,4,3", "3,4,4", "4,1,3", "4,1,4", "4,2,3", "4,2,4", "4,3,1", "4,3,2",
    "4,3,3", "4,3,4", "4,4,1", "4,4,2", "4,4,3", "4,4,4", "1,2,3", "1,2,4", "1,3,2", "1,3,3",
    "1,4,2", "2,1,3", "2,1,4", "2,2,3", "2,2,4", "2,3,1", "2,3,2", "2,3,3", "2,4,1", "2,4,2",
    "3,1,2", "3,1,3", "3,2,1", "3,2,2", "3,2,3", "3,3,1", "3,3,2", "4,1,2", "4,2,1", "4,2,2",
    "4,1,2", "1,1,1", "1,1,2", "1,1,3", "1,1,4", "1,2,1", "1,2,2", "1,3,1", "1,4,1", "2,1,1",
    "2,1,2", "2,1,3", "2,1,4", "2,2,1", "2,2,2", "3,1,1", "4,1,1"
]
types = [
    'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH',
    'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH',
    'HIGH', 'HIGH', 'HIGH', 'HIGH', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID',
    'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID', 'MID',
    'MID', 'MID', 'MID', 'MID', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW',
    'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW'
]

# --- MODIFIED: Set all counts to 1 ---
# Create a list of 1s that is the same length as the list of combinations
counts = [1] * len(combinations)

# Assemble the final dictionary
default_comdistro = {
    'Combination': combinations,
    'Type': types,
    'Count': counts
}


# A list of all files to be reset with their corresponding default data
files_to_reset = [
    # Permanent Files
    ("Permanent_UCR.csv", default_ucr),
    ("Permanent_Pattern.csv", default_pattern),
    ("Permanent_Heatmap.csv", default_heatmap),
    ("P_ComboDistributive.csv", default_comdistro),
    # Instance Files
    ("Instance_UCR.csv", default_ucr),
    ("Instance_Pattern.csv", default_pattern),
    ("Instance_Heatmap.csv", default_heatmap),
    ("I_ComboDistributive.csv", default_comdistro),
]

# --- Main Reset Logic ---
success_count = 0
for filename, data_dict in files_to_reset:
    try:
        filepath = os.path.join(DATA_DIR, filename)
        df = pd.DataFrame(data_dict)
        df.to_csv(filepath, index=False)
        print(f"Successfully reset: {filepath}")
        success_count += 1
    except Exception as e:
        print(f"ERROR resetting {filename}: {e}")

print(f"\n--- Reset complete. {success_count}/{len(files_to_reset)} files were reset to their defaults. ---")