import scrapy


class Message(scrapy.Item):
    path = scrapy.Field()
    email = scrapy.Field()
    group = scrapy.Field()