import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def get_restaurant_urls(zomato_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    response = requests.get(zomato_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    restaurant_urls = []
    for div in soup.find_all('div', class_='jumbo-tracker'):
        a_tag = div.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            full_url = "https://www.zomato.com" + href
            restaurant_urls.append(full_url.replace('info', 'menu'))
    
    return restaurant_urls

def get_high_res_menu_images(url, chrome_driver_path):
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        image_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//img[contains(@class, "sc-s1isp7-5") and contains(@class, "eisbVA")]')))
        image_urls = [img.get_attribute('src') for img in image_elements]
        # Attempt to get higher resolution images by modifying the URL pattern.
        high_res_image_urls = [img_url.replace('fit=around%7C200%3A200&crop=200%3A200%3B%2A%2C%2A', 'fit=around%7C600%3A600&crop=600%3A600%3B%2A%2C%2A') for img_url in image_urls]
        return high_res_image_urls

    finally:
        driver.quit()

def main(zomato_url, chrome_driver_path):
    restaurant_urls = get_restaurant_urls(zomato_url)
    all_high_res_images = {}

    for restaurant_url in restaurant_urls:
        print(f"Fetching images for {restaurant_url}")
        high_res_images = get_high_res_menu_images(restaurant_url, chrome_driver_path)
        all_high_res_images[restaurant_url] = high_res_images

    return all_high_res_images

def save_to_excel(data, filename='hotel_images.xlsx'):
    df = pd.DataFrame([(k, v) for k, urls in data.items() for v in urls], columns=['Restaurant URL', 'Image URL'])
    df.to_excel(filename, index=False)

zomato_url = "https://www.zomato.com/mumbai/restaurants"
chrome_driver_path = r'C:\Users\Bharathroyal\Downloads\chromedriver-win64\chromedriver.exe'
all_high_res_images = main(zomato_url, chrome_driver_path)
save_to_excel(all_high_res_images)