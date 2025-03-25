import pandas as pd
import streamlit as st
import re

# Set up the page configuration
st.set_page_config(layout="wide", page_title="MC06 MONITORING", page_icon="📊", initial_sidebar_state="expanded")

# Title of the app
st.title('MC06 MONITORING')

# Data loading function with file upload support
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

# File uploader for Excel file
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Filter out specific users based on 'Remark By'
    exclude_users = ['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                     'JGCELIZ', 'SPMADRID', 'RRCARLIT', 'MEBEJER',
                     'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA', 'JATERRADO', 'LMLABRADOR']
    df = df[~df['Remark By'].isin(exclude_users)]

    # Define Positive Skip and Negative Skip conditions
    positive_skip_keywords = [
        "BRGY SKIPTRACE_POS - LEAVE MESSAGE FACEBOOK",
        "POS VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "POSITIVE VIA DIGITAL SKIP - FACEBOOK",
        "POSITIVE VIA DIGITAL SKIP - VIBER",
        "RPC_POS SKIP WITH REPLY - OTHER SOCMED",
        "RPC_POSITIVE SKIP WITH REPLY - FACEBOOK",
        "RPC_POSITIVE SKIP WITH REPLY - VIBER"
    ]

    negative_skip_status = [
        "NEGATIVE VIA DIGITAL SKIP - FACEBOOK",
        "NEGATIVE VIA DIGITAL SKIP - VIBER",
        "NEG VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "BRGY SKIP TRACING_NEGATIVE - CLIENT UNKNOWN",
        "BRGY SKIP TRACING_NEGATIVE - MOVED OUT"
    ]

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
        summary_table = []

        # Group by 'Date' and 'Client'
        for (date, client), date_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Client']):
            total_agents = date_group['Remark By'].nunique()
            total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_talk_time = date_group['Talk Time Duration'].sum()
            formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s'))
            
            # Count positive skip occurrences (contains specific keywords)
            positive_skip_count = date_group[date_group['Status'].str.contains('|'.join(map(re.escape, positive_skip_keywords)), case=False, na=False)].shape[0]
            
            # Count negative skip occurrences (exact match)
            negative_skip_count = date_group[date_group['Status'].isin(negative_skip_status)].shape[0]
            
            connected_ave = round(total_connected / total_agents, 2) if total_agents > 0 else 0
            talk_time_ave = str(pd.to_timedelta(total_talk_time / total_agents, unit='s')) if total_agents > 0 else "00:00:00"

            summary_table.append([date, client, total_agents, total_connected, positive_skip_count, negative_skip_count, formatted_talk_time, connected_ave, talk_time_ave])

        # Convert to DataFrame and display
        summary_df = pd.DataFrame(summary_table, columns=[
            'Day', 'Client', 'Total Agents', 'Total Connected', 'Positive Skip', 'Negative Skip', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
        ])
        st.write(summary_df)

    with col2:
        st.write("## Overall Summary per Date")

        overall_summary = []

        for date, date_group in filtered_df.groupby(filtered_df['Date'].dt.date):
            total_agents = date_group['Remark By'].nunique()
            total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_talk_time = date_group['Talk Time Duration'].sum()
            formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s'))
            
            # Count positive skip occurrences (contains specific keywords)
            positive_skip_count = date_group[date_group['Status'].str.contains('|'.join(map(re.escape, positive_skip_keywords)), case=False, na=False)].shape[0]
            
            # Count negative skip occurrences (exact match)
            negative_skip_count = date_group[date_group['Status'].isin(negative_skip_status)].shape[0]
            
            connected_ave = round(total_connected / total_agents, 2) if total_agents > 0 else 0
            talk_time_ave = str(pd.to_timedelta(total_talk_time / total_agents, unit='s')) if total_agents > 0 else "00:00:00"

            overall_summary.append([date, total_agents, total_connected, positive_skip_count, negative_skip_count, formatted_talk_time, connected_ave, talk_time_ave])

        # Convert to DataFrame and display
        overall_summary_df = pd.DataFrame(overall_summary, columns=[
            'Day', 'Total Agents', 'Total Connected', 'Positive Skip', 'Negative Skip', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
        ])
        st.write(overall_summary_df)
