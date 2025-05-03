# coding: utf-8


import re
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def parse_html(html):
    """Parse content from various tags from OpenTable restaurants listing"""
    data, item = pd.DataFrame(), {}
    soup = BeautifulSoup(html, 'lxml')
    for i, resto in enumerate(soup.find_all('div', class_='ogUIF88Bm-M-')):  # 'rest-row-info'
        # resto.find('span', class_='rest-row-name-text').text
        item['name'] = resto.find('h6', class_='FhfgYo4tTD0-').text

        # resto.find('div', class_='booking')
        booking = resto.find('span', class_='gr6nnXdRSXE- IGV93qnDV0o- ZwYsiyOew-Q- NeZOcLtuYGk-')
        try:
            item['bookings'] = re.search(r'\d+', booking.text).group() if booking else 'NA'
        except AttributeError:
            print(f"No booking for index: {i} - resto: {resto}")

        # resto.find('div', class_='star-rating-score')
        rating = resto.find('div', class_='yEKDnyk-7-g-')
        try:
            item['rating'] = float(rating['aria-label'].split()[0]) if rating else 'NA'
        except AttributeError:
            print(f"No rating for index: {i} - resto: {resto}")

        # resto.find('span', class_='underline-hover')
        reviews = resto.find('a', class_='XmafYPXEv24-')
        item['reviews'] = int(
            re.search(r'\d+', reviews.text).group()) if reviews else 'NA'

        # .count('$')) #int(resto.find('div', class_='rest-row-pricing').find('i').text.count('$'))
        item['price'] = resto.find(
            'span', class_='Vk-xtpOrXcE-').text[len('Price: '):]

        cuisine_location = resto.find(
            'div', class_='_4QF0cXfwR9Q-').text.split(' • ')
        # resto.find('span', class_='rest-row-meta--cuisine rest-row-meta-text sfx1388addContent').text
        item['cuisine'] = cuisine_location[1]

        # resto.find('span', class_='rest-row-meta--location rest-row-meta-text sfx1388addContent').text
        item['location'] = cuisine_location[2]

        data[i] = pd.Series(item)
    return data.T


# Start selenium and click through pages until reach end
# store results by iteratively appending to csv file
driver = webdriver.Chrome()
url = "https://www.opentable.com/new-york-restaurant-listings"
driver.get(url)
wait = WebDriverWait(driver=driver, timeout=10)
page = collected = 0
driver.maximize_window()

last_height = 0

while page < 16: #True:
    sleep(2)
    ActionChains(driver=driver).move_to_element(driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/div/div/div[3]")).perform()
    driver.execute_script("window.scrollBy(0, 1000)")
    new_height = driver.execute_script("return document.body.scrollHeight")
    #sleep(1)
    print(f"{new_height} | {last_height}")
    if new_height == last_height:
        new_data = parse_html(driver.page_source)
        if new_data.empty:
            break
        if page == 0:
            new_data.to_csv('results.csv', index=False)
        elif page > 0:
            new_data.to_csv('results.csv', index=False, header=None, mode='a')
        
        page += 1
        collected += len(new_data)
        print(f'Page: {page} | Downloaded: {collected}')
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "gRlAhBweGeE-")))
        button = driver.find_element(By.LINK_TEXT, f"{page+1}")#.find_element(By.CSS_SELECTOR, "[aria-label='Go to the next page']")
        
    # find_element_by_link_text('Next').click()
        button.click()
        last_height = 0
    else:
        last_height = new_height

driver.close()
restaurants = pd.read_csv('results.csv')
print(restaurants)
