import requests
from PIL import Image
from io import BytesIO
import pytesseract
import re
import pandas as pd
import pymysql

def perform_ocr(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text

def parse_items_and_prices(text):
    pattern = re.compile(r'(.+?)\s+(\d+\.?\d*)')
    items_prices = pattern.findall(text)
    return items_prices

def store_in_excel(items_prices, excel_path):
    if items_prices:
        df = pd.DataFrame(items_prices, columns=['Item', 'Price'])
        df.to_excel(excel_path, index=False)
        print(f"Data saved to {excel_path}")
    else:
        print(f"No items and prices detected for {excel_path}, skipping...")

def store_in_pymysql(items_prices, connection):
    if items_prices:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS menu_items (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            item VARCHAR(255),
                            price FLOAT
                        )''')
        for item, price in items_prices:
            cursor.execute('''INSERT INTO menu_items (item, price) VALUES (%s, %s)''', (item, float(price)))
        connection.commit()
        print("Data saved to MySQL database")
    else:
        print("No items and prices detected, skipping...")

# Connect to MySQL database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='scrap')

excel_file = "hotel_images.xlsx"
df = pd.read_excel(excel_file)

for index, row in df.iterrows():
    image_url = row["Image URL"]
    ocr_text = perform_ocr(image_url)
    items_prices = parse_items_and_prices(ocr_text)
    
    # Store in Excel
    excel_path = f'menu_items_{index}.xlsx'
    store_in_excel(items_prices, excel_path)
    
    # Store in MySQL
    store_in_pymysql(items_prices, connection)
connection.close()
