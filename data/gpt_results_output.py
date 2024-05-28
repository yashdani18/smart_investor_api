import json
import os

import pymongo
from dotenv import load_dotenv
load_dotenv()

output = [
    """
        {
            "ticker": "TCS", 
            "caution": "The company's expenses have been increasing at a significant rate compared to revenue, which may indicate potential profitability challenges. Additionally, the stock's high P/E ratio relative to the industry P/E ratio might suggest overvaluation.",
            "score": {
                "value": "4",
                "reason": "While the company has shown growth in revenue and profit over the years, the increasing expenses pose a risk. The high P/E ratio also raises concerns about the stock's valuation, leading to a moderate investment score."
            }
        }
    """,
    """
        {
            "ticker": "INFY", 
            "caution": "The increasing expenses trend over the quarters and years raises concerns about the company's cost management efficiency and sustainability of profit margins.",
            "score": {
                "value": "7",
                "reason": "The company has shown a consistent growth in revenue and profit after tax over the quarters and years, with strong ROE and ROCE ratios, indicating good performance and efficiency in capital utilization."
            }
        }
    """,
    """
        {
            "ticker": "HCLTECH", 
            "caution": "The company's expenses are increasing, which may impact future profitability despite consistent revenue growth.",
            "score": {
                "value": "7",
                "reason": "The stock has a moderate P/E ratio compared to industry average, good ROE and ROCE, consistent revenue growth, and positive profit after tax. However, the increasing expenses pose a slight risk."
            }
        }
    """,
    """
        {
            "ticker": "WIPRO", 
            "caution": "The profit after tax has shown variations in the last few quarters which may indicate inconsistency in earnings.",
            "score": {
                "value": "7",
                "reason": "The company has a moderate P/E ratio compared to the industry, stable revenue growth over the years, and a decent ROE and ROCE, suggesting a potential for growth and profitability."
            }
        }
    """,
    """
        {
            "ticker": "LTIM", 
            "caution": "The company has a high P/E ratio compared to the industry average, indicating the stock may be overvalued. Additionally, the revenue and profit after tax fluctuate significantly in the last few quarters and years, which may indicate instability.",
            "score": {
                "value": "5",
                "reason": "The company's ROE and ROCE are good, suggesting efficient use of capital, but the high P/E ratio and fluctuating financial performance raise concerns, leading to a neutral investment perspective."
            }
        }
    """,
    """
        {
            "ticker": "TECHM", 
            "caution": "The company's profit after tax has shown inconsistency over the quarters and years, indicating potential instability in earnings.",
            "score": {
                "value": "6",
                "reason": "The stock has a moderate P/E ratio, positive ROE and ROCE, and consistent revenue growth over the years, showing a promising investment potential."
            }
        }
    """,
    """
        {
            "ticker": "OFSS", 
            "caution": "The stock P/E ratio is lower than the industry average P/E ratio, which may suggest lower growth expectations compared to industry peers.",
            "score": {
                "value": "7",
                "reason": "The company has consistently shown growth in revenue and profit over the years. The ROE and ROCE are also strong, indicating efficient use of capital."
            }
        }
    """,
    """
        {
            "ticker": "POLICYBZR", 
            "caution": "The company has been consistently reporting negative profits after tax for multiple quarters and years, indicating significant financial instability.",
            "score": {
                "value": "2",
                "reason": "The high P/E ratio, low profitability, and consistent negative profits make this investment very risky and unattractive."
            }
        }
    """,
    """
        {
            "ticker": "PERSISTENT", 
            "caution": "The high stock P/E ratio compared to industry P/E ratio and the significant fluctuation in profit after tax over the years pose a risk for the investment.",
            "score": {
                "value": "5",
                "reason": "The company has shown consistent revenue growth over the quarters and years with a decent ROE and ROCE. However, the high P/E ratio and fluctuating profits suggest a more neutral outlook for the investment."
            }
        }
    """,
    """
        {   
            "ticker": "LTTS", 
            "caution": "The increasing gap between expenses and revenue over the years could indicate potential issues with cost management or pricing strategies, which could pose a risk for investors.",
            "score": {
                "value": "5",
                "reason": "The stock has a relatively high P/E ratio compared to the industry, but the strong ROE and ROCE indicate good returns on equity and capital employed which could be positive for investors."
            }
        }
    """
]

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_financials_analysis = db['top_10_it_financials_analysis']


for val in output:
    json_response = json.loads(val)
    print(json_response['ticker'])
    if collection_financials_analysis.insert_one(json_response).acknowledged:
        print('Document for', json_response['ticker'], 'inserted successfully')
    # print(json_response['caution'])
    # print(json_response['score']['value'])
    # print(json_response['score']['reason'])
    # print()
    print()
