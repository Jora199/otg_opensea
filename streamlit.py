import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
import os
from datetime import datetime, timedelta

def load_img_data():
    # Изменен путь к файлу изображений
    img_path = os.path.join(os.path.dirname(__file__), 'data', 'img.csv')
    
    if os.path.exists(img_path):
        return dict(zip(pd.read_csv(img_path)['name'], pd.read_csv(img_path)['img']))
    return {}

def load_sales_data():
    # Изменен путь к директории с данными
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

def main():
    st.set_page_config(page_title="GunZ Market Analysis", page_icon="📊", layout="wide")
    
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
            color: white;
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
        .sales-table tbody tr:nth-of-type(even) {
            background-color: #2b2b2b;
        }
        .sales-table tbody tr:last-of-type {
            border-bottom: 2px solid #FF0000;
        }
        .sales-table .link-cell a {
            color: inherit;
            text-decoration: underline;
        }
        .sales-table .link-cell a:hover {
            opacity: 0.8;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("GunZ Market Analysis")
    
    items_data = load_sales_data()
    img_data = load_img_data()
    
    st.sidebar.header("Filters")
    
    selected_item = st.sidebar.selectbox(
        "Select Item",
        options=sorted(items_data.keys()),
        index=0
    )
    
    show_trendline = st.sidebar.checkbox('Show trend line', value=False)
    
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
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['sale_date'].dt.date >= start_date) & (df['sale_date'].dt.date <= end_date)
        filtered_df = df[mask]
        filtered_df['formatted_date'] = filtered_df['sale_date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        st.markdown("### Item Information")
        info_col1, info_col2 = st.columns([1, 3])
        
        with info_col1:
            if selected_item in img_data:
                st.image(img_data[selected_item], width=200)
        
        with info_col2:
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Average Price", f"{filtered_df['price_gun'].mean():.2f} GUN")
            with metrics_col2:
                st.metric("Minimum Price", f"{filtered_df['price_gun'].min():.2f} GUN")
            with metrics_col3:
                st.metric("Maximum Price", f"{filtered_df['price_gun'].max():.2f} GUN")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=filtered_df['sale_date'],
            y=filtered_df['price_gun'],
            mode='markers',
            name='Sales',
            marker=dict(size=10, color='#FF0000'),
            hovertemplate="<br>".join([
                "Date: %{customdata[0]}",
                "Price: %{y:.2f} GUN",
                "<extra></extra>"
            ]),
            customdata=filtered_df[['formatted_date']]
        ))

        if show_trendline and len(filtered_df) > 1:
            x_numeric = (filtered_df['sale_date'] - filtered_df['sale_date'].min()).dt.total_seconds()
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, filtered_df['price_gun'])
            
            if abs(r_value) < 0.5:
                st.sidebar.warning('⚠️ Trend line may be unreliable due to high price volatility and limited data')
            
            trend_y = slope * x_numeric + intercept
            
            fig.add_trace(go.Scatter(
                x=filtered_df['sale_date'],
                y=trend_y,
                mode='lines',
                name='Trend',
                line=dict(color='#00FF00', width=2, dash='dash'),
                hoverinfo='skip'
            ))
        
        fig.update_layout(
            hovermode='closest',
            height=600,
            showlegend=False,
            xaxis_title="Date",
            yaxis_title="Price (GUN)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sort DataFrame by sale_date in descending order
        filtered_df = filtered_df.sort_values('sale_date', ascending=False)
        
        table_html = '<table class="sales-table"><thead><tr>'
        columns = ['Date', 'Price (GUN)', 'Seller', 'Buyer', 'Tx Hash', 'View']
        for col in columns:
            table_html += f'<th>{col}</th>'
        table_html += '</tr></thead><tbody>'
        
        for idx, row in filtered_df.iterrows():
            table_html += '<tr>'
            table_html += f'<td>{row["formatted_date"]}</td>'
            table_html += f'<td>{row["price_gun"]:.2f}</td>'
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