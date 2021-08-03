import requests
import pandas as pd
import json

# Задание 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
# для конкретного пользователя, сохранить JSON-вывод в файле *.json.

USER = 'Radvall'
URL = 'https://api.github.com'


def get_data(url: str, owner: str) -> dict:
    try:
        response = requests.get(f'{url}/users/{owner}/repos').json()
        print('OK')
        return response
    except requests.exceptions.RequestException as e:
        print(f'Something went wrong with {URL}')
        raise SystemExit(e)


repo = []
for el in get_data(URL, USER):
    repo.append(el['name'])
pd.DataFrame(repo).to_json('task_1.json')

# Задание 2:  Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл

"""
Использовал ABBYY Lingvo API: https://www.programmableweb.com/api/abbyy-lingvo 
https://developers.lingvolive.com/ru-ru/Help
Для авторизации необходимо отправить POST запрос.

При успешной аутентификации получаем Bearer-токен, который нужно прикладывать к последующим запросам 
в заголовке Authorization. Иначе - сообщение о том, что аутентификация не удалась с кодом 401. 
Срок действия токена - сутки.
"""

API_KEY = 'OTczMjlhMjYtYmMzOC00ZTgzLTg5OWEtZmVhMzViN2E1NWY3OjE1YTM0YTgzZmMxZTQ3MWVhNWE3NjY0MmVlZGZhMzMy'
URL_auth = 'https://developers.lingvolive.com/api/v1.1/authenticate'

headers_auth = {'Authorization': f'Basic {API_KEY}'}
res = requests.post(URL_auth, headers=headers_auth)

print(f'Ответ ABBYY Lingvo: {res}')
bearer_token = res.text

# Сохраним ответ сервера в json.
text = 'raccoon'
srcLang = 1033
dstLang = 1049
URL = f'https://developers.lingvolive.com/api/v1/Minicard?text={text}&srcLang={srcLang}&dstLang={dstLang}'
headers = {'Authorization': f'Bearer {bearer_token}'}
req = requests.get(URL, headers=headers)

with open('task_2.json', 'w') as f:
    json.dump(req.json(), f)
