import pandas as pd
import streamlit as st
import math
from io import BytesIO

# Set up the page configuration
st.set_page_config(layout="wide", page_title="MC06 MONITORING", page_icon="📊", initial_sidebar_state="expanded")

# Title of the app
st.title('MC06 MONITORING')

# Data loading function with file upload support
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    # Filter out rows where 'Remark' contains "broken promise" (case-insensitive)
    df = df[~df['Remark'].astype(str).str.contains("broken promise", case=False, na=False)]
    return df

# Function to create a single Excel file with multiple sheets, auto-fit columns, borders, middle alignment, red headers, and custom date formats
def create_combined_excel_file(summary_dfs, overall_summary_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({
            'bg_color': '#FF0000',  # Red background
            'font_color': '#FFFFFF',  # White text
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        date_format = workbook.add_format({
            'num_format': 'mmm dd, yyyy',  # e.g., Mar 25, 2025
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        date_range_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        time_format = workbook.add_format({
            'num_format': 'hh:mm:ss',  # e.g., 01:23:45
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        for client, summary_df in summary_dfs.items():
            summary_df.to_excel(writer, sheet_name=f"Summary_{client[:31]}", index=False, startrow=1, header=False)
            worksheet = writer.sheets[f"Summary_{client[:31]}"]
            for col_idx, col in enumerate(summary_df.columns):
                worksheet.write(0, col_idx, col, header_format)
            for row_idx in range(len(summary_df)):
                for col_idx, value in enumerate(summary_df.iloc[row_idx]):
                    if col_idx == 0:  # 'Day' column
                        worksheet.write_datetime(row_idx + 1, col_idx, value, date_format)
                    elif col_idx in [6, 8, 9]:  # Talk Time columns (Total, Positive Skip, Negative Skip)
                        worksheet.write(row_idx + 1, col_idx, value, time_format)
                    else:
                        worksheet.write(row_idx + 1, col_idx, value, cell_format)
            for col_idx, col in enumerate(summary_df.columns):
                if col_idx == 0:
                    max_length = max(summary_df[col].astype(str).map(lambda x: len('MMM DD, YYYY')).max(), len(str(col)))
                else:
                    max_length = max(summary_df[col].astype(str).map(len).max(), len(str(col)))
                worksheet.set_column(col_idx, col_idx, max_length + 2)

        overall_summary_df.to_excel(writer, sheet_name="Overall_Summary", index=False, startrow=1, header=False)
        worksheet = writer.sheets["Overall_Summary"]
        for col_idx, col in enumerate(overall_summary_df.columns):
            worksheet.write(0, col_idx, col, header_format)
        for row_idx in range(len(overall_summary_df)):
            for col_idx, value in enumerate(overall_summary_df.iloc[row_idx]):
                if col_idx == 0:  # 'Date Range' column
                    worksheet.write(row_idx + 1, col_idx, value, date_range_format)
                elif col_idx in [10, 12, 13]:  # Talk Time columns (Total, Positive Skip, Negative Skip)
                    worksheet.write(row_idx + 1, col_idx, value, time_format)
                else:
                    worksheet.write(row_idx + 1, col_idx, value, cell_format)
        for col_idx, col in enumerate(overall_summary_df.columns):
            if col_idx == 0:
                max_length = max(overall_summary_df[col].astype(str).map(len).max(), len(str(col)))
            else:
                max_length = max(overall_summary_df[col].astype(str).map(len).max(), len(str(col)))
            worksheet.set_column(col_idx, col_idx, max_length + 2)

    return output.getvalue()

# File uploader for Excel file
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

# Define columns outside the conditional block
col1, col2 = st.columns(2)

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Ensure 'Date' column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Ensure 'Talk Time Duration' and 'Call Duration' are numeric
    df['Talk Time Duration'] = pd.to_numeric(df['Talk Time Duration'], errors='coerce').fillna(0)
    df['Call Duration'] = pd.to_numeric(df['Call Duration'], errors='coerce').fillna(0)

    # Define Positive Skip conditions
    positive_skip_keywords = [
        "BRGY SKIPTRACE_POS - LEAVE MESSAGE CALL SMS",
        "BRGY SKIPTRACE_POS - LEAVE MESSAGE FACEBOOK",
        "POS VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "POSITIVE VIA DIGITAL SKIP - FACEBOOK",
        "POSITIVE VIA DIGITAL SKIP - GOOGLE SEARCH",
        "POSITIVE VIA DIGITAL SKIP - INSTAGRAM",
        "POSITIVE VIA DIGITAL SKIP - LINKEDIN",
        "POSITIVE VIA DIGITAL SKIP - OTHER SOCMED",
        "POSITIVE VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "POSITIVE VIA DIGITAL SKIP - VIBER",
        "POS VIA SOCMED - GOOGLE SEARCH",
        "POS VIA SOCMED - LINKEDIN",
        "POS VIA SOCMED - OTHER SOCMED PLATFORMS",
        "POS VIA SOCMED - FACEBOOK",
        "POS VIA SOCMED - VIBER",
        "POS VIA SOCMED - INSTAGRAM",
        "POS VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "LS VIA SOCMED - T5 BROKEN PTP SPLIT AND OTP",
        "LS VIA SOCMED - T6 NO RESPONSE (SMS & EMAIL)",
        "LS VIA SOCMED - T7 PROMO OFFER LETTER",
        "LS VIA SOCMED - T9 RESTRUCTURING",
        "LS VIA SOCMED - T1 NOTIFICATION",
        "LS VIA SOCMED - T12 THIRD PARTY TEMPLATE",
        "LS VIA SOCMED - T8 AMNESTY PROMO TEMPLATE",
        "LS VIA SOCMED - T4 BROKEN PTP EPA",
        "LS VIA SOCMED - T6 NO RESPONSE SMS AND EMAIL",
        "LS VIA SOCMED - OTHERS",
        "LS VIA SOCMED - T10 PRE TERMINATION OFFER",
    ]

    # Define Negative Skip status conditions
    negative_skip_status = [
        "BRGY SKIP TRACING_NEGATIVE - CLIENT UNKNOWN",
        "BRGY SKIP TRACING_NEGATIVE - MOVED OUT",
        "BRGY SKIP TRACING_NEGATIVE - UNCONTACTED",
        "NEG VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "NEGATIVE VIA DIGITAL SKIP - FACEBOOK",
        "NEGATIVE VIA DIGITAL SKIP - GOOGLE SEARCH",
        "NEGATIVE VIA DIGITAL SKIP - INSTAGRAM",
        "NEGATIVE VIA DIGITAL SKIP - LINKEDIN",
        "NEGATIVE VIA DIGITAL SKIP - OTHER SOCMED",
        "NEGATIVE VIA DIGITAL SKIP - OTHER SOCMED PLATFORMS",
        "NEGATIVE VIA DIGITAL SKIP - VIBER",
        "NEG VIA SOCMED - OTHER SOCMED PLATFORMS",
        "NEG VIA SOCMED - FACEBOOK",
        "NEG VIA SOCMED - VIBER",
        "NEG VIA SOCMED - GOOGLE SEARCH",
        "NEG VIA SOCMED - LINKEDIN",
        "NEG VIA SOCMED - INSTAGRAM",
    ]

    # Dictionary to store summary DataFrames for each client
    summary_dfs = {}

    with col1:
        st.write("## Summary Table by Day")
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)
        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        # Debug: Check if filtered_df has data
        if filtered_df.empty:
            st.warning("No data available for the selected date range.")
        else:
            for client, client_group in filtered_df.groupby('Client'):
                with st.container():
                    st.subheader(f"Client: {client}")
                    
                    # Summary table for daily metrics
                    summary_table = []
                    for date, date_group in client_group.groupby(client_group['Date'].dt.date):
                        valid_group = date_group[(date_group['Call Duration'].notna()) & 
                                                (date_group['Call Duration'] > 0) & 
                                                (date_group['Remark By'].str.lower() != "system")]
                        total_agents = valid_group['Remark By'].nunique()
                        total_connected = date_group[date_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                        total_talk_time_seconds = date_group['Talk Time Duration'].sum()
                        hours, remainder = divmod(int(total_talk_time_seconds), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        formatted_talk_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        talk_time_ave_seconds = total_talk_time_seconds / total_agents if total_agents > 0 else 0
                        ave_hours, ave_remainder = divmod(int(talk_time_ave_seconds), 3600)
                        ave_minutes, ave_seconds = divmod(ave_remainder, 60)
                        talk_time_ave_str = f"{ave_hours:02d}:{ave_minutes:02d}:{ave_seconds:02d}"
                        positive_skip_count = sum(date_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))
                        negative_skip_count = date_group[date_group['Status'].isin(negative_skip_status)].shape[0]
                        total_skip = positive_skip_count + negative_skip_count
                        positive_skip_connected = date_group[(date_group['Call Status'] == 'CONNECTED') & 
                                                            (date_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))]['Account No.'].count()
                        negative_skip_connected = date_group[(date_group['Call Status'] == 'CONNECTED') & 
                                                            (date_group['Status'].isin(negative_skip_status))]['Account No.'].count()
                        positive_skip_talk_time_seconds = date_group[(date_group['Call Status'] == 'CONNECTED') & 
                                                                    (date_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))]['Talk Time Duration'].sum()
                        negative_skip_talk_time_seconds = date_group[(date_group['Call Status'] == 'CONNECTED') & 
                                                                    (date_group['Status'].isin(negative_skip_status))]['Talk Time Duration'].sum()
                        pos_hours, pos_remainder = divmod(int(positive_skip_talk_time_seconds), 3600)
                        pos_minutes, pos_seconds = divmod(pos_remainder, 60)
                        positive_skip_talk_time = f"{pos_hours:02d}:{pos_minutes:02d}:{pos_seconds:02d}"
                        neg_hours, neg_remainder = divmod(int(negative_skip_talk_time_seconds), 3600)
                        neg_minutes, neg_seconds = divmod(neg_remainder, 60)
                        negative_skip_talk_time = f"{neg_hours:02d}:{neg_minutes:02d}:{neg_seconds:02d}"
                        positive_skip_ave = round(positive_skip_count / total_agents, 2) if total_agents > 0 else 0
                        negative_skip_ave = round(negative_skip_count / total_agents, 2) if total_agents > 0 else 0
                        total_skip_ave = round(total_skip / total_agents, 2) if total_agents > 0 else 0
                        connected_ave = round(total_connected / total_agents, 2) if total_agents > 0 else 0
                        summary_table.append([
                            date, total_agents, total_connected, positive_skip_count, negative_skip_count, total_skip,
                            positive_skip_connected, negative_skip_connected, positive_skip_talk_time, negative_skip_talk_time,
                            formatted_talk_time, positive_skip_ave, negative_skip_ave, total_skip_ave, connected_ave, talk_time_ave_str
                        ])
                    summary_df = pd.DataFrame(summary_table, columns=[
                        'Day', 'Collectors', 'Total Connected', 'Positive Skip', 'Negative Skip', 'Total Skip',
                        'Positive Skip Connected', 'Negative Skip Connected', 'Positive Skip Talk Time', 'Negative Skip Talk Time',
                        'Talk Time (HH:MM:SS)', 'Positive Skip Ave', 'Negative Skip Ave', 'Total Skip Ave', 'Connected Ave', 'Talk Time Ave'
                    ])
                    st.dataframe(summary_df)
                    summary_dfs[client] = summary_df

                    # Separate containers for Positive Skip criteria
                    st.write("### Positive Skip Breakdown")
                    pos_col, neg_col = st.columns(2)
                    with pos_col:
                        positive_skip_group = client_group[client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False)]
                        for status, status_group in positive_skip_group.groupby('Status'):
                            with st.container():
                                st.write(f"**{status}**")
                                count = status_group.shape[0]
                                connected = status_group[status_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                                talk_time_seconds = status_group['Talk Time Duration'].sum()
                                hours, remainder = divmod(int(talk_time_seconds), 3600)
                                minutes, seconds = divmod(remainder, 60)
                                formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                                st.write(f"Count: {count}, Connected: {connected}, Talk Time: {formatted_time}")

                    # Separate containers for Negative Skip criteria
                    st.write("### Negative Skip Breakdown")
                    with neg_col:
                        negative_skip_group = client_group[client_group['Status'].isin(negative_skip_status)]
                        for status, status_group in negative_skip_group.groupby('Status'):
                            with st.container():
                                st.write(f"**{status}**")
                                count = status_group.shape[0]
                                connected = status_group[status_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                                talk_time_seconds = status_group['Talk Time Duration'].sum()
                                hours, remainder = divmod(int(talk_time_seconds), 3600)
                                minutes, seconds = divmod(remainder, 60)
                                formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                                st.write(f"Count: {count}, Connected: {connected}, Talk Time: {formatted_time}")

    with col2:
        st.write("## Overall Summary per Client")
        with st.container():
            date_range_str = f"{start_date.strftime('%b %d %Y').upper()} - {end_date.strftime('%b %d %Y').upper()}"
            valid_df = filtered_df[(filtered_df['Call Duration'].notna()) & 
                                  (filtered_df['Call Duration'] > 0) & 
                                  (filtered_df['Remark By'].str.lower() != "system")]
            avg_collectors_per_client = valid_df.groupby(['Client', valid_df['Date'].dt.date])['Remark By'].nunique().groupby('Client').mean().apply(lambda x: math.ceil(x) if x % 1 >= 0.5 else round(x))

            overall_summary = []
            for client, client_group in filtered_df.groupby('Client'):
                # Debug: Check if client_group has data
                if client_group.empty:
                    st.warning(f"No data for client {client} in the selected date range.")
                    continue

                total_agents = avg_collectors_per_client.get(client, 0)
                total_connected = client_group[client_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                total_talk_time_seconds = client_group['Talk Time Duration'].sum()
                hours, remainder = divmod(int(total_talk_time_seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted_talk_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                positive_skip_count = sum(client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))
                negative_skip_count = client_group[client_group['Status'].isin(negative_skip_status)].shape[0]
                total_skip = positive_skip_count + negative_skip_count
                positive_skip_connected = client_group[(client_group['Call Status'] == 'CONNECTED') & 
                                                      (client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))]['Account No.'].count()
                negative_skip_connected = client_group[(client_group['Call Status'] == 'CONNECTED') & 
                                                      (client_group['Status'].isin(negative_skip_status))]['Account No.'].count()
                positive_skip_talk_time_seconds = client_group[(client_group['Call Status'] == 'CONNECTED') & 
                                                              (client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))]['Talk Time Duration'].sum()
                negative_skip_talk_time_seconds = client_group[(client_group['Call Status'] == 'CONNECTED') & 
                                                              (client_group['Status'].isin(negative_skip_status))]['Talk Time Duration'].sum()
                pos_hours, pos_remainder = divmod(int(positive_skip_talk_time_seconds), 3600)
                pos_minutes, pos_seconds = divmod(pos_remainder, 60)
                positive_skip_talk_time = f"{pos_hours:02d}:{pos_minutes:02d}:{pos_seconds:02d}"
                neg_hours, neg_remainder = divmod(int(negative_skip_talk_time_seconds), 3600)
                neg_minutes, neg_seconds = divmod(neg_remainder, 60)
                negative_skip_talk_time = f"{neg_hours:02d}:{neg_minutes:02d}:{neg_seconds:02d}"
                daily_data = client_group.groupby(client_group['Date'].dt.date).agg({
                    'Remark By': lambda x: x[(client_group['Call Duration'].notna()) & 
                                            (client_group['Call Duration'] > 0) & 
                                            (client_group['Remark By'].str.lower() != "system")].nunique(),
                    'Account No.': lambda x: x[client_group['Call Status'] == 'CONNECTED'].count(),
                    'Status': [
                        lambda x: sum(x.astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False)),
                        lambda x: x.isin(negative_skip_status).sum(),
                        lambda x: x[(client_group['Call Status'] == 'CONNECTED') & 
                                   (x.astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))].count(),
                        lambda x: x[(client_group['Call Status'] == 'CONNECTED') & 
                                   (x.isin(negative_skip_status))].count()
                    ],
                    'Talk Time Duration': [
                        'sum',
                        lambda x: x[(client_group['Call Status'] == 'CONNECTED') & 
                                   (client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))].sum(),
                        lambda x: x[(client_group['Call Status'] == 'CONNECTED') & 
                                   (client_group['Status'].isin(negative_skip_status))].sum()
                    ]
                })
                daily_data.columns = ['Collectors', 'Total Connected', 
                                     'Positive Skip', 'Negative Skip', 'Positive Skip Connected', 'Negative Skip Connected',
                                     'Talk Time', 'Positive Skip Talk Time Seconds', 'Negative Skip Talk Time Seconds']
                daily_data['Total Skip'] = daily_data['Positive Skip'] + daily_data['Negative Skip']
                daily_data['Positive Skip Ave'] = daily_data['Positive Skip'] / daily_data['Collectors']
                daily_data['Negative Skip Ave'] = daily_data['Negative Skip'] / daily_data['Collectors']
                daily_data['Total Skip Ave'] = daily_data['Total Skip'] / daily_data['Collectors']
                daily_data['Connected Ave'] = daily_data['Total Connected'] / daily_data['Collectors']
                daily_data['Talk Time Ave Seconds'] = daily_data['Talk Time'] / daily_data['Collectors']
                positive_skip_ave = round(daily_data['Positive Skip Ave'].mean(), 2) if not daily_data.empty else 0
                negative_skip_ave = round(daily_data['Negative Skip Ave'].mean(), 2) if not daily_data.empty else 0
                total_skip_ave = round(daily_data['Total Skip Ave'].mean(), 2) if not daily_data.empty else 0
                connected_ave = round(daily_data['Connected Ave'].mean(), 2) if not daily_data.empty else 0
                talk_time_ave_seconds = daily_data['Talk Time Ave Seconds'].mean() if not daily_data.empty else 0
                ave_hours, ave_remainder = divmod(int(talk_time_ave_seconds), 3600)
                ave_minutes, ave_seconds = divmod(ave_remainder, 60)
                talk_time_ave_str = f"{ave_hours:02d}:{ave_minutes:02d}:{ave_seconds:02d}"
                overall_summary.append([
                    date_range_str, client, total_agents, total_connected, positive_skip_count, negative_skip_count, total_skip,
                    positive_skip_connected, negative_skip_connected, positive_skip_talk_time, negative_skip_talk_time,
                    positive_skip_ave, negative_skip_ave, total_skip_ave, formatted_talk_time, connected_ave, talk_time_ave_str
                ])
            overall_summary_df = pd.DataFrame(overall_summary, columns=[
                'Date Range', 'Client', 'Collectors', 'Total Connected', 'Positive Skip', 'Negative Skip', 'Total Skip',
                'Positive Skip Connected', 'Negative Skip Connected', 'Positive Skip Talk Time', 'Negative Skip Talk Time',
                'Positive Skip Ave', 'Negative Skip Ave', 'Total Skip Ave', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
            ])
            
            # Check if overall_summary_df is empty
            if overall_summary_df.empty:
                st.warning("No overall summary data available for the selected date range.")
            else:
                st.dataframe(overall_summary_df)

                # Generate the Excel file content with formatted tables
                excel_data = create_combined_excel_file(summary_dfs, overall_summary_df)

                # Use st.download_button for reliable download
                st.download_button(
                    label="Download All Results",
                    data=excel_data,
                    file_name="MC06_Monitoring_Results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
