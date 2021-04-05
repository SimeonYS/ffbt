import scrapy
import re
from scrapy.loader import ItemLoader
from ..items import FffbtItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class BlogSpider(scrapy.Spider):
    name = 'blog'
    start_urls = ['https://www.ffbt.com/online-resources/blog/1']
    ITEM_PIPELINES = {
        'blog.pipelines.FffbtPipeline': 300,

    }

    def parse(self, response):
        post_links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

        next_page = response.xpath('//ul[@class="pagination"]/li/a/@href').getall()
        if next_page:
            yield from response.follow_all(next_page, self.parse)

    def parse_post(self, response):
        date = response.xpath('//div[@class="sfpostAuthorAndDate blog-meta"]/text()').get().split(' | ')[0]
        title = response.xpath('//h2[@class="sfpostTitle sftitle blog-title"]/span/text()').get()
        content = response.xpath('//div[@class="sfpostContent sfcontent"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=FffbtItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()