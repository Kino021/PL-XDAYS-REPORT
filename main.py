import streamlit as st
import pandas as pd

# Load your dataset (Modify this to load from your actual source)
# Example: df = pd.read_csv("your_file.csv")
df = None  # Replace this with actual data loading

# Ensure df is defined before proceeding
if df is None:
    st.error("The DataFrame 'df' is not loaded. Please check if the data source is correct.")
    st.stop()

# Ensure DataFrame is not empty
if df.empty:
    st.error("The dataset is empty. Please upload a valid dataset.")
    st.stop()

# Ensure column names are stripped of spaces
df.columns = df.columns.str.strip()

# Convert 'Date' column to datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle invalid dates
else:
    st.error("Column 'Date' is missing from the dataset.")
    st.stop()

# Create the columns layout
col1, col2 = st.columns(2)

# ------------------------------------------
# 🔹 SUMMARY TABLE BY DAY
# ------------------------------------------
with col1:
    st.write("## Summary Table by Day")

    # Add date filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    # Filter data by selected date range
    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    # Initialize the summary table
    summary_table = pd.DataFrame(columns=['Day', 'Client', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'])

    # Group by 'Date' and 'Client'
    for (date, client), date_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Client']):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_talk_time = date_group['Talk Time Duration'].sum()  # Sum of Talk Time in seconds

        # Format Talk Time as HH:MM:SS
        formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s'))

        # Calculate averages
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0

        # Format Talk Time Average
        formatted_talk_time_ave = str(pd.to_timedelta(round(talk_time_ave), unit='s'))

        # Append row to summary table
        summary_table = pd.concat([summary_table, pd.DataFrame([{
            'Day': date,
            'Client': client,
            'Total Agents': total_agents,
            'Total Connected': total_connected,
            'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2),
            'Talk Time Ave': formatted_talk_time_ave
        }])], ignore_index=True)

    # Display the summary table
    st.write(summary_table)

# ------------------------------------------
# 🔹 OVERALL SUMMARY PER DATE
# ------------------------------------------
with col2:
    st.write("## Overall Summary per Date")

    # Initialize the overall summary table
    overall_summary = pd.DataFrame(columns=['Day', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'])

    # Group by 'Date'
    for date, date_group in filtered_df.groupby(filtered_df['Date'].dt.date):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_talk_time = date_group['Talk Time Duration'].sum()  # Sum of Talk Time in seconds

        # Format Talk Time as HH:MM:SS
        formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s'))

        # Calculate averages
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0

        # Format Talk Time Average
        formatted_talk_time_ave = str(pd.to_timedelta(round(talk_time_ave), unit='s'))

        # Append row to overall summary
        overall_summary = pd.concat([overall_summary, pd.DataFrame([{
            'Day': date,
            'Total Agents': total_agents,
            'Total Connected': total_connected,
            'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2),
            'Talk Time Ave': formatted_talk_time_ave
        }])], ignore_index=True)

    # Display the overall summary table
    st.write(overall_summary)
