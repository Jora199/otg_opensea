import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
import os
from datetime import datetime, timedelta
import numpy as np

def get_rarity_style(rarity):
    rarity_colors = {
        'Common': ('#ffffff', 'common'),
        'Uncommon': ('#1eff00', 'uncommon'),
        'Rare': ('#0070dd', 'rare'),
        'Epic': ('#a335ee', 'epic'),
        'Legendary': ('#ff8000', 'legendary')
    }
    return rarity_colors.get(rarity, ('#ffffff', 'common'))

def load_current_price():
    price_path = os.path.join(os.path.dirname(__file__), 'data', 'current_price.csv')
    try:
        with open(price_path, 'r') as f:
            return float(f.read().strip())
    except:
        return 0.03

def load_sales_data():
    sales_dir = os.path.join(os.path.dirname(__file__), 'data', 'sales')
    items = {}
    
    if not os.path.exists(sales_dir):
        st.error(f"Directory not found: {sales_dir}")
        return {}
        
    for file in os.listdir(sales_dir):
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(sales_dir, file))
                if not df.empty:
                    item_name = df['name'].iloc[0]
                    rarity = df['rarity'].iloc[0] if 'rarity' in df.columns else None
                    
                    key = f"{item_name} {rarity}" if rarity else item_name
                    
                    items[key] = {
                        'data': df,
                        'rarity': rarity
                    }
                        
        except Exception as e:
            st.error(f"Error reading file {file}: {str(e)}")
            
    return items

def format_option(item_name):
    if item_name in items_data and items_data[item_name]['rarity']:
        rarity = items_data[item_name]['rarity']
        dots = {
            'Common': '⚪',
            'Uncommon': '🟢',
            'Rare': '🔵',
            'Epic': '🟣',
            'Legendary': '🟡'
        }
        return f"{dots.get(rarity, '⚪')} {item_name.rsplit(' ', 1)[0]}"
    return f"⚪ {item_name}"

def shorten_address(address, length=8):
    if not isinstance(address, str):
        return address
    return f"{address[:length]}...{address[-length:]}"

def format_opensea_link(address):
    return f"https://opensea.io/{address}"

def format_gunzscan_link(tx_hash):
    return f"https://gunzscan.io/tx/{tx_hash}"

def format_number(number, show_usd=False, gun_price=0.03, include_both=False):
    gun_formatted = ""
    usd_formatted = ""
    
    if number >= 1000000:
        gun_formatted = f"{number/1000000:.1f}M GUN"
    elif number >= 1000:
        gun_formatted = f"{number/1000:.1f}k GUN"
    else:
        gun_formatted = f"{number:.2f} GUN"
        
    usd_value = number * gun_price
    if usd_value >= 1000000:
        usd_formatted = f"${usd_value/1000000:.1f}M"
    elif usd_value >= 1000:
        usd_formatted = f"${usd_value/1000:.1f}k"
    else:
        usd_formatted = f"${usd_value:.2f}"
        
    if include_both:
        return gun_formatted, usd_formatted
    return usd_formatted if show_usd else gun_formatted

