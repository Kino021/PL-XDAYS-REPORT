import streamlit as st
import pandas as pd

# Load your DataFrame here (Replace with your actual data loading logic)
# Example: df = pd.read_csv("your_file.csv")

# Ensure column names are stripped of spaces
df.columns = df.columns.str.strip()

# Check if 'Date' exists before conversion
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle invalid dates
else:
    st.error("Column 'Date' is missing from the dataset.")
    st.stop()

# Create the columns layout
col1, col2 = st.columns(2)

with col1:
    st.write("## Summary Table by Day")

    # Add date filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    # Initialize an empty DataFrame for the summary table
    summary_table = pd.DataFrame(columns=[ 
        'Day', 'Client', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
    ])

    # Group by 'Date' and 'Client'
    for (date, client), date_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Client']):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()  # Count unique agents with Call Duration > 0
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()

        # Calculate total talk time
        total_talk_time = date_group['Talk Time Duration'].sum()
        formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s')).split()[2]  # HH:MM:SS format

        # Calculate averages
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
        talk_time_ave_str = str(pd.to_timedelta(round(talk_time_ave), unit='s')).split()[2]

        # Add row to summary table
        summary_table = pd.concat([summary_table, pd.DataFrame([{
            'Day': date,
            'Client': client,
            'Total Agents': total_agents,
            'Total Connected': total_connected,
            'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2),
            'Talk Time Ave': talk_time_ave_str
        }])], ignore_index=True)

    # Add total averages row
    if not summary_table.empty:
        total_connected_ave = summary_table['Total Connected'].mean()
        total_talk_time_ave = summary_table['Talk Time (HH:MM:SS)'].apply(
            lambda x: pd.to_timedelta(x).total_seconds()).mean()
        formatted_total_talk_time_ave = str(pd.to_timedelta(round(total_talk_time_ave), unit='s')).split()[2]

        total_row = pd.DataFrame([{
            'Day': 'Total',
            'Client': '',
            'Total Agents': '',
            'Total Connected': round(total_connected_ave, 2),
            'Talk Time (HH:MM:SS)': formatted_total_talk_time_ave,
            'Connected Ave': summary_table['Connected Ave'].mean(),
            'Talk Time Ave': formatted_total_talk_time_ave
        }])

        summary_table = pd.concat([summary_table, total_row], ignore_index=True)

    st.write(summary_table)

# Now create the overall summary table per date
with col2:
    st.write("## Overall Summary per Date")

    overall_summary = pd.DataFrame(columns=[ 
        'Day', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
    ])

    # Group by 'Date'
    for date, date_group in filtered_df.groupby(filtered_df['Date'].dt.date):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()

        # Calculate total talk time
        total_talk_time = date_group['Talk Time Duration'].sum()
        formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s')).split()[2]

        # Calculate averages
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
        talk_time_ave_str = str(pd.to_timedelta(round(talk_time_ave), unit='s')).split()[2]

        # Add row to overall summary
        overall_summary = pd.concat([overall_summary, pd.DataFrame([{
            'Day': date,
            'Total Agents': total_agents,
            'Total Connected': total_connected,
            'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2),
            'Talk Time Ave': talk_time_ave_str
        }])], ignore_index=True)

    st.write(overall_summary)
