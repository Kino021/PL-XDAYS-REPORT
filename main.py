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
            ave_hours, ave_remainder = divmod(int(talk_time_ave_seconds), 3600)  # Fixed line
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
        
        if overall_summary_df.empty:
            st.warning("No overall summary data available for the selected date range.")
        else:
            st.dataframe(overall_summary_df)

            excel_data = create_combined_excel_file(summary_dfs, overall_summary_df)
            st.download_button(
                label="Download All Results",
                data=excel_data,
                file_name="MC06_Monitoring_Results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
