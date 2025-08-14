import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
import os
from datetime import datetime, timedelta
import numpy as np

def load_current_price():
    price_path = os.path.join(os.path.dirname(__file__), 'data', 'current_price.csv')
    
    try:
        with open(price_path, 'r') as f:
            return float(f.read().strip())
    except:
        return 0.03


def load_sales_data():
    sales_dir = os.path.join(os.path.dirname(__file__), 'data', 'sales')
    
    if not os.path.exists(sales_dir):
        st.error(f"Directory not found: {sales_dir}")
        st.error(f"Current working directory: {os.getcwd()}")
        st.error(f"Contents of current directory: {os.listdir(os.getcwd())}")
        return {}
        
    items = {}
    for file in os.listdir(sales_dir):
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(sales_dir, file))
                if not df.empty:
                    item_name = df['name'].iloc[0]
                    items[item_name] = df
        except Exception as e:
            st.error(f"Error reading file {file}: {str(e)}")
    return items

def shorten_address(address, length=8):
    if not isinstance(address, str):
        return address
    return f"{address[:length]}...{address[-length:]}"

def format_opensea_link(address):
    return f"https://opensea.io/{address}"

def format_gunzscan_link(tx_hash):
    return f"https://gunzscan.io/tx/{tx_hash}"

def format_number(number, show_usd=False, gun_price=0.03):
    if show_usd:
        usd_value = number * gun_price
        if usd_value >= 1000000:
            return f"${usd_value/1000000:.1f}M"
        if usd_value >= 1000:
            return f"${usd_value/1000:.1f}k"
        return f"${usd_value:.2f}"
    else:
        if number >= 1000000:
            return f"{number/1000000:.1f}M GUN"
        if number >= 1000:
            return f"{number/1000:.1f}k GUN"
        return f"{number:.2f} GUN"

