from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\Brave.exe"
DRIVER_PATH = "C:\\Users\\anton\\Downloads\\chromedriver_win32\\chromedriver.exe"
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

# Open Scrapingbee's website
driver.get("http://www.scrapingbee.com")

# Match all img tags on the page
all_img = driver.find_elements(By.XPATH, "//img")

# Match all a tags that contain the class of btn
all_btn = driver.find_elements(By.XPATH, "//a[contains(@class, 'btn')]")

# Match the first h1 tag on the page
first_h1 = driver.find_element(By.XPATH, "//h1")

# Get text of h1 tag
first_h1_text = first_h1.text

# Get count of all_img and all_btn
all_img_count = len(all_img)
all_btn_count = len(all_btn)

print(first_h1_text)
print(all_img_count)
print(all_btn_count)