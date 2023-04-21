import requests
import pandas as pd
import numpy as np
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin
import scrapy.dupefilters
import pandas as pd
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






def proxy(proxy):
        try:
            r = requests.get('https://www.techpowerup.com/cpu-specs/', proxies = {'http':proxy, 'https':proxy}, timeout=3)
            print(r.json(), 'working')
        except:
            print('doesnt work')
            pass
        return proxy


data = ['\r\n                            ', '\r\n                            2,000 Watt\r\n                        ']
# Extract the text and remove unwanted characters
text = data[1].strip().split()[0].replace(",", "")



import pandas as pd
from selenium import webdriver
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
"""service = Service("/home/ubuntu/selenium_drivers/chromedriver")
service2 = Service("/home/ubuntu/selenium_drivers/chromedriver")
base_url = 'https://www.crave.ca/en/tv-shows/16-and-pregnant'
base_url2 = 'https://www.ldlc.com/fr-ch/fiche/PB00345957.html'
page_one = True
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
driver2 = webdriver.Chrome(service=service2, options=options)
driver.get(base_url)
driver2.get(base_url2)
driver.find_element(By.XPATH,'//*[@id="dropdown-basic"]').click()
driver2.find_element(By.XPATH,'//*[@id="dropdown-basic"]').click()
time.sleep(1)
total_seasons = driver.find_elements(By.CSS_SELECTOR,'button.dropdown-item')
total_seasons = driver2.find_elements(By.CSS_SELECTOR,'button.dropdown-item')
driver.find_element(By.XPATH,'//*[@id="dropdown-basic"]').click()
driver2.find_element(By.XPATH,'//*[@id="dropdown-basic"]').click()
print(len(total_seasons))"""
"""d=[]
for i in range(len(total_seasons)):
    alleps = driver.find_elements(By.XPATH,'//*[@id="episodes"]/div/ul/li')
    for j in range(1,len(alleps)+1):

        d.append({
            
            'Duration ': driver.find_element(By.XPATH,f'//*[@id="episodes"]/div/ul/li[{j}]/div[1]/div[2]/span/span[1]').text,
            'Episode_Number ': j,
            'Episode_Synopsis ': driver.find_element(By.XPATH,f'//*[@id="episodes"]/div/ul/li[{j}]/div[1]/div[2]/p').text,
            'Episode_Title ': re.sub(r'[^a-zA-Z ]+','',driver.find_element(By.XPATH,f'//*[@id="episodes"]/div/ul/li[{j}]/div[1]/div[2]/h3').text).strip(),
            
        })
    driver.find_element(By.XPATH,'//*[@id="dropdown-basic"]').click()
    seasons = driver.find_elements(By.CSS_SELECTOR,'button.dropdown-item')
    seasons[i].click()
    time.sleep(1)

data = pd.DataFrame.from_dict(d)"""

"""from bs4 import BeautifulSoup
import requests
rw = []
r = requests.get("https://www.ldlc.com/fr-ch/fiche/PB00345957.html", headers={'user-agent': 'Chrome'}) 
soup = BeautifulSoup(r.content, 'html.parser')
for div_tag in soup.find_all('td', {"class" : "checkbox"}):
    div_tag2 = div_tag.text.strip().split()[0].replace("", "")
    rw.append(div_tag2)



html_content = requests.get("https://www.ldlc.com/fr-ch/fiche/PB00345957.html", headers={'user-agent': 'Chrome'}) 
# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(html_content.body, 'html.parser')

# Find the brand name
brand = soup.find('td', text='Marque').find_next_sibling('td').text.strip().split()[0].replace("", "")

# Find the model name
model = soup.find('td', text='Modèle').find_next_sibling('td').text.strip()

# Find the processor support information
processor_support = soup.find('td', text='Support du processeur').find_next_sibling('td').text.strip()

# Find the number of supported CPUs
num_cpus = soup.find('td', text='Nombre de CPU supportés').find_next_sibling('td').text.strip()

# Find the chipset information
chipset = soup.find('td', class_='label', text='Chipset').find_next_sibling('td').text.strip()


# Find the memory frequencies
#memory_frequencies = [freq.text.strip() for freq in soup.find('th', text='Fréquence(s) Mémoire').find_next_sibling('td').find_all('li')]

# Create a dictionary to store the formatted data
formatted_data = {
    'brand': brand,
    'model': model,
    'processor_support': processor_support,
    'num_cpus': num_cpus,
    'chipset': chipset,
    #'memory_frequencies': memory_frequencies
}

print(formatted_data)"""


import scrapy
from urllib.parse import urlencode

API_KEY = "3cff6e3f-01a0-4e1f-ac05-f65088e823d9"

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'https://www.toppreise.ch/chercher?q=ASUS+ROG-STRIX-1000G+Gold+Aura+Editio&cid='
        ]
        for url in urls:
            yield scrapy.Request(url=get_scrapeops_url(url), callback=self.discover_product_specs)
    
    def discover_product_specs(self, response):
        # Create a BeautifulSoup object to parse the HTML content
        #soup = BeautifulSoup(response.body, 'html.parser')
            yield {
            "name": response.xpath('//*[@id="Plugin_HashedPrice_157019"]/div/text()').get()
            }

# Runs once to retrieve all benchmark
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
process.start()