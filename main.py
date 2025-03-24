import streamlit as st
import pandas as pd

# Load DataFrame (assuming you have already loaded your data into 'df')
df['Date'] = pd.to_datetime(df['Date'])

# Create the columns layout
col1, col2 = st.columns(2)

with col1:
    st.write("## Summary Table by Day")

    # Add date filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    summary_table = pd.DataFrame(columns=[
        'Day', 'Client', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
    ])

    for (date, client), date_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Client']):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_talk_time = date_group['Talk Time Duration'].sum()
        talk_time_str = str(pd.to_timedelta(total_talk_time, unit='s'))
        formatted_talk_time = talk_time_str.split()[2]
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
        talk_time_ave_str = str(pd.to_timedelta(talk_time_ave, unit='s')).split()[2]

        summary_table = pd.concat([summary_table, pd.DataFrame([{
            'Day': date, 'Client': client, 'Total Agents': total_agents,
            'Total Connected': total_connected, 'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2), 'Talk Time Ave': talk_time_ave_str
        }])], ignore_index=True)

    st.write(summary_table)

with col2:
    st.write("## Overall Summary per Date")

    overall_summary = pd.DataFrame(columns=[
        'Day', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
    ])

    for date, date_group in filtered_df.groupby(filtered_df['Date'].dt.date):
        valid_agents = date_group[date_group['Call Duration'].notna() & (date_group['Call Duration'] > 0)]
        total_agents = valid_agents['Remark By'].nunique()
        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_talk_time = date_group['Talk Time Duration'].sum()
        talk_time_str = str(pd.to_timedelta(total_talk_time, unit='s'))
        formatted_talk_time = talk_time_str.split()[2]
        connected_ave = total_connected / total_agents if total_agents > 0 else 0
        talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
        talk_time_ave_str = str(pd.to_timedelta(talk_time_ave, unit='s')).split()[2]

        overall_summary = pd.concat([overall_summary, pd.DataFrame([{
            'Day': date, 'Total Agents': total_agents,
            'Total Connected': total_connected, 'Talk Time (HH:MM:SS)': formatted_talk_time,
            'Connected Ave': round(connected_ave, 2), 'Talk Time Ave': talk_time_ave_str
        }])], ignore_index=True)

    st.write(overall_summary)
