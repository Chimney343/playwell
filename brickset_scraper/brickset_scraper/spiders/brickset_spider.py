import scrapy
import re
import math
from urllib.parse import urljoin
import scrapy
import csv
import scrapy
import csv
from scrapy import signals
from pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess


class BricksetSpider(scrapy.Spider):
    name = 'brickset'
    start_urls = ['https://brickset.com/browse/sets']
#
    def parse(self, response):
        subpages = response.css('a::attr(href)').getall()
        for subpage in subpages:
            if 'theme' in subpage:
                yield response.follow(subpage, self.parse_subpage)

    def parse_name(self, response, article):
        xpath = f'/html/body/div[1]/div/div/section/article[{article}]/div[2]/h1/a/text()'
        val = response.xpath(xpath).get()
        if val:
            return val.strip()

    def parse_number(self, response, article):
        xpath = f'/html/body/div[1]/div/div/section/article[{article}]/div[2]/div[1]/a[1]/text()'
        val = response.xpath(xpath).get()
        if val:
            return val.strip()

    def parse_theme(self, response, article):
        xpath = f"/html/body/div[1]/div/div/section/article[{article}]/div[2]/div[1]/a[2]/text()"
        val = response.xpath(xpath).get()
        if val:
            return val.strip()

    def parse_subtheme(self, response, article):
        xpath = f"/html/body/div[1]/div/div/section/article[{article}]/div[2]/div[1]/a[3]/text()"
        val = response.xpath(xpath).get()
        if val:
            return val.strip()

    def parse_year(self, response, article):
        xpath =f"/html/body/div[1]/div/div/section/article[{article}]/div[2]/div[1]/a[4]/text()"
        val = response.xpath(xpath).get()
        if val:
            return val.strip()


    def parse_tags(self, response, article=1):
        selector = f'article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(3)'
        tags = response.css(selector).xpath('string()').getall()[0]
        tags = tags.split("»")[1].split(' ')
        tags = [tag for tag in tags if tag]
        return tags

    def parse_metadata(self, response, article=1):
        metadata = {}
        first_col_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5)"
        second_col_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(6)"
        first_col_n_rows = len(response.css(first_col_selector + ' dt'))
        second_col_n_rows = len(response.css(second_col_selector + ' dt'))

        for i in range(1, first_col_n_rows*2, 2 ):
            row_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5) > dl:nth-child(1) > dt:nth-child({i})"
            value_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5) > dl:nth-child(1) > dd:nth-child({i+1})"
            row = response.css(row_selector).xpath('string()').get()
            value = response.css(value_selector).xpath('string()').get()
            metadata[row] = value

        for i in range(1, second_col_n_rows*2, 2 ):
            row_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(6) > dl:nth-child(1) > dt:nth-child({i})"
            value_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(6) > dl:nth-child(1) > dd:nth-child({i+1})"
            row = response.css(row_selector).xpath('string()').get()
            value = response.css(value_selector).xpath('string()').get()
            metadata[row] = value

        return metadata

    def parse_subpage(self, response):
        for i in range(1, 26):  # Adjust the range accordingly if necessary
            name = self.parse_name(response, article=i)
            if not name:
                continue

            data =  {
                'name': name,
                'number': self.parse_number(response, i),
                'theme': self.parse_theme(response, i),
                'subtheme': self.parse_subtheme(response, i),
                'year': self.parse_year(response, i),
                'tags': self.parse_tags(response, i),
                'inventory_link': (urljoin('https://brickset.com/inventories/', self.parse_number(response, i)))
            }
            metadata =  self.parse_metadata(response, i)
            for k, v in metadata.items():
                data[k] = v

            with open("sets.csv", 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
            yield data



        next_page_url = response.css('li.next > a::attr(href)').get()
        if next_page_url:
            yield response.follow(next_page_url, self.parse_subpage)


# class InventorySpider(scrapy.Spider):
#     name = "inventory"
#     start_urls = None
#
#     def __init__(self, set_number):
#         self.table_loaded = False
#         dispatcher.connect(self.spider_idle, signals.spider_idle)
#
#     def parse(self, response):
#         # Waiting until the table is loaded
#         table = response.css('table.neattable:nth-child(5) > tbody:nth-child(2)')
#         if table:
#             self.extract_table_data(table)
#             self.table_loaded = True
#
#     def spider_idle(self):
#         if not self.table_loaded:
#             pass
#
#     def extract_table_data(self, table):
#         # Extracting table data
#         rows = table.css('tr')
#
#         # Creating a CSV file and writing the data
#         with open(f'{set_number}_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
#             writer = csv.writer(csvfile)
#             for row in rows:
#                 columns = row.css('td')
#                 row_data = [column.css('::text').get().strip() for column in columns]
#                 writer.writerow(row_data)
