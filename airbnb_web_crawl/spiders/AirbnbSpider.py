import scrapy
import json
import time
from selenium import webdriver
from airbnb_web_crawl.items import AirbnbWebCrawlItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class AirbnbSpider(scrapy.Spider):

    #Query = "allston/homes?adults=1&checkin=2017-05-17&checkout=2017-05-18&ne_lat=42.36447710622584&ne_lng=-71.1279552729207&search_by_map=true&sw_lat=42.35651342299473&sw_lng=-71.13625939203081&zoom=16&s_tag=Xzaipvc6"

    neighborhood = "allston/homes?"
    checkin = "&checkin=2017-05-17"
    checkout = "&checkout=2017-05-18"
    location_on_map = "&ne_lat=42.36447710622584&ne_lng=-71.1279552729207&search_by_map=true&sw_lat=42.35651342299473&sw_lng=-71.13625939203081&zoom=16&s_tag=Xzaipvc6"

    name = "airbnb_spider"

    start_urls = ['http://www.airbnb.com/s/' + neighborhood + checkin + checkout + location_on_map]


    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        last_page_number = 4
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

        try:
            price = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="summary"]/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/form/div/div/div[2]/div/table/tbody/tr[last()]/td/span/span'))
            )
        finally:
            print("no no no")
            # self.driver.quit()
        #
        #price = self.driver.find_element_by_xpath(
        #        '//*[@id="summary"]/div/div/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/form/div/div/div[2]/div/table/tbody/tr[last()]/td/span/span')
        if price:
            item['price'] = price.text


        # get description data
        desc = response.xpath('//meta[@property="og:title"]/@content').extract()[0].split('-')[0]
        if desc:
            item['description'] = desc

        yield item