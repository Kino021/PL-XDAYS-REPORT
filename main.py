import streamlit as st
import pandas as pd

# Streamlit app title
st.title("📊 Productivity Per Agent Dashboard")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Ensure Date column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Ensure Call Duration and Talk Time Duration are numeric
    df['Call Duration'] = pd.to_numeric(df['Call Duration'], errors='coerce')
    df['Talk Time Duration'] = pd.to_numeric(df['Talk Time Duration'], errors='coerce')

    # Drop any rows where Date is NaT
    df = df.dropna(subset=['Date'])

    # UI Layout
    col1, col2 = st.columns(2)

    # 🔹 Summary Table by Day
    with col1:
        st.write("## 📆 Summary Table by Day")

        # Date Range Filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

        # Filter by date
        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        # Initialize Summary Table
        summary_table = pd.DataFrame(columns=[
            'Day', 'Client', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
        ])

        # Group by 'Date' and 'Client'
        for (date, client), group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Client']):
            valid_agents = group[group['Call Duration'].notna() & (group['Call Duration'] > 0)]
            total_agents = valid_agents['Remark By'].nunique()
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_talk_time = group['Talk Time Duration'].sum()

            # Format talk time
            formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s')).split()[2]

            # Averages
            connected_ave = total_connected / total_agents if total_agents > 0 else 0
            talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
            talk_time_ave_str = str(pd.to_timedelta(talk_time_ave, unit='s')).split()[2]

            # Append data
            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'Client': client,
                'Total Agents': total_agents,
                'Total Connected': total_connected,
                'Talk Time (HH:MM:SS)': formatted_talk_time,
                'Connected Ave': round(connected_ave, 2),
                'Talk Time Ave': talk_time_ave_str
            }])], ignore_index=True)

        # Display Table
        st.write(summary_table)

    # 🔹 Overall Summary per Date
    with col2:
        st.write("## 📊 Overall Summary per Date")

        overall_summary = pd.DataFrame(columns=[
            'Day', 'Total Agents', 'Total Connected', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
        ])

        # Group by 'Date'
        for date, group in filtered_df.groupby(filtered_df['Date'].dt.date):
            valid_agents = group[group['Call Duration'].notna() & (group['Call Duration'] > 0)]
            total_agents = valid_agents['Remark By'].nunique()
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_talk_time = group['Talk Time Duration'].sum()

            # Format talk time
            formatted_talk_time = str(pd.to_timedelta(total_talk_time, unit='s')).split()[2]

            # Averages
            connected_ave = total_connected / total_agents if total_agents > 0 else 0
            talk_time_ave = total_talk_time / total_agents if total_agents > 0 else 0
            talk_time_ave_str = str(pd.to_timedelta(talk_time_ave, unit='s')).split()[2]

            # Append data
            overall_summary = pd.concat([overall_summary, pd.DataFrame([{
                'Day': date,
                'Total Agents': total_agents,
                'Total Connected': total_connected,
                'Talk Time (HH:MM:SS)': formatted_talk_time,
                'Connected Ave': round(connected_ave, 2),
                'Talk Time Ave': talk_time_ave_str
            }])], ignore_index=True)

        # Display Table
        st.write(overall_summary)

else:
    st.warning("⚠ Please upload a CSV file to continue.")
