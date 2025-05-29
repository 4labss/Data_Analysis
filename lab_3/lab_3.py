import os
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for Streamlit compatibility
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
from download_csv import download_csv
from data_cleaning import read_data
from replace import replace_function

# Configuration
country = "UKR"
year_1 = 1982
year_2 = 2025
type_data = "Mean"
directory = os.path.join(os.getcwd(), "data_csv")

PROVINCE_NAME_dict = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

# Cache data loading to run once
@st.cache_data
def load_data():
    download_csv(country, year_1, year_2, type_data, directory)
    data_frames = read_data(directory)
    if data_frames is None:
        st.error("No valid data loaded from the directory. Please check the CSV files or download fresh data.")
        st.stop()
    return replace_function(data_frames)

# Load data
data_frames_work = load_data()

# Streamlit app
st.title("NOAA Data Visualization")

# Debug toggle
show_debug = st.checkbox("Show Debug Information", value=False)

if show_debug:
    st.write(f"Loaded data_frames_work with {len(data_frames_work)} rows and columns: {list(data_frames_work.columns)}")
    st.write(f"Available PROVINCE_ID values: {sorted(data_frames_work['PROVINCE_ID'].unique())}")

# Input widgets
index = st.selectbox("NOAA Data Type", options=['VCI', 'TCI', 'VHI'], 
                     format_func=lambda x: {'VCI': 'Vegetation Condition Index (VCI)', 
                                           'TCI': 'Temperature Condition Index (TCI)', 
                                           'VHI': 'Vegetation Health (VHI)'}[x])
region = st.selectbox("Region", options=sorted(data_frames_work['PROVINCE_ID'].unique()), 
                      format_func=lambda x: PROVINCE_NAME_dict.get(x, str(x)), index=1)  # Default to Волинська
range_weeks = st.text_input("Range of Weeks (1 - 52)", value="1 - 52")
range_year = st.text_input("Range of Years", value="1982 - 2024")

# Initialize session state for filtered data
if 'data_frame' not in st.session_state:
    st.session_state.data_frame = None

# Function to filter data
def filter_data(index, region, range_weeks, range_year):
    try:
        week_1, week_2 = map(int, range_weeks.strip().split('-'))
        year_1, year_2 = map(int, range_year.strip().split('-'))
        
        if not (1 <= week_1 <= week_2 <= 52):
            st.error("Week range must be between 1 and 52.")
            return None
        if not (1982 <= year_1 <= year_2 <= 2024):
            st.error("Year range must be between 1982 and 2024.")
            return None

        province_name = PROVINCE_NAME_dict.get(int(region), "")
        data_frame = data_frames_work[
            (data_frames_work["PROVINCE_ID"] == int(region)) &
            (data_frames_work["Week"].between(week_1, week_2)) &
            (data_frames_work["Year"].between(year_1, year_2))
        ][["PROVINCE_ID", "Year", "Week", index]]
        data_frame.insert(0, "PROVINCE_NAME", province_name)

        if show_debug:
            st.write(f"Filtered data with {len(data_frame)} rows for {province_name}, "
                      f"weeks {week_1}-{week_2}, years {year_1}-{year_2}, index {index}")
            if not data_frame.empty:
                st.write(f"Sample data: {data_frame.head().to_dict()}")
        
        return data_frame
    except Exception as e:
        st.error(f"Error: {e}. Use format like '1 - 52' for weeks and years.")
        return None

# Filter data when button is clicked
if st.button("Get Data"):
    st.session_state.data_frame = filter_data(index, region, range_weeks, range_year)

# Initial filtering if no data in session state
if st.session_state.data_frame is None:
    st.session_state.data_frame = filter_data(index, region, range_weeks, range_year)

# Create tabs
tab1, tab2 = st.tabs(["Data Table", "Visualizations"])

with tab1:
    if st.session_state.data_frame is None or st.session_state.data_frame.empty:
        st.warning(f"No data available for {PROVINCE_NAME_dict.get(int(region), region)}, "
                   f"weeks {range_weeks}, years {range_year}, index {index}. Try different parameters.")
    else:
        st.subheader("Data Table")
        st.dataframe(st.session_state.data_frame)

with tab2:
    if st.session_state.data_frame is None or st.session_state.data_frame.empty:
        st.warning(f"No data to plot for {PROVINCE_NAME_dict.get(int(region), region)}, "
                   f"weeks {range_weeks}, years {range_year}, index {index}. Try different parameters.")
    else:
        st.subheader("Data Visualization")
        df = st.session_state.data_frame.drop(['PROVINCE_ID'], axis=1)

        # Line plot
        fig1, ax1 = plt.subplots(figsize=(10, 7))
        sns.lineplot(x='Week', y=index, hue='Year', data=df, marker='o', ax=ax1, linestyle='-')
        ax1.set_title(f"{index} for {country}: {df.iloc[0]['PROVINCE_NAME']}", 
                      fontsize=14, weight='bold')
        ax1.set_xlabel("Week", fontsize=12, weight='bold')
        ax1.set_ylabel(index, fontsize=12, weight='bold')
        ax1.grid(True, linestyle='--', alpha=0.95)
        ax1.legend(title="Year", fontsize=10, title_fontsize=12)
        ax1.tick_params(axis='both', labelsize=10)
        ax1.set_xlim(df['Week'].min() - 1, df['Week'].max() + 1)
        ax1.set_ylim(df[index].min() * 0.9, df[index].max() * 1.1)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig1.savefig(tmpfile.name)
            st.image(tmpfile.name)
        os.unlink(tmpfile.name)
        plt.close(fig1)

        # Heatmap
        fig2, ax2 = plt.subplots(figsize=(10, 7))
        pivot_data = df.pivot(index="Week", columns="Year", values=index)
        sns.heatmap(pivot_data, cmap="Greens", annot=True, fmt=".1f", ax=ax2)
        ax2.set_title(f"{index} for {country}: {df.iloc[0]['PROVINCE_NAME']}", 
                      fontsize=14, weight='bold')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig2.savefig(tmpfile.name)
            st.image(tmpfile.name)
        os.unlink(tmpfile.name)
        plt.close(fig2)