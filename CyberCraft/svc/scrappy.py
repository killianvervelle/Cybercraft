from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
import scrapy.dupefilters
from scrapy_splash import SplashRequest
import scrapy
import random
import logging
from bs4 import BeautifulSoup
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
import pandas as pd
from selenium import webdriver
from urllib.parse import urlencode
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
logger = logging.getLogger("uvicorn.error")


# Crawler Scrapy
class QuotesSpider(scrapy.Spider):
    name = "spider"
    API_KEY = "4f4f5166-b931-4ffd-bb24-4bdf93ced0a5"
    SCRAPEOPS_PROXY_ENABLED = True
    download_delay = random.randint(1, 3)
    LOG_LEVEL='DEBUG'
    
    def get_scrapeops_url(self, url):
        payload = {'api_key': self.API_KEY, 'url': url}
        proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
        return proxy_url

    def start_requests(self):
        config = self.settings.get('arg')
        urls = ["https://www.toppreise.ch/chercher?q=" + component for component in config]
        print(urls)
        for url in urls:
            print("URL", url)
            yield scrapy.Request(url=url, callback=self.discover_urlset_specs)

    """def start_requests(self):
        config = self.settings.get('arg')
        urls = ["https://www.toppreise.ch/chercher?q=" + component for component in config]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.discover_urlset_specs)
        #yield scrapy.Request(url=url, callback=self.parse)"""
    
    def parse(self, response):
        pagination_links = response.xpath('//ul[@class="pagination"]/li[not(@class="next")]/a/@href').getall()
        for link in pagination_links:
            link = urljoin('https://www.ldlc.com', link)
            yield scrapy.Request(url=link, callback=self.discover_product_urls)
            
    def discover_product_urls(self, response):
        # Get product URLs for a given page
        search_products = response.xpath('//li[contains(@id, "pdt-")]')
        for product in search_products:
            relative_url = product.css('a::attr(href)').get()
            product_url = urljoin('https://www.ldlc.com', relative_url)   
            yield scrapy.Request(url=product_url, callback=self.discover_product_specs)
    
    def discover_urlset_specs(self,response): 
        low_sup = response.xpath('//a[contains(@href, "/comparison-prix")][1]/@href').get()
        if low_sup != None:
            yield scrapy.Request(url=urljoin("https://www.toppreise.ch",low_sup), callback=self.browser_scrapping) 
        else:
            low_sup = response.xpath('//a[contains(@href, "/ext_fr")][1]/@href').get()
            name = response.xpath('//a[contains(@href, "/ext_fr")][1]/text()').get()
            type = response.xpath('//div[contains(@id, "Plugin_Breadcrumbs")]/div/div/div[4]/span/text()').get()
            if low_sup != None:
                yield {
                "url": response.request.url,
                "lowest_supplier_url": "https://www.toppreise.ch"+low_sup,
                "name": name,
                "type": type
                }
            else:
                logger.info('Product not found.')
                yield {
                "url": response.request.url,
                "lowest_supplier_url": "Not found",
                "name": "Not found",
                "type": "Not found"
                }
                
    def browser_scrapping(self,response):
        low_sup = response.xpath('//a[contains(@href, "/ext_fr")][1]/@href').get()
        name = response.xpath('//a[contains(@href, "/ext_fr")][1]/text()').get()
        type = response.xpath('//div[contains(@id, "Plugin_Breadcrumbs")]/div[1]/div/div[4]/div/a/span/text()').get()
        if low_sup != None:
            yield {
                "url": response.request.url,
                "lowest_supplier_url": "https://www.toppreise.ch"+low_sup,
                "name": name,
                "type": type,
                "type": type
                }
        else:
            logger.info('Product not found.')
            yield {
                "url": response.request.url,
                "lowest_supplier_url": "Not found",
                "name": "Not found",
                "type": "Not found"
                }

    def discover_product_specs(self, response):
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.body, 'html.parser')
        if response.xpath('//div[@id="activeOffer"]/div[1]/h2[contains(text(), "Carte mère")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(),
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "format": soup.find('td', text='Format de carte mère').find_next_sibling('td').text.strip(),
            "memory_type": soup.find('td', text='Type de mémoire').find_next_sibling('td').text.strip(),                  
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//*[@id="activeOffer"]/div[1]/h2[contains(text(), "Alimentation")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(),
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "power": soup.find('td', text='Puissance').find_next_sibling('td').text.strip().replace(' ', ''),
            "power_type": soup.find('td', text='Format Alimentation').find_next_sibling('td').text.strip(),                   
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//li[@class="alone"]/a[contains(text(), "Ventilateur")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(), 
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "type": soup.find('td', text='Type de refroidissement').find_next_sibling('td').text.strip(),
            "largeur": soup.find('td', text='Largeur (ventilateur inclus)').find_next_sibling('td').text.strip().replace(' ', ''),              
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//*[@id="activeOffer"]/div[1]/h2[contains(text(), "Boîtier")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(),
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "type_mb1": soup.find('td', text='Format de carte mère').find_next_sibling('td').text.strip(),
            "type_mb2": soup.find('td', text='Format de carte mère').find_next('tr').text.strip(),
            "len_gpu_max": soup.find('td', text='Longueur max. carte graphique').find_next_sibling('td').text.strip().replace(' ', ''),
            "watercooling_compat": soup.find('td', text='Compatible Watercooling').find_next_sibling('td').text.strip(),
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//*[@id="activeOffer"]/div[1]/h2[contains(text(), "RAM")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(), 
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "type": soup.find('td', text='Type de mémoire').find_next_sibling('td').text.strip(),  
            "capacity": soup.find('td', text='Capacité').find_next_sibling('td').text.strip().replace(' ', ''),
            "frequency": soup.find('td', text='Fréquence(s) Mémoire').find_next_sibling('td').text.strip(),            
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
            
        elif response.xpath('//li[@class="alone"]/a[contains(text(), "SSD")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(), 
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "capacity": soup.find('td', text='Capacité').find_next_sibling('td').text.strip().replace(' ', ''),            
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//li[@class="alone"]/a[contains(text(), "Carte graphique")]/text()').get() is not None:
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(), 
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "4k_ready": soup.find('td', text='Résolution(s) 4K UHD').find_next_sibling('td').text.strip(),  
            "power_usage": soup.find('td', text='Consommation').find_next_sibling('td').text.strip().replace(' ', ''),
            "length": soup.find('td', text='Longueur').find_next_sibling('td').text.strip().replace(' ', ''),            
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        elif response.xpath('//li[@class="alone"]/a[contains(text(), "Processeur")]/text()').get() is not None:
            compatibility_table = soup.find('td', {'class': 'label'}, text='Compatibilité chipset carte mère').find_parent('table')
            compatibility_chipset = []
            keywords=["B550", "X570", "A520", "B350", "B450", "X370", "A320", "A300", "X470", "X670E", \
                "X670", "B650E", "B650", "H110", "H310", "B150", "B250", "B360", "H170", "H270", "H370", \
                    "Z170", "Z270", "Z390", "Z370", "H770", "B760", "Z790", "B660", "H610", "H670", "Z690"]
            for a_tag in compatibility_table.find_all('a'):
                a_tag = a_tag.text.strip().replace(' ', '')
                for keyword in keywords:
                    if keyword in a_tag:
                        compatibility_chipset.append(keyword)
            yield {
            "name": soup.find('td', text='Désignation').find_next_sibling('td').text.strip(), 
            "model": soup.find('td', text='Modèle').find_next_sibling('td').text.strip(),
            "compatiblity_list": compatibility_chipset,              
            "price": response.xpath('//*[@id="activeOffer"]/div[2]/div[3]/aside/div[1]/div/text()').get().strip()
            }
        
        else: print('Error : product unavailable')
        
        
"""# Runs once to retrieve all benchmark
process = CrawlerProcess(settings={
        "FEEDS": {
            #"mb.csv": {"format": "csv"},
            #"rad.csv": {"format": "csv"},
            #"power.csv": {"format": "csv"},
            #"case.csv": {"format": "csv"},
            #"gpu2.csv": {"format": "csv"},
            #"cpu2.csv": {"format": "csv"},
            "ram2.csv": {"format": "csv"},
            #"ssd2.csv": {"format": "csv"}
        },
        "DOWNLOAD_DELAY" : 4,
        "LOG_LEVEL" : 'DEBUG'
    })  
process.crawl(QuotesSpider)
process.start()"""