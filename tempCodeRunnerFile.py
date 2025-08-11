import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import re
import time
from datetime import datetime

def clean_filename(filename):
    # Удаляем все символы кроме букв, цифр и пробелов
    cleaned = re.sub(r'[^\w\s]', '', filename)
    # Заменяем пробелы на пустоту
    cleaned = re.sub(r'\s+', '', cleaned)
    return cleaned

def export_sales_to_csv():
    load_dotenv()
    
    db_params = {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    
    while True:
        try:
            engine = create_engine(connection_string)
            
            query = """
            SELECT sale_date, name, token_id, price_gun, item_url
            FROM cleared_sales
            ORDER BY sale_date
            """
            
            df = pd.read_sql(query, engine)
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, 'data', 'sales')
            os.makedirs(output_dir, exist_ok=True)
            
            for name in df['name'].unique():
                clean_name = clean_filename(name)
                item_df = df[df['name'] == name]
                
                output_file = os.path.join(output_dir, f'{clean_name}.csv')
                item_df.to_csv(output_file, index=False)
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] Exported {len(df['name'].unique())} files to {output_dir}/")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            engine.dispose()
            
        time.sleep(600)

if __name__ == '__main__':
    try:
        print("Starting continuous export (Press Ctrl+C to stop)")
        export_sales_to_csv()
    except KeyboardInterrupt:
        print("\nExport stopped by user")