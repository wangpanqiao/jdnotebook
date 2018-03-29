# -*- coding: utf-8 -*-
import json

import scrapy


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']

    def start_requests(self):
        for page in range(1, 100):
            # 670,671,672 表示笔记本分类
            url = "http://list.jd.com/list.html?cat=670,671,672&page={}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main".format(page)
            yield scrapy.Request(url)

    def parse(self, response):
        li_list = response.xpath("//div[@id='plist']/ul/li/div/@data-sku").extract()
        for li in li_list:
            # 请求详情页
            url = "https://item.jd.com/{}.html".format(li)
            item = {"shop_id": li}
            yield scrapy.Request(url, callback=self.detail, meta={"item": item})

    def detail(self, response):
        item = response.meta["item"]
        parameter = response.xpath("//ul[@class='parameter2 p-parameter-list']/li/text()").extract()
        f = lambda i: {i.split("：")[0]: i.split("：")[1]}
        for i in map(f, parameter):
            item.update(i)
        url = "http://p.3.cn/prices/get?skuid=J_"+item["shop_id"]
        yield scrapy.Request(url,callback=self.get_price, meta={"item": item})

    def get_price(self, response):
        item = response.meta["item"]
        data = json.loads(response.text)
        item["price"] = data[0]["p"]
        yield item
