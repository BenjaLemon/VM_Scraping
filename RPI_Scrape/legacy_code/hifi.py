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

def Hifi_Portal_Login(driver):
    driver.get('https://portal.hifi-filter.com/login')
    time.sleep(2)
    emailInput = driver.find_element("xpath", '//*[@id="loginForm"]/div[1]/div[2]/div/input')
    emailInput.send_keys('richard.massara@mlafilters.co.uk')
    pwordInput = driver.find_element("xpath", '//*[@id="loginForm"]/div[1]/div[3]/div/input')
    pwordInput.send_keys('SePaR!(*(1989')
    pwordInput.send_keys(Keys.ENTER)
    return(driver)



'''
CTRL + F on element inspector to open search box and check an xpath/selector
'''

def Scrape_Hifi(codes,thread_num):
    logging.basicConfig(level=logging.ERROR, filename=f'./logs/threaded_errors_{thread_num}.log', encoding='utf-8')
    SEARCH_BOX_XPATH = '//*[@id="applicationCtrl"]/div/div[2]/div/div[1]/div/form/div/div[2]/input'
    TABLE_XPATH = '//*[@id="DataTables_Table_0"]/tbody'
    ERROR_XPATH = './/td[@class="dataTables_empty"]'
    PRODUCT_XPATH = './/tr[@class="odd" or @class="even"]' #.// uses previous element as base while // uses global scope i.e. full HTML 
    GLOBAL_MAX_WAIT = 5
    driver = Instantiate_Driver()
    driver = Hifi_Portal_Login(driver)
    time.sleep(3)
    output_data = []
    client = Client('AC2a95abbb09ae9761d6d57911dd1c9bc1','327d8d0722bbb5b209f1032062aa84e6')      
    start = time.perf_counter()
    for code in codes:
        try:
            if len(output_data) > 200: #save data as a csv in a subdirectory when reaches a large amount of data
                folder = f'./threaded_output_data/thread_{thread_num}'
                file_num = next_file_num(thread_num)
                file_name = f'{folder}/scraped_data_{file_num}.csv'
                df = pd.DataFrame(output_data, columns = ['Code searched', 'Matched code','Part Manufacturer','Part Category on Hifi','Hifi XREF'])
                df.to_csv(file_name,index=False)
                output_data = []

            if time.perf_counter()-start > 21000: #~6hrs elapsed
                index = codes[codes==code].index[0] #select row with elem then get index
                completion_pct = (index/len(codes))*100
                client.messages.create(body=f"Thread {thread_num} alive|{file_num*200} xrefs so far in session",from_='+447360495933',to='+447771837490')
                start= time.perf_counter()
                
        except Exception as error:
            log_error = f"An exception occurred in csv write loop: {type(error).__name__} - {error}"
            logging.error(f'Failed on code {code}|{log_error}')
            print(traceback.format_exc())
            driver.close()
            return(code) #break out of fn as something went wrong

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
                results_table = driver.find_elements('xpath',TABLE_XPATH)
                
                if results_table == []: #catches IndexError if results table has yet to load
                    time.sleep(0.5)
                    continue
                results_table = results_table[0]
               
                #check by class name for empty data message as both the first row of results and error message are at /tbody/tr/td 
                errors = results_table.find_elements('xpath', ERROR_XPATH)
                products = results_table.find_elements('xpath',PRODUCT_XPATH) #this uses the custom xpath selector I made and works 
                
                if errors != []: #i.e there are no results
                    scraped = True
                elif products !=[]:
                    for product in products:
                        macthed_code = ''
                        brand = ''
                        XREF = ''
                        category = ''
                        data = product.find_elements('xpath', './/td[contains(@class,"collapsing")]')  #needs to be relative XPATH, duhhh
                        try:
                            matched_code = data[0].text
                            brand = data[1].text
                            XREF = data[2].text
                            category = data[3].text
                        except IndexError:
                            pass
                        output_data.append([code,matched_code,brand,category,XREF])
                        print([code,matched_code,brand,category,XREF])
                    scraped = True
                time.sleep(0.5)

        except Exception as error:
            log_error = f"An exception occurred in main scrape loop: {type(error).__name__} - {error}"
            logging.error(f'Failed on code {code}|{log_error}')
            print(traceback.format_exc())
            driver.close()
            driver = Instantiate_Driver()
            driver = Hifi_Portal_Login(driver)
         
    #output final data in case <200
    folder = f'./threaded_output_data/thread_{thread_num}'
    file_num = next_file_num(thread_num)
    file_name = f'{folder}/scraped_data_{file_num}.csv'
    df = pd.DataFrame(output_data, columns = ['Code searched', 'Matched code','Part Manufacturer','Part Category on Hifi','Hifi XREF'])
    df.to_csv(file_name,index=False)
    return("Complete")
