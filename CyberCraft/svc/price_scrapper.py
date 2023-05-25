import os
import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
# options.headless = True
options.add_argument('--ignore-certificate-errors')
options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.get('https://www.ldlc.com/fr-ch/configurateur-pc/')
driver.implicitly_wait(5) # seconds
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

def wait_for_element(by_type=By.ID, elem="component_1", from_elem=driver):
    try:
        element = WebDriverWait(from_elem, 5, ignored_exceptions=ignored_exceptions).until(
            EC.visibility_of_element_located((by_type, elem))
        )
    except:
        element = None
        print('element not found')
        
    return element

def get_elements_properties():
    elem_list = []
    tbody = wait_for_element(By.CLASS_NAME, "item-table-body")
    # Mouse over the elements
    # stop=0
    all_elements_founds = False
    saved_index = 0
    while not all_elements_founds:
        rows = tbody.find_elements(By.XPATH, "./tr")
        print(len(rows))
        for index in range(saved_index, len(rows)):
            row = rows[index]
            
            # Wait for the element to load
            try:
                driver.execute_script("arguments[0].scrollIntoView();", row)
                if saved_index == index:
                    # time.sleep(2)
                    ActionChains(driver).move_to_element(row).perform()
                
                # Get the informations
                designation = WebDriverWait(row, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'item-designation'))).text
                price = WebDriverWait(row, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'item-prix'))).text
                description = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'description'))).text
            except:
                print(f'saved index : {saved_index}')
                # time.sleep(2)
                break
            if index > saved_index:
                saved_index = index
            
            # Extract the number from the price
            price = re.findall("\d*'*\d+\.\d+", price)[0]
            price = price.replace('\'', '')
            
            # Remove the designation from the description
            description = description.replace(f'{designation} - ','')
            
            # Register the elements in a dictionnary
            elem_list.append({'designation' : designation, 'price' : price, 'description' : description})
            
            print(designation)
            # Early stopping for testing
            # stop += 1
            # if stop > 10 : break
        if saved_index >= len(rows)-1: all_elements_founds = True
    
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
        # Click on the category button
        wait_for_element(elem=f"component_{value}")
        time.sleep(1)
        driver.find_element(By.ID, f"component_{value}").click()

        # Register the elements of the page
        elem_list = get_elements_properties()
        print(len(elem_list))

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

# Accept cookies
element = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.ID, "cookieConsentAcceptButton"))
)
element.click()

print('Scraping starting...')

# wait for the page to load 
wait_for_element()

scrap_data(categories)

print('Scraping done!')

driver.quit()
