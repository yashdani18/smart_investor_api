import json

from dotenv import load_dotenv
import os
import pymongo

from backend.constants import PRICE, STOCK_PE, HIGH_LOW
from backend.data.extract_tickers import top_10_it_companies

load_dotenv()

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_tickers = db['top_10_it_companies']

for ticker in top_10_it_companies:
    collection_tickers.insert_one({'ticker': ticker})

# db_client = pymongo.MongoClient(os.getenv('MONGODB'))
# db = db_client[os.getenv('DB_NAME')]
# print(os.getenv('MONGODB'))
# print(os.getenv('DB_NAME'))
# col_tickers = db['col_tickers']
# results = col_tickers.find()
# for result in results:
#     print(result['_id'], result['ticker'])
# json_response = loads(dumps(results))
# print(json_response)

# import requests
# from bs4 import BeautifulSoup
#
# url = 'https://www.screener.in/company/TCS/consolidated/'
# html = requests.get(url).text
# soup = BeautifulSoup(html, 'lxml')

# rows = soup.find(False, {'class': ['responsive-holder fill-card-width']}).find('tbody').find_all('tr')
# cells = rows[-1].find_all('td')
# for cell in cells[1:]:
#     print('https://www.screener.in' + cell.find('a')['href'])


# def download_file(download_url):
#     # response = urllib2.urlopen(download_url)
#     response = requests.get(download_url)
#     file = open("document.pdf", 'wb')
#     file.write(response.content)
#     file.close()
#     print("Completed")
#
#
# box_con_calls = soup.find_all(False, {'class': ['show-more-box']})[-1]
# first_transcript = box_con_calls.find('li').find('a')['href']
# print(first_transcript)
# download_file(first_transcript)

dictionary = {
    PRICE: {
        'index': 1,
        'val': 0
    },
    HIGH_LOW: {
        'index': 2,
        'val': 0
    },
    STOCK_PE: {
        'index': 1,
        'val': 0
    }
}

for key, value in dictionary.items():
    print(key, value['index'], value['val'])

text = """```json
[
    {
        "criteria": [
            {
                "title": "Financial Performance Metrics",
                "text": "TCS reported strong financial performance with the highest operating margin of 26% in the last 12 quarters, FY 2024 revenue growth at 6.8% in rupee terms, net margin at 19.3%, and record Q4 TCV of $13.2 billion, showing solid deal momentum and double-digit growth."
            },
            {
                "title": "Management Commentary and Guidance",
                "text": "Management expressed caution due to short-term demand uncertainty and volatility in customer decisions, noting pent-up demand in sectors like consumer business, insurance, manufacturing, airlines, and transportation. They highlighted the unpredictability in customer readiness to proceed with discretionary projects based on ROI and market confidence."
            },
            {
                "title": "Market and Competitive Landscape",
                "text": "TCS highlighted strong growth opportunities in sectors such as insurance, manufacturing, consumer business, airlines, transportation, and capital markets. They mentioned a focus on strategic partnerships, risk & compliance spend, and confidence in long-term growth trajectories. Management emphasized the need for agility to align with the changing paradigm in customer decisions and market dynamics."
            }
        ],
        "caution": "Although TCS has shown resilience and growth in key sectors, the unpredictability in customer decisions and short-term demand uncertainty pose risks in revenue predictability and growth acceleration. Investors should closely monitor the company's ability to convert the strong TCV into revenue amidst changing customer priorities and market conditions."
    }
]
```"""

dictionary = {}
dictionary['some'] = json.loads(text[7:-3])
print(dictionary)

