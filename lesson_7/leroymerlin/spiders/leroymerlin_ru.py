import scrapy
import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroymerlinRuSpider(scrapy.Spider):
    name = 'leroymerlin_ru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response):
        url = response.xpath("//a[@data-qa='product-name']")
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in url:
            yield response.follow(link, callback=self.parse_products)

    def parse_products(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath("name", "//h1/text()")
        loader.add_xpath("photos", "//img[@slot='thumbs']/@src")
        loader.add_xpath("description", "//section[@id='nav-description']//p/parent::div")
        options = {}
        for option in response.xpath("//div[@class='def-list__group']"):
            options[option.xpath("./dt/text()").get()] = option.xpath("./dd/text()").get()
        loader.add_value("options", options)
        loader.add_value("link", response.url)
        loader.add_xpath("price", "//span[@slot='price']/text()")

        yield loader.load_item()


