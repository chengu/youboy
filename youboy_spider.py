#-*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Spider, Request
from stack.items import YouBoyItem
import re, sys, urlparse
import codecs, csv

reload(sys)
sys.setdefaultencoding('utf-8')

class YouBoySpider(Spider):
    csvFile = open("/Users/rottens/Desktop/scrapy/youboy.csv", 'w+')
    csvFile.write(codecs.BOM_UTF8)
    writer = csv.writer(csvFile)

    name = 'test'
    allowed_domains = ["book.youboy.com"]
    start_urls = [
        "http://book.youboy.com/bj/9061/",
    ]
    def parse(self, response):
        links = Selector(response).xpath('//div[@class="shengfenlb_txl_con"]//a/@href').extract()
        for link in links:
            areaurl = urlparse.urljoin(response.url, link)
            yield Request(areaurl, callback=self.parsearea)

    def parse_detail(self, response):
        uls = response.xpath('//ul[@class="sheng_weizhi_lb"]')

        for ul in uls:
            item = YouBoyItem()
            item['title'] = str(ul.xpath('.//a/text()').extract_first())
            for li in ul.xpath('.//li/text()').extract():
                arr = li.strip().replace('\t', "").replace('\n', "").replace('\r', "").split('：')
                if len(arr) == 2:
                    item['address'] = str(arr[1])
                elif len(arr) == 3:
                    item['tel'] = str(arr[2])
                    item['user'] = str(arr[1].replace(u'电话',""))

            self.writer.writerow((item.get('title', ''), item.get('user', ''), item.get('tel', ''), item.get('address', '')))
            #yield item

        urls = response.xpath('//dl[@id="digg"]/a')
        for nexturl in urls:
            if nexturl.xpath('text()').extract_first() == u'下一页':
                nextpage = urlparse.urljoin(response.url, nexturl.xpath('./@href').extract_first().replace(u"#page=", ''))
                yield Request(url=nextpage, callback=self.parse_detail)