def main():
    st.set_page_config(page_title='Off The Grid', page_icon="📊", layout="wide")
    
    st.markdown("""
        <style>
        .otg-logo {
            margin-bottom: 20px;
            padding: 5px;
        }
        .otg-logo img {
            width: 100%;
            max-width: 150px;
            height: auto;
            display: block;
            margin: 0 auto;
            opacity: 0.9;
            transition: opacity 0.2s ease;  /* Добавляем плавный переход */
        }
        .otg-logo a:hover img {
            opacity: 1;  /* Повышаем яркость при наведении */
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
        <div class="otg-logo">
            <a href="https://store.epicgames.com/en-US/p/off-the-grid-7e3cc5" target="_blank">
                <img src="https://i.postimg.cc/cCs5d0hF/Off-The-Grid-Official-Master-Logo-jpeg-scaled.png" alt="Off The Grid">
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: var(--background-color);  /* Используем системную переменную цвета фона */
            padding: 10px 0;
            text-align: center;
            border-top: 1px solid rgba(255, 0, 0, 0.2);
        }
        .footer-content {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .footer img {
            height: 20px;
            vertical-align: middle;
        }
        .footer a {
            color: inherit;  /* Наследуем цвет текста от родителя */
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        [data-theme="light"] .footer {
            background-color: #ffffff;
            color: #0e1117;
        }
        [data-theme="dark"] .footer {
            background-color: #0e1117;
            color: #ffffff;
        }
        </style>
        
        <div class="footer">
            <div class="footer-content">
                <span>Powered by</span>
                <a href="https://opensea.io" target="_blank">
                    <img src="https://storage.googleapis.com/opensea-static/Logomark/Logomark-Blue.svg" alt="OpenSea">
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .sales-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            border: 2px solid #FF0000;
        }
        .sales-table thead tr {
            background-color: var(--background-color);
            color: var(--text-color);
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #FF0000;
        }
        .sales-table th,
        .sales-table td {
            padding: 12px 15px;
        }
        .sales-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        .sales-table tbody tr:last-of-type {
            border-bottom: 2px solid #FF0000;
        }
        [data-testid="stAppViewContainer"] {
            background-color: var(--background-color);
        }
        .sales-table .link-cell a {
            color: inherit;
            text-decoration: underline;
        }
        .sales-table .link-cell a:hover {
            opacity: 0.8;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 5px;
            margin-top: 20px;
        }
        .page-number {
            padding: 5px 10px;
            border: 1px solid #FF0000;
            border-radius: 3px;
            color: inherit;
            text-decoration: none;
        }
        .page-number.active {
            background-color: #FF0000;
            color: white;
        }
        .page-number:hover:not(.active) {
            background-color: rgba(255, 0, 0, 0.1);
        }
        .image-container {
            padding: 10px;
            margin-bottom: 20px;
            background-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)
    
    items_data = load_sales_data()
    current_gun_price = load_current_price()
    
    st.sidebar.header("Filters")
    
    selected_item = st.sidebar.selectbox(
        "Select Item",
        options=sorted(items_data.keys()),
        index=0
    )
    
    show_trendline = st.sidebar.checkbox('Trend line', value=False)
    if show_trendline:
        trend_type = st.sidebar.selectbox(
            "Trend type",
            options=['Linear', 'Polynomial'],
            index=0
        )
        if trend_type == 'Polynomial':
            degree = st.sidebar.slider('Polynomial degree', 2, 5, 2)
    
    show_volume = st.sidebar.checkbox('Volume', value=False)
    connect_dots = st.sidebar.checkbox('Connect points', value=False)
    
    df = items_data[selected_item]
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    min_date = df['sale_date'].min()
    max_date = df['sale_date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    show_usd = st.sidebar.checkbox('USD', value=False)
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['sale_date'].dt.date >= start_date) & (df['sale_date'].dt.date <= end_date)
        filtered_df = df[mask]
        filtered_df['formatted_date'] = filtered_df['sale_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        st.markdown(f"### {selected_item}")
        info_col1, info_col2 = st.columns([1, 3])
        
        with info_col1:
            if not filtered_df.empty and 'image_url' in filtered_df.columns:
                image_url = filtered_df['image_url'].iloc[0]
                if image_url:
                    st.markdown('<div class="image-wrapper">', unsafe_allow_html=True)
                    st.image(
                        image_url,
                        width=300
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with info_col2:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Price", format_number(filtered_df['price_gun'].mean(), show_usd, current_gun_price))
                st.metric("Total Volume", format_number(filtered_df['price_gun'].sum(), show_usd, current_gun_price))
            with col2:
                st.metric("Minimum Price", format_number(filtered_df['price_gun'].min(), show_usd, current_gun_price))
                st.metric("Maximum Price", format_number(filtered_df['price_gun'].max(), show_usd, current_gun_price))
            with col3:
                unique_sellers = filtered_df['seller'].nunique()
                unique_buyers = filtered_df['buyer'].nunique()
                st.metric("Unique Sellers", unique_sellers)
                st.metric("Unique Buyers", unique_buyers)
            with col4:
                total_transactions = len(filtered_df)
                unique_wallets = len(set(filtered_df['seller'].unique()) | set(filtered_df['buyer'].unique()))
                st.metric("Total Transactions", total_transactions)
                st.metric("Total Unique Wallets", unique_wallets)

            with st.expander("Wallet Activity Details"):
                wallet_col1, wallet_col2 = st.columns(2)
                
                with wallet_col1:
                    st.subheader("Top Sellers")
                    top_sellers = (filtered_df['seller']
                                 .value_counts()
                                 .head(5)
                                 .reset_index())
                    top_sellers.columns = ['Address', 'Sales']
                    
                    sellers_html = '<table class="sales-table"><tbody>'
                    for _, row in top_sellers.iterrows():
                        sellers_html += '<tr>'
                        sellers_html += (f'<td class="link-cell"><a href="{format_opensea_link(row["Address"])}" '
                                       f'target="_blank">{shorten_address(row["Address"])}</a></td>')
                        sellers_html += f'<td>{row["Sales"]} sales</td>'
                        sellers_html += '</tr>'
                    sellers_html += '</tbody></table>'
                    st.markdown(sellers_html, unsafe_allow_html=True)
                
                with wallet_col2:
                    st.subheader("Top Buyers")
                    top_buyers = (filtered_df['buyer']
                                .value_counts()
                                .head(5)
                                .reset_index())
                    top_buyers.columns = ['Address', 'Purchases']
                    
                    buyers_html = '<table class="sales-table"><tbody>'
                    for _, row in top_buyers.iterrows():
                        buyers_html += '<tr>'
                        buyers_html += (f'<td class="link-cell"><a href="{format_opensea_link(row["Address"])}" '
                                      f'target="_blank">{shorten_address(row["Address"])}</a></td>')
                        buyers_html += f'<td>{row["Purchases"]} purchases</td>'
                        buyers_html += '</tr>'
                    buyers_html += '</tbody></table>'
                    st.markdown(buyers_html, unsafe_allow_html=True)

        fig = go.Figure()

        scatter_mode = 'lines+markers' if connect_dots else 'markers'
        
        sales_formatted = [format_number(price, show_usd, current_gun_price) for price in filtered_df['price_gun']]

        hover_template = "<br>".join([
            "Date: %{customdata[0]}",
            "Price: %{customdata[1]}"
            "<extra></extra>"
        ])

        fig.add_trace(go.Scatter(
            x=filtered_df['sale_date'],
            y=filtered_df['price_gun'],
            mode=scatter_mode,
            name='Sales',
            marker=dict(size=10, color='#FF0000'),
            line=dict(color='#CC0000'),
            hovertemplate=hover_template,
            customdata=list(zip(filtered_df['formatted_date'], sales_formatted))
        ))

        if show_volume:
            daily_volumes = filtered_df.groupby(filtered_df['sale_date'].dt.date).agg({
                'price_gun': ['sum', 'count']
            }).reset_index()
            daily_volumes.columns = ['date', 'volume_gun', 'count']
            
            volume_dates = [datetime.combine(date, datetime.min.time()) + timedelta(hours=12) for date in daily_volumes['date']]
            
            volume_hover_template = "<br>".join([
                "Date: %{x}",
                "Volume: %{customdata[1]}",
                "Transactions: %{customdata[0]}"
                "<extra></extra>"
            ])

            volume_formatted = [format_number(vol, show_usd, current_gun_price) for vol in daily_volumes['volume_gun']]
            
            y_values = daily_volumes['volume_gun'] if not show_usd else daily_volumes['volume_gun'] * current_gun_price
            
            fig.add_trace(go.Bar(
                x=volume_dates,
                y=y_values,
                name='Volume',
                marker_color='rgba(139,0,0,0.3)',
                yaxis='y2',
                hovertemplate=volume_hover_template,
                customdata=list(zip(daily_volumes['count'], volume_formatted))
            ))

        if show_trendline and len(filtered_df) > 1:
            x_numeric = (filtered_df['sale_date'] - filtered_df['sale_date'].min()).dt.total_seconds()
            
            if trend_type == 'Linear':
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, filtered_df['price_gun'])
                trend_y = slope * x_numeric + intercept
                
                if abs(r_value) < 0.5:
                    st.sidebar.warning('⚠️ Trend line may be unreliable due to high price volatility and limited data')
            else:
                coeffs = np.polyfit(x_numeric, filtered_df['price_gun'], degree)
                trend_y = np.polyval(coeffs, x_numeric)
            
            fig.add_trace(go.Scatter(
                x=filtered_df['sale_date'],
                y=trend_y,
                mode='lines',
                name='Trend',
                line=dict(color='#00FF00', width=2, dash='dash'),
                hoverinfo='skip'
            ))
        
        price_label = "Price (USD)" if show_usd else "Price (GUN)"
        fig.update_layout(
            hovermode='closest',
            height=600,
            showlegend=False,
            xaxis_title="Date",
            yaxis_title=price_label,
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            ) if show_volume else dict()
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        query_params = st.query_params
        page = int(query_params.get("page", 1))
        
        filtered_df = filtered_df.sort_values('sale_date', ascending=False)

        items_per_page = 10
        total_pages = len(filtered_df) // items_per_page + (1 if len(filtered_df) % items_per_page > 0 else 0)

        col1, col2 = st.columns([8, 2])
        with col2:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered_df.iloc[start_idx:end_idx]

        table_html = '<table class="sales-table"><thead><tr>'
        columns = ['Date', 'Price', 'Seller', 'Buyer', 'Tx Hash', 'View']
        for col in columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'

        for _, row in page_data.iterrows():
            table_html += '<tr>'
            table_html += f'<td>{row["formatted_date"]}</td>'
            table_html += f'<td>{format_number(row["price_gun"], show_usd, current_gun_price)}</td>'
            table_html += (f'<td class="link-cell"><a href="{format_opensea_link(row["seller"])}" target="_blank">'
                        f'{shorten_address(row["seller"])}</a></td>')
            table_html += (f'<td class="link-cell"><a href="{format_opensea_link(row["buyer"])}" target="_blank">'
                        f'{shorten_address(row["buyer"])}</a></td>')
            table_html += (f'<td class="link-cell"><a href="{format_gunzscan_link(row["transaction_hash"])}" target="_blank">'
                        f'{shorten_address(row["transaction_hash"])}</a></td>')
            table_html += (f'<td class="link-cell"><a href="{row["item_url"]}" target="_blank">View Item</a></td>')
            table_html += '</tr>'

        table_html += '</tbody></table>'
        
        st.markdown(table_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()