def format_metric_value(value, show_usd, gun_price):
    gun_value = format_number(value, False, gun_price)
    usd_value = format_number(value, True, gun_price)
    
    if show_usd:
        return f"""
            <div class="tooltip">
                {usd_value}
                <span class="tooltiptext">{gun_value}</span>
            </div>
        """
    else:
        return f"""
            <div class="tooltip">
                {gun_value}
                <span class="tooltiptext">{usd_value}</span>
            </div>
        """

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
            transition: opacity 0.2s ease;
        }
        .otg-logo a:hover img {
            opacity: 1;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .metric-container {
            margin-bottom: 1rem;
        }
        .metric-label {
            font-size: 14px;
            font-weight: normal;
            color: rgb(180, 180, 180);
            margin-bottom: 0.2rem;
        }
        .metric-value {
            font-size: 16px;
            font-weight: bold;
            color: rgb(250, 250, 250);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            background-color: rgba(0, 0, 0, 0.8);
            color: #fff;
            text-align: center;
            border-radius: 4px;
            padding: 5px 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            white-space: nowrap;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .twitter-container {
            position: fixed;
            bottom: 20px;
            left: 0;
            width: 250px;
            text-align: center;
        }
        .twitter-link {
            display: inline-block;
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.2s ease;
        }
        .twitter-link:hover {
            opacity: 1;
        }
        .twitter-icon {
            width: 40px;
            height: 40px;
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .sidebar-footer {
            position: relative;
            width: 100%;
            padding: 10px 0;
            text-align: center;
            margin-top: auto;
        }
        .footer-content {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            flex-direction: column;
            margin: 0 auto;
            width: 100%;
        }
        .footer-section {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 12px;
            width: 100%;
        }
        .footer-divider {
            width: 30px;
            height: 1px;
            background-color: rgba(255, 0, 0, 0.2);
            margin: 2px 0;
        }
        .footer-icon {
            height: 16px !important;
            width: 16px !important;
            transition: opacity 0.2s;
        }
        .sidebar-footer a {
            color: inherit;
            text-decoration: none;
            transition: opacity 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .sidebar-footer a:hover {
            opacity: 0.8;
        }

        [data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='flex: 1'></div>", unsafe_allow_html=True)

    st.sidebar.markdown("""
        <div class="otg-logo">
            <a href="https://store.epicgames.com/en-US/p/off-the-grid-7e3cc5" target="_blank">
                <img src="https://i.postimg.cc/cCs5d0hF/Off-The-Grid-Official-Master-Logo-jpeg-scaled.png" alt="Off The Grid">
            </a>
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
        
        .rarity-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .rarity-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .rarity-text {
            font-size: 0.9em;
            font-weight: normal;
        }
        .rarity-common { color: #ffffff; }
        .rarity-uncommon { color: #1eff00; }
        .rarity-rare { color: #0070dd; }
        .rarity-epic { color: #a335ee; }
        .rarity-legendary { color: #ff8000; }
        
        .select-item {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
        .select-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)
    
    items_data = load_sales_data()
    current_gun_price = load_current_price()
    
    st.sidebar.header("Filters")

    def format_option(item_name):
        if item_name in items_data and items_data[item_name]['rarity']:
            rarity = items_data[item_name]['rarity']
            dots = {
                'Common': '⚪',
                'Uncommon': '🟢',
                'Rare': '🔵',
                'Epic': '🟣',
                'Legendary': '🟡'
            }
            return f"{dots.get(rarity, '⚪')} {item_name.rsplit(' ', 1)[0]}"
        return f"⚪ {item_name}"

    selected_formatted_item = st.sidebar.selectbox(
        "Select Item",
        options=sorted(items_data.keys()),
        format_func=format_option,
        index=sorted(items_data.keys()).index("Golden Yank Hat Epic") if "Golden Yank Hat Epic" in items_data else 0
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
    
    df = items_data[selected_formatted_item]['data']
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

        if not filtered_df.empty and 'rarity' in filtered_df.columns:
            rarity = filtered_df['rarity'].iloc[0]
            color, rarity_class = get_rarity_style(rarity)
            # Remove rarity from item name if it exists at the end
            item_name = selected_formatted_item.rsplit(' ', 1)[0]
            st.markdown(f"""
                <div class="rarity-container">
                    <h3 style="margin: 0;">{item_name}</h3>
                    <span class="rarity-dot" style="background-color: {color};"></span>
                    <span class="rarity-text rarity-{rarity_class}">{rarity}</span>
                </div>
            """, unsafe_allow_html=True)

        info_col1, info_col2 = st.columns([1, 3])
        
        with info_col1:
            if not filtered_df.empty and 'image_url' in filtered_df.columns:
                image_url = filtered_df['image_url'].iloc[0]
                if image_url:
                    st.markdown('<div class="image-wrapper">', unsafe_allow_html=True)
                    st.image(image_url, width=300)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with info_col2:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Average Price</div>{format_metric_value(filtered_df['price_gun'].mean(), show_usd, current_gun_price)}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Total Volume</div>{format_metric_value(filtered_df['price_gun'].sum(), show_usd, current_gun_price)}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Minimum Price</div>{format_metric_value(filtered_df['price_gun'].min(), show_usd, current_gun_price)}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Maximum Price</div>{format_metric_value(filtered_df['price_gun'].max(), show_usd, current_gun_price)}</div>", unsafe_allow_html=True)
            with col3:
                unique_sellers = filtered_df['seller'].nunique()
                unique_buyers = filtered_df['buyer'].nunique()
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Unique Sellers</div>{unique_sellers}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Unique Buyers</div>{unique_buyers}</div>", unsafe_allow_html=True)
            with col4:
                total_transactions = len(filtered_df)
                unique_wallets = len(set(filtered_df['seller'].unique()) | set(filtered_df['buyer'].unique()))
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Total Transactions</div>{total_transactions}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-container'><div class='metric-label'>Total Unique Wallets</div>{unique_wallets}</div>", unsafe_allow_html=True)

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
            "Price: %{customdata[1]}",
            "USD: %{customdata[2]}"
            "<extra></extra>"
        ])

        gun_prices = [format_number(price, False, current_gun_price) for price in filtered_df['price_gun']]
        usd_prices = [format_number(price, True, current_gun_price) for price in filtered_df['price_gun']]

        fig.add_trace(go.Scatter(
            x=filtered_df['sale_date'],
            y=filtered_df['price_gun'],
            mode=scatter_mode,
            name='Sales',
            marker=dict(size=10, color='#FF0000'),
            line=dict(color='#CC0000'),
            hovertemplate=hover_template,
            customdata=list(zip(filtered_df['formatted_date'], gun_prices, usd_prices))
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
            if show_usd:
                table_html += f'<td>{format_number(row["price_gun"], True, current_gun_price)}</td>'
            else:
                gun_value = format_number(row["price_gun"], False, current_gun_price)
                usd_value = format_number(row["price_gun"], True, current_gun_price)
                table_html += f'<td><div class="tooltip">{gun_value}<span class="tooltiptext">{usd_value}</span></div></td>'
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

        st.sidebar.markdown("""
            <div class="sidebar-footer">
                <div class="footer-content">
                    <div class="footer-section">
                        <span>Powered by</span>
                        <a href="https://opensea.io/collection/off-the-grid" target="_blank">
                            <img class="footer-icon" src="https://storage.googleapis.com/opensea-static/Logomark/Logomark-Blue.svg" alt="OpenSea">
                        </a>
                    </div>
                    <div class="footer-divider"></div>
                    <div class="footer-section">
                        <span>Developed by</span>
                        <a href="https://x.com/blackpoint_team" target="_blank">
                            <img class="footer-icon" src="https://i.postimg.cc/L5wFLwgw/NEW-LOGO.png" alt="Twitter">
                        </a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()