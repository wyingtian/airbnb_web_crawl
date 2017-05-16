import scrapy
import json
import time
from selenium import webdriver
from airbnb_web_crawl.items import AirbnbWebCrawlItem
class AirbnbSpider(scrapy.Spider):

    Query = "allston/homes?checkin=2017-05-18&checkout=2017-05-20"
    name = "airbnb_spider"

    start_urls = ['http://www.airbnb.com/s/' + Query]


    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        last_page_number = 40
        if last_page_number < 1:
            return
        else:
            page_urls = [response.url + "?section_offset=" + str(pageNumber) for pageNumber in range(last_page_number)]
        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=self.parse_listing_results_page)


    def parse_listing_results_page(self, response):
        room_url_parts = set(response.xpath('//div/a[contains(@href,"rooms")]/@href').extract())
        for href in list(room_url_parts):
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_listing_contents)

    def parse_listing_contents(self, response):
        item = AirbnbWebCrawlItem()

        # get total price, including cleaning fee and service fee
        # use tr[last() in xpath to get total data
        self.driver.get(response.url)
        time.sleep(3)
        price = self.driver.find_element_by_xpath(
               '//*[@id="summary"]/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/form/div/div/div[2]/div/table/tbody/tr[last()]/td/span/span')
        if price:
            item['price'] = price.text


        # get description data
        desc = response.xpath('//meta[@property="og:title"]/@content').extract()[0].split('-')[0]
        if desc:
            item['description'] = desc


        yield item