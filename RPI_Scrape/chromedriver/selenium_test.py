from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def Instantiate_Driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    chrome_options.BinaryLocation = "/usr/bin/google-chrome"
    driver_path = "/usr/bin/chromedriver"
    #chrome_options.page_load_strategy = 'eager'   # Only waits till html has been loaded + parsed
    chrome_options.page_load_strategy = 'normal'  # Waits for all resources to dl inc. images
    driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    return(driver)


driver = Instantiate_Driver()

driver.get("https://google.com/")
print(driver.title)
driver.quit()
