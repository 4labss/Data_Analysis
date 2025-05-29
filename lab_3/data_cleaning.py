import pandas as pd
from datetime import datetime
import os
import re

# data cleaning
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def read_csv_file(filepath):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    try:
        df = pd.read_csv(filepath, header=1, names=headers, converters={'Year': remove_html_tags})
        df = df.drop(df[(df['VHI'] == -1) | (df['TCI'] == -1) | (df['VCI'] == -1)].index)
        df = df.drop("empty", axis=1)
        df = df.drop(df.index[-1])          
        print(f"[+] Successfully processed file: {filepath}")
        return df
    except pd.errors.ParserError as e:
        print(f"[-] Error reading {filepath}: {e}")
        return None
    except Exception as e:
        print(f"[-] Unexpected error reading {filepath}: {e}")
        return None

def read_data(directory):
    data_frames = []
    print(f"[+] Reading CSV files from directory: {directory}")
    if not os.path.exists(directory):
        print(f"[-] Directory does not exist: {directory}")
        return None
    
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if not csv_files:
        print(f"[-] No CSV files found in directory: {directory}")
        return None

    for filename in csv_files:
        filepath = os.path.join(directory, filename)
        try:
            province_ID = filename.split('_')[2] if len(filename.split('_')) >= 3 else None
            if province_ID is None or not province_ID.isdigit():
                print(f"[-] Invalid filename format, cannot extract province_ID: {filename}")
                continue
            province_ID = int(province_ID)
            if province_ID in [12, 20]:
                print(f"[-] Skipping excluded province_ID {province_ID} for file: {filename}")
                continue
            df = read_csv_file(filepath)
            if df is not None:
                df.insert(0, "PROVINCE_ID", province_ID, True)
                df["Week"] = df["Week"].astype(int)
                df["Year"] = df["Year"].astype(int)
                data_frames.append(df)
                print(f"[+] Added DataFrame for province_ID {province_ID} from file: {filename}")
            else:
                print(f"[-] Failed to process file: {filename}")
        except Exception as e:
            print(f"[-] Error processing file {filename}: {e}")
            continue
    
    if not data_frames:
        print(f"[-] No valid DataFrames created from directory: {directory}")
        return None
    
    print(f"[+] Concatenating {len(data_frames)} DataFrames")
    data_frames = pd.concat(data_frames).drop_duplicates().reset_index(drop=True)
    return data_frames