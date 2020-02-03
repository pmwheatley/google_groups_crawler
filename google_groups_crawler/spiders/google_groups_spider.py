import email
import re

import dateparser
import scrapy

from google_groups_crawler.items import Message


class GoogleGroupsSpider(scrapy.Spider):
    name = 'google-groups'

    topic_regex = re.compile('/d/topic/')
    msg_regex = re.compile('/d/msg/')

    PAGE_BASE = "https://groups.google.com/forum/?_escaped_fragment_=categories/"
    GROUP = None

    def start_requests(self):
        self.GROUP = getattr(self, 'GROUP', self.GROUP)
        if self.GROUP:
            yield scrapy.Request(f"{self.PAGE_BASE}{self.GROUP}[1-100]")

    def parse(self, response):
        for topic_url in response.xpath('//td/a/@href').extract():
            topic_url = self.topic_regex.sub('/forum/?_escaped_fragment_=topic/', topic_url)
            yield scrapy.Request(topic_url, callback=self.parse_topic)
        has_more = response.xpath('//a[text()="More topics »"]')
        if len(has_more):
            yield scrapy.Request(has_more[0].xpath('@href')[0].extract())

    def parse_topic(self, response):
        for msg_url in response.xpath('//td/a/@href').extract():
            msg_url = self.msg_regex.sub('/forum/message/raw?msg=', msg_url)
            yield scrapy.Request(msg_url, callback=self.parse_msg)

    def parse_msg(self, response):
        msg = email.message_from_string(response.text)
        d = dateparser.parse(msg.get('Date'), settings={"RETURN_AS_TIMEZONE_AWARE": True})
        if d:
            msg.replace_header('Date', d.ctime())

        path_parts = response.url.split('msg=')[-1].split('/')
        path = '/'.join([path_parts[0]] + ['.'.join(path_parts[1:]) + '.eml'])
        yield Message(path=path, email=msg, group=self.GROUP)
