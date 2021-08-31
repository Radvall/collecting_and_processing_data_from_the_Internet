from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import pymongo
from pymongo import MongoClient

from pprint import pprint
import re
import random
import time


chrome_options = Options()
chrome_options.add_argument('--window-size=1200,700')

driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)
driver.get('https://goldfish-cafe.ru/')

# Выбираем город
current_area = driver.find_element_by_xpath("//a[@aria-current='page']")
if current_area.text is not 'Ваш город: Калуга':
    order_district = driver.find_element_by_id('menu-item-2136')
    order_district.click()
    city = driver.find_element_by_xpath("//ul[@class = 'sub-menu']/li/a[contains(text(), 'Калуга')]")
    city.click()

# Загружаем все блюда
try:
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                    "//*[@class='nm-infload-controls button-mode']/"
                                                                    "a[@class = 'nm-infload-btn']"))).click()
except Exception as e:
    print('Все элементы загружены')
    print("type error: " + str(e))

# Подключение к локальному серверу MongoDB.
client = MongoClient('127.0.0.1', 27017)
db = client['dishes_db']
dishes_db = db.dishes_db

# Для записи в БД выбираем название блюда и ссылку на него
dishes = driver.find_elements_by_xpath("//li[contains(@class, 'product type-product')]")
for dish in dishes:
    title = dish.find_element_by_xpath(".//h3[@class = 'woocommerce-loop-product__title']/a").text
    url = dish.find_element_by_xpath(".//div[@class = 'nm-shop-loop-thumbnail']/a").get_attribute('href')
    # Обработка возможных вариантов отображения цены
    prices = dish.find_elements_by_xpath(".//span[@class = 'woocommerce-Price-amount amount']")
    price = [re.sub("\D", "", i.text) for i in prices]
    if len(price) > 1:
        if float(price[0]) > float(price[1]):  # Скидка
            price = 0.01 * float(price[1])
        else:  # Диапазон цен
            price = 0.5 * (float(price[0]) + float(price[1]))
    else:
        price = float(price[0])

    dict_dish = {
        'title': title,
        'url': url,
        'price': price
    }
    dishes_db.insert_one(dict_dish)

print(f'Количество документов в коллекции MongoDB: \n{db.dishes_db.count_documents({})}')

# Выбираем случайное блюдо
random_index = random.randint(0, len(dishes) - 1)
add_to_basket_url = dishes[random_index].\
    find_element_by_xpath(".//div[@class='nm-shop-loop-actions']/a").get_attribute('href')
# Добавляем случайное блюдо в корзину
driver.get(add_to_basket_url)
time.sleep(3)
# Переход в корзину
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@class = "
                                                                      "'button checkout wc-forward']"))).click()

# Заполняем пользовательские данные
name = driver.find_element_by_id("billing_first_name")
phone = driver.find_element_by_id("billing_phone")
email = driver.find_element_by_id("billing_email")
city_check = driver.find_element_by_id("billing_new_fild10")

name.send_keys('ИМЯ')
phone.send_keys('+99999999999')
email.send_keys('email АДРЕС')
city_check.click()

cart_total = driver.find_element_by_xpath("//span[@class = 'woocommerce-Price-amount amount']")
cart_total = re.sub("\D", "", cart_total.text)
if float(cart_total / 100) < 500:
    print("Доставка будет платной")
