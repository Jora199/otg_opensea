import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

def load_sales_data():
    sales_dir = os.path.join(os.path.dirname(__file__), 'data', 'sales')
    items = {}
    
    for file in os.listdir(sales_dir):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(sales_dir, file))
            if not df.empty:
                item_name = df['name'].iloc[0]
                items[item_name] = df
    
    return items

def main():
    st.set_page_config(page_title="GunZ Market Analysis", page_icon="📊", layout="wide")
    st.title("GunZ Market Analysis")
    
    # Загрузка данных
    items_data = load_sales_data()
    
    # Сайдбар с фильтрами
    st.sidebar.header("Filters")
    
    # Выбор предмета
    selected_item = st.sidebar.selectbox(
        "Select Item",
        options=sorted(items_data.keys()),
        index=0
    )
    
    # Получаем данные выбранного предмета
    df = items_data[selected_item]
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    # Определяем минимальную и максимальную даты
    min_date = df['sale_date'].min()
    max_date = df['sale_date'].max()
    
    # Выбор временного интервала
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
        
        # График
        fig = px.scatter(
            filtered_df,
            x='sale_date',
            y='price_gun',
            title=f'Sales History for {selected_item}',
            labels={
                'sale_date': 'Date',
                'price_gun': 'Price (GUN)'
            }
        )
        
        # Форматируем дату для отображения
        filtered_df['formatted_date'] = filtered_df['sale_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Создаем кастомный текст для hover
        fig.update_traces(
            marker=dict(size=10),
            hovertemplate="<br>".join([
                "Date: %{customdata[0]}",
                "Price: %{y:.2f} GUN",
                "<extra></extra>"
            ]),
            customdata=filtered_df[['formatted_date']]
        )
        
        fig.update_layout(
            hovermode='closest',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Статистика
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"{filtered_df['price_gun'].mean():.2f} GUN")
        with col2:
            st.metric("Minimum Price", f"{filtered_df['price_gun'].min():.2f} GUN")
        with col3:
            st.metric("Maximum Price", f"{filtered_df['price_gun'].max():.2f} GUN")
        
        # Добавляем ссылки отдельным списком
        if st.checkbox("Show URLs"):
            st.markdown("### Sale URLs")
            for _, row in filtered_df.iterrows():
                st.markdown(f"- [{row['formatted_date']} - {row['price_gun']} GUN]({row['item_url']})")

if __name__ == "__main__":
    main()