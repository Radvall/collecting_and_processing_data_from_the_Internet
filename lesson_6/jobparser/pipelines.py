# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_hhru_salary(item['salary'])
        elif spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['salary_cur'] = self.process_superjob_salary(item['salary'])

        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_hhru_salary(self, salary):
        salary = salary.replace('\xa0', '').split()
        salary_cur = salary[-1]
        if salary[0] == 'от' and salary[2] == 'до':
            salary_min = int(salary[1])
            salary_max = int(salary[3])
        elif len(salary) < 4 and salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
        elif salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
        else:
            salary_min = None
            salary_max = None
            salary_cur = None
        return salary_min, salary_max, salary_cur

    def process_superjob_salary(self, salary):
        salary = [_.replace('\xa0', '') for _ in salary]
        if salary:
            if salary[0] == 'от':
                salary_und = re.split(r'(\d+)', salary[2])
                salary_min = int(salary_und[1])
                salary_cur = salary_und[-1]
                salary_max = None
            elif salary[0] == 'до':
                salary_height = re.split(r'(\d+)', salary[2])
                salary_cur = salary_height[-1]
                salary_max = int(salary_height[1])
                salary_min = None
            elif salary[0] == 'По договорённости':
                salary_min = None
                salary_max = None
                salary_cur = None
            elif len(salary) > 4:
                salary_min = int(salary[0])
                salary_max = int(salary[1])
                salary_cur = salary[-2]
        else:
            salary_min = None
            salary_max = None
            salary_cur = None

        return salary_min, salary_max, salary_cur
