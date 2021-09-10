import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem
import configparser

class InstagramSpider(scrapy.Spider):
    config = configparser.ConfigParser()
    config.read('config.ini')
    LOGIN = config['instaparser']['LOGIN']
    PASS = config['instaparser']['PASS']

    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com']
    insta_login = LOGIN
    insta_pass = PASS
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    user_parse_list = ['ai_machine_learning', 'machine_learning_with_python']
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://i.instagram.com/api/v1/'


    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.insta_login_link,
                                 method='POST',
                                 callback=self.user_login,
                                 formdata={'username': self.insta_login,
                                           'enc_password': self.insta_pass},
                                 headers={'X-CSRFToken': csrf})

    def user_login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            for user_parse in self.user_parse_list:
                yield response.follow(f'/{user_parse}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user_parse})


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"count": 12}
        statuses = ['following', 'followers']

        for user_status in statuses:
            users_url = f'{self.graphql_url}friendships/{user_id}/{user_status}/?{urlencode(variables)}'
            yield response.follow(users_url,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables),
                                             'user_status': user_status},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})


    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables, user_status):
        if response.status == 200:
            j_data = response.json()
            if j_data.get('next_max_id'):
                variables['after'] = j_data.get('next_max_id')
                url_follower = f'{self.graphql_url}friendships/{user_id}/{user_status}/?{urlencode(variables)}'
                yield response.follow(url_follower,
                                      callback=self.user_followers_parse,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'variables': deepcopy(variables),
                                                 'user_status': user_status},
                                      headers={'User-Agent': 'Instagram 155.0.0.37.107'})
            for user in j_data.get('users'):
                item = InstaparserItem(user_id=user.get('pk'),
                                       username=user.get('username'),
                                       photo=user.get('profile_pic_url'),
                                       user_status=user_status
                                       )
                yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
