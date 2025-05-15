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
        return df
    
    except pd.errors.ParserError as e:
        print(f"Error reading {filepath}: {e}")
        return None

def read_data(directory):
    data_frames = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filepath.endswith('.csv'):
            province_ID = filename.split('_')[2] if len(filename.split('_')) >= 3 else None                          
                      
            df = read_csv_file(filepath)  
            if int(province_ID) not in [12, 20]:          
                if df is not None:
                    df.insert(0, "PROVINCE_ID", int(province_ID), True)                   
                    df["Week"] = df["Week"].astype(int)
                    df["Year"] = df["Year"].astype(int)               
                    data_frames.append(df)                 
    
    data_frames.sort(key=lambda x: int(x["PROVINCE_ID"].iloc[0]))
    data_frames = pd.concat(data_frames).drop_duplicates().reset_index(drop=True)                      
    return data_frames