from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    # process.crawl(HhruSpider)
    process.crawl(SjruSpider)

    process.start()
