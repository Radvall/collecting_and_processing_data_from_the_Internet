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
import pprint
import json
import lxml
import tabulate

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
}


def get_products_url(search_word: str, page_count: int = 1) -> list:
    """Сбор URL продуктов питания с сайта roscontrol.com с поиском по определенному продукту
    на заданном количестве страниц"""

    product_urls = []
    for el in range(page_count):
        url = f'https://roscontrol.com/testlab/search?keyword={search_word}&page={el + 1}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        # Получаем URL продуктов со страниц page_count
        product_on_page = ['https://roscontrol.com' + i['href'] for i in
                           soup.find_all(class_='block-product-catalog__item js-activate-rate '
                                                'util-hover-shadow clear')]
        # Выполняем проверку присутствует ли URL в списке product_urls, чтобы избежать повторов
        if product_on_page[0] in product_urls:
            print(f'На странице {el + 1} обнаружены повторы URL.')
            return product_urls
        else:
            product_urls += product_on_page
    return product_urls


def get_products_roscontrol(product_url: str) -> 'df':
    """Сбор информации по продуктам питания с сайта roscontrol.com"""

    # Получаем подробную информацию о продукте
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # Получаем название продукта
    product_name = soup.find(class_='main-title testlab-caption-products util-inline-block').text

    # Получаем название категории и подкатегории
    categories = [i.text for i in soup.select('.breadcrumb > ol > li > a span')]
    category_name = categories[1]
    subcategory_name = categories[2]

    # Получаем рейтинги
    # Для всех продуктов одинаковые параметры: "Общая оценка", "Безопасность".
    # Их и имеет смысл вносить в DataFrame. Остальные параметры добавлены в "Остальные параметры".
    ratings = [i.text for i in soup.select('div.rate-item div span')]
    ratings_name = [i.text.strip() for i in soup.select('div.rate-item div div ') if len(i.text.strip()) > 0]
    total_rating = [i.text for i in soup.select('#product__single-rev-total > div:nth-child(1)')]
    # Если у продукта отсутствует параметр Безопасность, то продукт находится в чёрном списке либо нет отзывов.

    black_list = soup.select('div.blacklist__item-danger:nth-child(1)')
    if 'Безопасность' in ratings_name:
        safety_rating = int(ratings[ratings_name.index('Безопасность')])
        total_rating = int(total_rating[0])

        # Получаем others_ratings
        others_name = ratings_name.copy()
        others_name.remove('Безопасность')
        others_rating = ratings.copy()
        others_rating.pop(ratings_name.index('Безопасность'))

        # Собираем словарь dic_others_rating
        dic_others_rating = {}
        for index, name in enumerate(others_name):
            dic_others_rating[name] = int(others_rating[index])
    elif black_list:
        total_rating = 0
        safety_rating = 0
        dic_others_rating = {'В чёрном списке': 'Да'}
    else:
        total_rating = None
        safety_rating = None
        dic_others_rating = {'В чёрном списке': 'Нет'}

    # Добавляем сайт, откуда получена информация
    site_name = ['https://roscontrol.com']

    # Итоговый словарь
    product_detail = {
        'Наименование продукта': product_name,
        'Название категории': category_name,
        'Название подкатегории': subcategory_name,
        'Безопасность': safety_rating,
        'Остальные параметры': dic_others_rating,
        'Общая оценка': total_rating,
        'Ссылка на продукт': product_url,
        'Сайт': site_name
    }

    return product_detail


urls = get_products_url('Сыр плавленый', 6)
for url in urls:
    result_dic = get_products_roscontrol(url)
    pprint.pprint(result_dic)
    # Сохраняем результат в json файл
    with open('task_1.json', 'a', encoding='UTF-8') as f:
        product = json.dumps(result_dic, ensure_ascii=False)
        f.write(product)
