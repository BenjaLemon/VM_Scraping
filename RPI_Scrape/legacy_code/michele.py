#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time
import traceback
import logging
import timeit
from twilio.rest import Client
from os import listdir

def next_file_num(thread_num):
    rel_path=f"./threaded_output_data/thread_{thread_num}"
    #path = os.path.join(os.getcwd(),rel_path)
    files = listdir(rel_path)
    files = [file for file in files if file.endswith(".csv")]
    return(max([int(x[x.rfind('_')+1:x.rfind('.')])+1 for x in files]+[0]))

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

def Scrape_Michele(codes,thread_num):
    logging.basicConfig(level=logging.ERROR, filename=f'./threaded_errors_{thread_num}.log', encoding='utf-8')
    URL = 'https://e-commerce.michelecaroli.com/wso/pages/user/wso0201.jsf'
    SEARCH_BOX_XPATH = '//*[@id="mobile_search:form:value"]'
    NO_RESULTS_XPATH = '//*[@id="ergon_form:ergon_found:grid"]/div/div'
    PRODUCT_XPATH = '//*[@id="loop-products"]/li/div/div'
    DATA_XPATH = '//a[@title="View Details"]' #matches with the xpath of the category and code a tags
    GLOBAL_MAX_WAIT = 5
    driver = Instantiate_Driver()
    driver.get(URL)
    output_data = []
    client = Client('ACfb485306a338b1318ed1d0e691c212f5','506f8665a5ff66fcba9070b34b15182a')
    start = time.perf_counter()
    print('Code started')
    #client.messages.create(body=f"Thread {thread_num} started",from_='+12763228326',to='+447771837490')
    for code in codes:
        try:
            if len(output_data) > 200: #save data as a csv in a subdirectory when reaches a large amount of data
                folder = f'./threaded_output_data/thread_{thread_num}'
                file_num = next_file_num(thread_num)
                file_name = f'{folder}/Michele_scraped_data_{file_num}.csv'
                df = pd.DataFrame(output_data, columns = ['Code searched', 'Matched code','Part Category on Michele','Link to Michele product'])
                df.to_csv(file_name,index=False)
                output_data = []
                client.messages.create(body=f"{200*file_num} xrefs found in session by thread {thread_num}",from_='+12763228326',to='+447771837490')

            if time.perf_counter()-start > 7200: #2hrs elapsed
                index = codes[codes==code].index[0] #select row with elem then get index
                #completion_pct = (index/len(codes))*100
                #client.messages.create(body=f"Thread {thread_num} alive|{file_num*100} xrefs so far in session",from_='+12763228326',to='+447771837490')
                start= time.perf_counter()
                
        except Exception:
            client.messages.create(body=f"Thread {thread_num} Exception in write loop",from_='+12763228326',to='+447771837490')
            driver.close()
            return() #break out of fn as something went wrong

        try:
            while True: #loops until we guarantee the input has been registered properly
                try:
                    WebDriverWait(driver, GLOBAL_MAX_WAIT).until(EC.visibility_of_element_located((By.XPATH, SEARCH_BOX_XPATH)))
                    elem = driver.find_element('xpath',SEARCH_BOX_XPATH)
                    elem.clear()
                    elem.send_keys(code)
                    elem.send_keys(Keys.ENTER)
                    time.sleep(1)
                    break
                except StaleElementReferenceException:
                    pass

            scraped = False
            while not(scraped): #loops until data is scraped in case of weird loading time slowness
                errors = driver.find_elements('xpath',NO_RESULTS_XPATH)
                products = driver.find_elements('xpath',PRODUCT_XPATH)
                if errors != []: #i.e there are no results
                    scraped = True
                elif products !=[]:
                    for product in products:
                        data = product.find_elements('xpath',DATA_XPATH)
                        matched_code = data[0].text
                        if matched_code == '':
                            matched_code = data[1].text
                            category = ''
                        else:
                            category = data[1].text
                        link = data[1].get_attribute('href')
                        output_data.append([code,matched_code,category,link])
                        #print([code,matched_code,category,link])
                    scraped = True
            time.sleep(0.5)

        except:
            logging.error(f'Failed on code {code}')
            driver.close()
            driver = Instantiate_Driver()
            driver.get(URL)



