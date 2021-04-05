import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FffbtItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'

class FffbtSpider(scrapy.Spider):
	name = 'ffbt'
	start_urls = ['https://investor.ffbt.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&LanguageId=1&bodyType=3&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['GetPressReleaseListResult'])):
			link = data['GetPressReleaseListResult'][index]['LinkToDetailPage']
			date = data['GetPressReleaseListResult'][index]['PressReleaseDate'].split()[0]
			title = data['GetPressReleaseListResult'][index]['Headline']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date,title=title))

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="module_body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FffbtItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
