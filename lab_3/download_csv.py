import urllib.request
from datetime import datetime
import os
import time

def clean_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[+] Directory created successfully.")
        return True  # Returning True as directory was just created, implying data download is necessary
    
    response = input("Do you want to clean the directory and download fresh data? (y/n): ").lower()
    if response == 'y':
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                os.unlink(filepath)
        print(f"[+] Directory cleaned successfully.\n")
        return True  # Returning True as user chose to clean directory and download fresh data
    else:
        print(f"[+] Directory cleaning skipped.\n")
        return False  # Returning False as user chose not to clean directory, implying existing data should be used

def download_csv(country, year_1, year_2, type_data, directory):
    clean_existing_data = clean_directory(directory)
    
    if clean_existing_data:
        for province_ID in range(1, 28):
            url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country={country}&provinceID={province_ID}&year1={year_1}&year2={year_2}&type={type_data}"
            
            retries = 3
            for attempt in range(retries):
                try:
                    with urllib.request.urlopen(url) as wp:
                        text = wp.read()
                    break
                except urllib.error.URLError as e:
                    print(f"Error downloading data for ID {province_ID}: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying download for ID {province_ID} in 5 seconds...")
                        time.sleep(5)
                    else:
                        print(f"Failed to download data for ID {province_ID} after {retries} attempts.")
                        continue

            current_time = datetime.now().strftime("%a, %Y-%m-%d %H:%M:%S")
            filename = f'NOAA_ID_{province_ID}_{current_time}.csv'
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, 'wb') as out:
                    out.write(text)
                print(f"Process is downloading:\nfile_csv:{filename}...\n")
                print(f"File_csv:{filename} downloaded successfully.")
                print(f"="*80)
            except IOError as e:
                print(f"Error writing file {filename}: {e}")

    else:
        print("Using existing data in the directory.")