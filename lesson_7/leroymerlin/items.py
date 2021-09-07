# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def convert_str_to_float(value):
    try:
        value = float(value.replace(' ', ''))
    except ValueError:
        pass
    return value


def remove_spaces(value):
    if type(value) == dict:
        for k, v in value.items():
            v = v.lstrip()
            v = v.rstrip()
            value[k] = convert_str_to_float(v)

    return value


class LeroymerlinItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    description = scrapy.Field()
    options = scrapy.Field(input_processor=MapCompose(remove_spaces), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_str_to_float), output_processor=TakeFirst())
    _id = scrapy.Field()
