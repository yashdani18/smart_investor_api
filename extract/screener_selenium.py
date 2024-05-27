import os
import time
from dataclasses import dataclass

import pymongo
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from backend.constants import PRICE, HIGH_LOW, STOCK_PE, INDUSTRY_PE, INTRINSIC_VALUE, GRAHAM_NUMBER, \
    CFO, PAT, TICKER, ROCE, ROE, HIGH, LOW
from data.extract_tickers import top_10_it_companies

from dotenv import load_dotenv

load_dotenv()

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
print(os.getenv('MONGODB'))
print(os.getenv('DB_NAME'))


@dataclass
class FundamentalRatios:
    ticker: str
    price: float
    high: float
    low: float
    stock_pe: float
    industry_pe: float
    intrinsic_value: float
    graham_number: float
    cashflow_operations: float
    profit_after_tax: float


def get_data_from_screener_using_selenium(ticker):
    options = None
    options = Options()
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=options)
    driver.get('https://www.screener.in/login/')

    field_username = driver.find_element(By.NAME, 'username')
    ActionChains(driver).send_keys_to_element(field_username, os.getenv('SCREENER_USERNAME')).perform()

    field_password = driver.find_element(By.NAME, 'password')
    ActionChains(driver).send_keys_to_element(field_password, os.getenv('SCREENER_PASSWORD')).perform()

    field_password.send_keys(Keys.RETURN)

    for ticker in top_10_it_companies:
        try:
            search_dashboard = WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located((By.ID, "desktop-search"))
            )
            field_company = search_dashboard.find_element(By.CLASS_NAME, "u-full-width")
            field_company.clear()
            field_company.send_keys(ticker)
            time.sleep(1)
            field_company.send_keys(Keys.RETURN)

            try:
                # Wait for the data (top ratios) to load
                results = WebDriverWait(driver, 10).until(
                    expected_conditions.presence_of_element_located((By.ID, "top-ratios"))
                )
                time.sleep(2)

                # Find all fundamental ratios
                cells = results.find_elements(By.CSS_SELECTOR, "li.flex.flex-space-between")

                dictionary = {
                    PRICE: {
                        'index': 1,
                        'val': ''
                    },
                    HIGH_LOW: {
                        'index': 2,
                        'val': ''
                    },
                    STOCK_PE: {
                        'index': 3,
                        'val': ''
                    },
                    INDUSTRY_PE: {
                        'index': 9,
                        'val': ''
                    },
                    INTRINSIC_VALUE: {
                        'index': 12,
                        'val': ''
                    },
                    GRAHAM_NUMBER: {
                        'index': 13,
                        'val': ''
                    },
                    CFO: {
                        'index': 25,
                        'val': ''
                    },
                    PAT: {
                        'index': 26,
                        'val': ''
                    },
                    ROCE: {
                        'index': 6,
                        'val': ''
                    },
                    ROE: {
                        'index': 7,
                        'val': ''
                    }
                }

                for key, value in dictionary.items():
                    cell_index = value['index']
                    cell_values = cells[cell_index].text.split('\n')
                    if len(cell_values) > 1:
                        value['val'] = cell_values[1]

                val_price = dictionary[PRICE]['val']
                val_stock_pe = dictionary[STOCK_PE]['val']
                val_industry_pe = dictionary[INDUSTRY_PE]['val']
                val_intrinsic_value = dictionary[INTRINSIC_VALUE]['val']
                val_graham_number = dictionary[GRAHAM_NUMBER]['val']
                val_cfo = dictionary[CFO]['val']
                val_pat = dictionary[PAT]['val']
                val_roce = dictionary[ROCE]['val']
                val_roe = dictionary[ROE]['val']
                val_high_low = dictionary[HIGH_LOW]['val'][1:].strip()

                return_value = {
                    TICKER: ticker,
                    STOCK_PE: float(val_stock_pe),
                    INDUSTRY_PE: float(val_industry_pe),
                    PRICE: float(val_price[1:].strip().replace(',', '')),
                    INTRINSIC_VALUE: float(val_intrinsic_value[1:].strip().replace(',', '')),
                    GRAHAM_NUMBER: float(val_graham_number[1:].strip().replace(',', '')),
                    CFO: float(val_cfo[1:-3].strip().replace(',', '')),
                    PAT: float(val_pat[1:-3].strip().replace(',', '')),
                    ROE: float(val_roe[:-1].strip()),
                    ROCE: float(val_roce[:-1].strip()),
                    HIGH: float(val_high_low.split(' / ')[0].replace(',', '')),
                    LOW: float(val_high_low.split(' / ')[1].replace(',', ''))
                }

                print(return_value)
                collection_it_ratios = db['top_10_it_ratios']
                result = collection_it_ratios.insert_one(return_value)
                if result.acknowledged:
                    print('Document inserted successfully')
                time.sleep(1)
                # return dictionary
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                return {}
        except:
            return {}


print(get_data_from_screener_using_selenium('TCS'))
