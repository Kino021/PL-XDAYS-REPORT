import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Daily Remark Summary", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .reportview-container {
        background: #2E2E2E;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # Clean column names (remove leading/trailing spaces, make uppercase)
    df.columns = df.columns.str.strip().str.upper()

    # Convert 'Date' to datetime if it isn't already
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

    # Exclude rows where the date is a Sunday (weekday() == 6)
    df = df[df['DATE'].dt.weekday != 6]  # 6 corresponds to Sunday

    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Exclude rows where 'Debtor' contains 'DEFAULT_LEAD_'
    df = df[~df['DEBTOR'].str.contains("DEFAULT_LEAD_", case=False, na=False)]

    # Exclude rows where STATUS contains 'BP' (Broken Promise) or 'ABORT'
    df = df[~df['STATUS'].str.contains('ABORT', na=False)]

    # Exclude rows where REMARK contains certain keywords or phrases
    excluded_remarks = [
        "Broken Promise",
        "New files imported", 
        "Updates when case reassign to another collector", 
        "NDF IN ICS", 
        "FOR PULL OUT (END OF HANDLING PERIOD)", 
        "END OF HANDLING PERIOD"
    ]
    df = df[~df['REMARK'].str.contains('|'.join(excluded_remarks), case=False, na=False)]

    # Exclude rows where "CALL STATUS" contains "OTHERS"
    df = df[~df['CALL STATUS'].str.contains('OTHERS', case=False, na=False)]

    # Extract cycle from 'SERVICE NO.'
    df['CYCLE'] = df['SERVICE NO.'].str.extract(r'(CYCLE \d+)')

    def calculate_summary(df, remark_types, cycle_grouping=False):
        summary_table = pd.DataFrame(columns=[ 
            'CYCLE' if cycle_grouping else 'DAY', 'ACCOUNTS', 'TOTAL DIALED', 'PENETRATION RATE (%)', 'CONNECTED #', 
            'CONNECTED RATE (%)', 'CONNECTED ACC', 'PTP ACC', 'PTP RATE', 'TOTAL PTP AMOUNT', 
            'TOTAL BALANCE', 'CALL DROP #', 'SYSTEM DROP', 'CALL DROP RATIO #'
        ]) 

        df_filtered = df[df['REMARK TYPE'].isin(remark_types)]

        grouping_column = 'CYCLE' if cycle_grouping else df_filtered['DATE'].dt.date
        for cycle, group in df_filtered.groupby(grouping_column):
            accounts = group['ACCOUNT NO.'].nunique()
            total_dialed = group['ACCOUNT NO.'].count()
            connected = group[group['CALL STATUS'] == 'CONNECTED']['ACCOUNT NO.'].nunique()
            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None
            connected_acc = group[group['CALL STATUS'] == 'CONNECTED']['ACCOUNT NO.'].count()
            connected_rate = (connected_acc / total_dialed * 100) if total_dialed != 0 else None
            ptp_acc = group[(group['STATUS'].str.contains('PTP', na=False)) & (group['PTP AMOUNT'] != 0)]['ACCOUNT NO.'].nunique()
            ptp_rate = (ptp_acc / connected * 100) if connected != 0 else None
            total_ptp_amount = group[(group['STATUS'].str.contains('PTP', na=False)) & (group['PTP AMOUNT'] != 0)]['PTP AMOUNT'].sum()
            total_balance = group[(group['PTP AMOUNT'] != 0)]['BALANCE'].sum()
            system_drop = group[(group['STATUS'].str.contains('DROPPED', na=False)) & (group['REMARK BY'] == 'SYSTEM')]['ACCOUNT NO.'].count()
            call_drop_count = group[(group['STATUS'].str.contains('NEGATIVE CALLOUTS - DROP CALL', na=False)) & 
                                    (~group['REMARK BY'].str.upper().isin(['SYSTEM']))]['ACCOUNT NO.'].count()
            call_drop_ratio = (system_drop / connected_acc * 100) if connected_acc != 0 else None

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'CYCLE' if cycle_grouping else 'DAY': cycle,
                'ACCOUNTS': accounts,
                'TOTAL DIALED': total_dialed,
                'PENETRATION RATE (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'CONNECTED #': connected,
                'CONNECTED RATE (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'CONNECTED ACC': connected_acc,
                'PTP ACC': ptp_acc,
                'PTP RATE': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'TOTAL PTP AMOUNT': total_ptp_amount,
                'TOTAL BALANCE': total_balance,
                'CALL DROP #': call_drop_count,
                'SYSTEM DROP': system_drop,
                'CALL DROP RATIO #': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)

        return summary_table

    # Display summaries
    st.write("## Overall Combined Summary Table")
    combined_summary_table = calculate_summary(df, ['Predictive', 'Follow Up', 'Outgoing'])
    st.write(combined_summary_table)

    st.write("## Overall Predictive Summary Table")
    predictive_summary_table = calculate_summary(df, ['Predictive', 'Follow Up'])
    st.write(predictive_summary_table)

    st.write("## Overall Manual Summary Table")
    manual_summary_table = calculate_summary(df, ['Outgoing'])
    st.write(manual_summary_table)

    st.write("## Per Cycle Predictive Summary Table")
    cycle_predictive_summary = calculate_summary(df[df['CYCLE'].notna()], ['Predictive', 'Follow Up'], cycle_grouping=True)
    st.write(cycle_predictive_summary)

    st.write("## Per Cycle Manual Summary Table")
    cycle_manual_summary = calculate_summary(df[df['CYCLE'].notna()], ['Outgoing'], cycle_grouping=True)
    st.write(cycle_manual_summary)
