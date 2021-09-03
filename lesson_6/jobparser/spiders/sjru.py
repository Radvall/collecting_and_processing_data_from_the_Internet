import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python',
                  'https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//div[contains(@class,'f-test-vacancy-item')]//a[contains(@href, 'vakansii')]/@href").getall()
        next_page_button = response.xpath("//a[contains(@class,'f-test-button-dalshe')]/@href").get()
        if next_page_button:
            yield response.follow(next_page_button, callback=self.parse)
        for url in urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vac_name = response.xpath("//h1/text()").get()
        vac_salary = response.xpath("//h1/following-sibling::span//text()").getall()
        vac_url = response.url
        item = JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)
        yield item
