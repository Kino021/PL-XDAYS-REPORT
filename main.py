with col2:
    st.write("## Overall Summary per Client")

    # Single container for all clients
    with st.container():
        # Format the date range string
        date_range_str = f"{start_date.strftime('%b %d %Y').upper()} - {end_date.strftime('%b %d %Y').upper()}"

        # Calculate average collectors per client from filtered_df and round up if .5 or greater
        avg_collectors_per_client = filtered_df.groupby(['Client', filtered_df['Date'].dt.date])['Remark By'].nunique().groupby('Client').mean().apply(lambda x: math.ceil(x) if x % 1 >= 0.5 else round(x))

        # Initialize a single summary list for all clients
        overall_summary = []

        # Group by 'Client' and calculate day-by-day averages
        for client, client_group in filtered_df.groupby('Client'):
            # Use the rounded average collectors
            total_agents = avg_collectors_per_client[client]
            total_connected = client_group[client_group['Call Status'] == 'CONNECTED']['Account No.'].count()

            # Sum Talk Time Duration in seconds
            total_talk_time_seconds = client_group['Talk Time Duration'].sum()

            # Convert total talk time to HH:MM:SS format without days
            hours, remainder = divmod(int(total_talk_time_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_talk_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Count Positive Skip
            positive_skip_count = sum(client_group['Status'].astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False))

            # Count Negative Skip
            negative_skip_count = client_group[client_group['Status'].isin(negative_skip_status)].shape[0]

            # Calculate Total Skip
            total_skip = positive_skip_count + negative_skip_count

            # Group by date to calculate day-by-day averages
            daily_data = client_group.groupby(client_group['Date'].dt.date).agg({
                'Remark By': 'nunique',  # Number of agents per day
                'Talk Time Duration': 'sum',  # Total talk time per day
                'Account No.': lambda x: x[client_group['Call Status'] == 'CONNECTED'].count(),  # Total connected per day
                'Status': [
                    lambda x: sum(x.astype(str).str.contains('|'.join(positive_skip_keywords), case=False, na=False)),  # Positive Skip per day
                    lambda x: x.isin(negative_skip_status).sum()  # Negative Skip per day
                ]
            })

            # Rename columns for clarity
            daily_data.columns = ['Collectors', 'Talk Time', 'Total Connected', 'Positive Skip', 'Negative Skip']

            # Calculate daily averages
            daily_data['Total Skip'] = daily_data['Positive Skip'] + daily_data['Negative Skip']
            daily_data['Positive Skip Ave'] = daily_data['Positive Skip'] / daily_data['Collectors']
            daily_data['Negative Skip Ave'] = daily_data['Negative Skip'] / daily_data['Collectors']
            daily_data['Total Skip Ave'] = daily_data['Total Skip'] / daily_data['Collectors']
            daily_data['Connected Ave'] = daily_data['Total Connected'] / daily_data['Collectors']
            daily_data['Talk Time Ave Seconds'] = daily_data['Talk Time'] / daily_data['Collectors']

            # Compute the mean of daily averages
            positive_skip_ave = round(daily_data['Positive Skip Ave'].mean(), 2) if not daily_data.empty else 0
            negative_skip_ave = round(daily_data['Negative Skip Ave'].mean(), 2) if not daily_data.empty else 0
            total_skip_ave = round(daily_data['Total Skip Ave'].mean(), 2) if not daily_data.empty else 0
            connected_ave = round(daily_data['Connected Ave'].mean(), 2) if not daily_data.empty else 0
            talk_time_ave_seconds = daily_data['Talk Time Ave Seconds'].mean() if not daily_data.empty else 0

            # Convert average talk time to HH:MM:SS format
            ave_hours, ave_remainder = divmod(int(talk_time_ave_seconds), 3600)
            ave_minutes, ave_seconds = divmod(ave_remainder, 60)
            talk_time_ave_str = f"{ave_hours:02d}:{ave_minutes:02d}:{ave_seconds:02d}"

            # Append results to the overall summary
            overall_summary.append([
                date_range_str, client, total_agents, total_connected, positive_skip_count, negative_skip_count, total_skip,
                positive_skip_ave, negative_skip_ave, total_skip_ave, formatted_talk_time, connected_ave, talk_time_ave_str
            ])

        # Convert to DataFrame and display all clients in one table
        overall_summary_df = pd.DataFrame(overall_summary, columns=[
            'Date Range', 'Client', 'Collectors', 'Total Connected', 'Positive Skip', 'Negative Skip', 'Total Skip',
            'Positive Skip Ave', 'Negative Skip Ave', 'Total Skip Ave', 'Talk Time (HH:MM:SS)', 'Connected Ave', 'Talk Time Ave'
        ])
        st.write(overall_summary_df)
