import scrapy
import re
import math
#
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
        selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5)"

        n_rows = len(response.css(selector + ' dt'))

        for i in range(1, n_rows*2, 2 ):
            row_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5) > dl:nth-child(1) > dt:nth-child({i})"
            value_selector = f"article.set:nth-child({article}) > div:nth-child(3) > div:nth-child(5) > dl:nth-child(1) > dd:nth-child({i+1})"
            row = response.css(row_selector).xpath('string()').get()
            value = response.css(value_selector).xpath('string()').get()
            metadata[row] = value

        return metadata

    def parse_subpage(self, response):
        for i in range(1, 26):  # Adjust the range accordingly if necessary
            name = self.parse_name(response, article=i)
            if not name:
                continue

            values =  {
                'name': name,
                'number': self.parse_number(response, i),
                'theme': self.parse_theme(response, i),
                'subtheme': self.parse_subtheme(response, i),
                'year': self.parse_year(response, i),
                'tags': self.parse_tags(response, i),
                'metadata': self.parse_metadata(response, i)

            }
            yield values

        next_page_url = response.css('li.next > a::attr(href)').get()
        print(next_page_url)
        if next_page_url:
            yield response.follow(next_page_url, self.parse_subpage)