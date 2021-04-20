import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IinterbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'


class PressreleaseSpider(scrapy.Spider):
    name = 'pressrelease'
    start_urls = ['https://interbank.pe/blog/sala-de-prensa']
    ITEM_PIPELINES = {
        'pressrelease.pipelines.IinterbankPipeline': 300,

    }
    def parse(self, response):
        post_links = response.xpath('//a[@class="post-title"]/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

    def parse_post(self, response):
        date = response.xpath('//div[@class="post__icon-date"]/span/text()').get()
        if date:
            date = date.strip()
        title = response.xpath(
            '//ol[@class="lq-breadcrumb__nav"]/li[last()]/text() | //h2[@class="lq-pd__title"]/text()').get()
        content = response.xpath(
            '(//div[@class="lq-row"])[last()]//text() | //div[@class="lq-col-sm-13 lq-col-sm-off-1 lq-col-md-16 lq-col-md-off-1 lq-pd__content-col"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=IinterbankItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

