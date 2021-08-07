"""
Задание
Вариант 2
Необходимо собрать информацию по продуктам питания с сайтов:

    Роскачество официальный сайт. Исследование качества продуктов питания | Рейтинг товаров.
    Список протестированных продуктов на сайте Росконтроль.рф
    Получившийся список должен содержать:
    Наименование продукта.
    Категорию продукта (например «Бакалея»).
    Подкатегорию продукта (например «Рис круглозерный»).
    Параметр «Безопасность».
    Параметр «Качество».
    Общий балл.
    Сайт, откуда получена информация. ### Структура должна быть одинаковая для продуктов с обоих сайтов.
    Общий результат можно вывести с помощью dataFrame через Pandas.
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
from fake_headers import Headers

headers = Headers(headers=True).generate()

URL_rskrf = 'https://rskrf.ru/ratings/produkty-pitaniya'
URL_roscontrol = 'https://roscontrol.com/products/?tested=tested'


def get_products_rskrf(url: str) -> 'df':
    """Сбор информации по продуктам питания с сайта rskrf.ru"""

    site_name = 'https://rskrf.ru'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # Получаем URL продуктов
    product_good_urls = [site_name + i['href'] for i in soup.select('.rgoods-section-good ol li div div div a')]
    product_poor_urls = [site_name + i['href'] for i in soup.select('.rgoods-section-poor ol li div div div a')]
    product_urls = product_good_urls + product_poor_urls

    # Получаем подробную информацию о продукте
    product_names, site_names = [], []
    subcategory_names, category_names, total_ratings, safety_ratings, quality_ratings, urls = [], [], [], [], [], []

    for u in product_urls:

        response = requests.get(u, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        # Получаем название и категорию продута
        names = [i.text for i in soup.select('li.breadcrumb-item')]
        category_names.append(names[2])
        product_name = names[3]
        product_names.append(product_name)

        # Первое или два первых слова из названия будут подкатегорией
        if len(product_name.split()[1]) > 2:
            subcategory_names.append(product_name.split()[0] + ' ' + product_name.split()[1])
        else:
            subcategory_names.append(product_name.split()[0])

        # Получаем рейтинги
        rating = [i.text for i in soup.select('div.rating-item span')]
        total_rating = rating[rating.index('Общий рейтинг') + 1]
        if total_rating:
            total_ratings.append(total_rating)
        else:
            total_ratings.append(0)
        safety_ratings.append(rating[rating.index('Безопасность ') + 1])
        quality_ratings.append(rating[rating.index('Качество') + 1])

        # Добавляем сайт, откуда получена информация
        site_names.append(site_name)

    product_detail = {
        'product_name': product_names,
        'category_name': category_names,
        'subcategory_name': subcategory_names,
        'safety_rating': safety_ratings,
        'quality_rating': quality_ratings,
        'total_rating': total_ratings,
        'product_link': product_urls,
        'site_name': site_names
    }
    df = pd.DataFrame(product_detail)
    return df


def get_urls(url: str, change_range=True) -> 'df':
    """Сбор информации по продуктам питания с сайта roscontrol.com"""

    site_name = 'https://roscontrol.com'

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # Получаем URL продуктов
    product_urls = [site_name + i['href'] for i in soup.find_all(class_='block-product-catalog__item js-activate-rate '
                                                                        'util-hover-shadow clear')]
    # Получаем подробную информацию о продуктах
    product_names, site_names = [], []
    subcategory_names, category_names, total_ratings, safety_ratings, quality_ratings, urls = [], [], [], [], [], []
    for u in product_urls:
        response = requests.get(u, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        # Получаем название продукта
        product_name = soup.find(class_='main-title testlab-caption-products util-inline-block').text
        product_names.append(product_name)
        # Получаем название категорий и рейтинги
        categories = [i.text for i in soup.select('.breadcrumb > ol > li > a span')]
        category_names.append(categories[1])
        subcategory_names.append(categories[2])
        ratings = [i.text for i in soup.select('div.rate-item div span')]
        total_rating = [i.text for i in soup.select('#product__single-rev-total > div:nth-child(1)')]

        # Преобразовываем диапазон от 0 до 100 в диапазон от 0 до 5
        if not change_range:
            safety_ratings.append(ratings[0])
            quality_ratings.append(ratings[-1])
            total_ratings.append(total_rating[0])
        else:
            safety_ratings.append(int(ratings[0]) * 0.05)
            quality_ratings.append(int(ratings[-1]) * 0.05)
            total_ratings.append(int(total_rating[0]) * 0.05)

        # Добавляем сайт, откуда получена информация
        site_names.append(site_name)

    product_detail = {
        'product_name': product_names,
        'category_name': category_names,
        'subcategory_name': subcategory_names,
        'safety_rating': safety_ratings,
        'quality_rating': quality_ratings,
        'total_rating': total_ratings,
        'product_link': product_urls,
        'site_name': site_names
    }

    df = pd.DataFrame(product_detail)
    return df


df1 = get_products_rskrf(URL_rskrf)
df2 = get_urls(URL_roscontrol)
# Без преобразования рейтинга
# df2 = get_urls(URL_roscontrol, change_range=False)

result_df = pd.concat([df1, df2], ignore_index=True)
print(result_df.to_markdown())
# Сохраняем результат в txt файл
result_df.to_markdown('task_1.txt')
