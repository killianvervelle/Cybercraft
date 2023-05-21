import os
import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

options = webdriver.ChromeOptions()
options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.get('https://www.ldlc.com/fr-ch/configurateur-pc/')
a = ActionChains(driver)

# wait for the page to load 
time.sleep(2)
# WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "button outline picto noMarge config-login")))

def get_elements_properties():
    elem_list = []
    # Mouse over the elements
    tbody = driver.find_element(By.CLASS_NAME, "item-table-body")
    for row in tbody.find_elements(By.XPATH, './tr'):
        a.move_to_element(row).perform()
        # Get the informations
        designation = row.find_element(By.CLASS_NAME, 'item-designation').text
        price = row.find_element(By.CLASS_NAME, 'item-prix').text
        description = driver.find_element(By.CLASS_NAME, "description").text
        
        # Extract the number from the price
        price = re.findall("\d+\.\d+", price)[0]
        
        # Remove the designation from the description
        description = description.replace(f'{designation} - ','')
        
        # Register the elements in a dictionnary
        elem_list.append({'designation' : designation, 'price' : price, 'description' : description})
        
        print(designation)
    
    # Close the pop-up
    driver.find_element(By.CLASS_NAME, "close").click()
    
    return elem_list

def write_csv(path, name, elem_list):
    # Export the list to a CSV file
    keys = elem_list[0].keys()
    save_dir = os.path.join(path, name + '.' + 'csv')

    with open(save_dir, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(elem_list)

def scrap_data(categories):
    for key, value in categories.items():
        # Click on the first link (Processeur)
        driver.find_element(By.ID, f"component_{value}").click()
        time.sleep(2)

        # Register the elements of the page
        elem_list = get_elements_properties()

        # Export the data to a csv file
        PATH = 'data/raw/LDLC/'
        write_csv(PATH, key, elem_list)
        
        print(f'Scraping for {key} done')

# Categories with the number of apparition in the website
categories = {'CPU'         :1,
              'ventirad'    :2,
              'motherboard' :3,
              'RAM'         :4,
              'GPU'         :5,
              'SSD'         :6,
              'HDD'         :7,
              'case'        :8,
              'PSU'         :9}

print('Scraping starting...')

scrap_data(categories)

print('Scraping done!')

driver.quit()
