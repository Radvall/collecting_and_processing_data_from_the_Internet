"""
Вариант 2
Необходимо собрать информацию по продуктам питания с сайта: Список протестированных продуктов на сайте
Росконтроль.рф Приложение должно анализировать несколько страниц сайта (вводим через input или аргументы).

Получившийся список должен содержать:

    Наименование продукта.
    Все параметры (Безопасность, Натуральность, Пищевая ценность, Качество)
    Общую оценку
    Сайт, откуда получена информация.

Общий результат можно вывести с помощью dataFrame через Pandas. Сохраните в json либо csv.
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import lxml
import tabulate

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
}


def get_products_roscontrol(page_count: int) -> 'df':
    """Сбор информации по продуктам питания с сайта roscontrol.com"""

    site_name = 'https://roscontrol.com'

    # Получаем URL продуктов со страниц page_count
    product_urls = []
    for el in range(page_count):
        url = f'https://roscontrol.com/products/?tested=tested&page={el + 1}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        product_on_page = [site_name + i['href'] for i in
                           soup.find_all(class_='block-product-catalog__item js-activate-rate '
                                                'util-hover-shadow clear')]
        product_urls = product_urls + product_on_page

    # Получаем подробную информацию о продуктах
    product_names, site_names = [], []
    subcategory_names, category_names = [], []
    total_ratings, safety_ratings, others_ratings, urls = [], [], [], []
    for u in product_urls:
        response = requests.get(u, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        # Получаем название продукта
        product_name = soup.find(class_='main-title testlab-caption-products util-inline-block').text
        product_names.append(product_name)

        # Получаем название категорий
        categories = [i.text for i in soup.select('.breadcrumb > ol > li > a span')]
        category_names.append(categories[1])
        subcategory_names.append(categories[2])

        # Получаем рейтинги
        # Для всех продуктов одинаковые параметры: "Общая оценка", "Безопасность".
        # Их и имеет смысл вносить в DataFrame. Остальные параметры добавлены в столбец "others_ratings".
        ratings = [i.text for i in soup.select('div.rate-item div span')]
        ratings_name = [i.text.strip() for i in soup.select('div.rate-item div div ') if len(i.text.strip()) > 0]
        total_rating = [i.text for i in soup.select('#product__single-rev-total > div:nth-child(1)')]
        safety_ratings.append(ratings[ratings_name.index('Безопасность')])
        total_ratings.append(total_rating[0])

        # Получаем others_ratings
        others_name = ratings_name.copy()
        others_name.remove('Безопасность')
        others_rating = ratings.copy()
        others_rating.pop(ratings_name.index('Безопасность'))
        # Собираем строку для DataFrame
        others_string = ''
        for i, name in enumerate(others_name):
            rating_string = f'{name} - {others_rating[i]} '
            others_string += rating_string
        others_ratings.append(others_string)

        # Добавляем сайт, откуда получена информация
        site_names.append(site_name)

    # Итоговый словарь
    product_detail = {
        'product_name': product_names,
        'category_name': category_names,
        'subcategory_name': subcategory_names,
        'safety_rating': safety_ratings,
        'others_ratings': others_ratings,
        'total_rating': total_ratings,
        'product_link': product_urls,
        'site_name': site_names
    }

    df = pd.DataFrame(product_detail)
    return df


result_df = get_products_roscontrol(page_count=5)

print(result_df.to_markdown())
# Сохраняем результат в json файл
result_df.to_json('task_1.json')
