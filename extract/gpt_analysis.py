import glob
import json
import os
import time
from dataclasses import dataclass, field

import PyPDF2
import requests
from openai import OpenAI

from backend.data.extract_tickers import top_10_it_companies
from dotenv import load_dotenv
import pymongo

from backend.constants import TICKER, PRICE, HIGH, LOW, STOCK_PE, INDUSTRY_PE, INTRINSIC_VALUE, \
    GRAHAM_NUMBER, CFO, PAT, ROE, ROCE, \
    Q_SALES, Q_EXPENSES, Q_PAT, A_SALES, A_EXPENSES, A_PAT

load_dotenv()


@dataclass
class Criteria:
    title: str = field(init=False)
    text: str = field(init=False)


@dataclass
class Score:
    value: str = field(init=False)
    reason: str = field(init=False)


@dataclass
class ConcallAnalysis:
    criteria: list[Criteria] = field(init=False)
    caution: str = field(init=False)
    score: Score = field(init=False)



def download_pdf(url, p_ticker):
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36 '
        }
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Check if the Content-Type header is 'application/pdf'
            if response.headers['Content-Type'] == 'application/pdf':
                # Open a local file with write-binary mode
                with open(f'{p_ticker}.pdf', 'wb') as file:
                    # Write the content of the response to the file in chunks
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print("File downloaded successfully")
            else:
                print("The URL does not point to a PDF file")
        else:
            print(f"Failed to retrieve the file. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def read_pdf(filename: str):
    with open(filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        # Iterate through each page and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text


db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_ratios = db['top_10_it_ratios']
collection_results = db['top_10_it_results']
collection_concall_analysis = db['top_10_it_concall_analysis']
collection_results_analysis = db['top_10_it_results_analysis']
OPENAI_API = os.getenv('OPENAI_API')

for ticker in top_10_it_companies:
    # if ticker == 'TCS' or ticker == 'INFY' or ticker == 'HCLTECH' or ticker == 'LTIM' \
    #         or ticker == 'WIPRO' or ticker == 'TECHM' or ticker == 'OFSS' or ticker == 'LTTS'\
    #         or ticker == 'POLICYBZR':
    #     continue
    print('Starting flow for:', ticker)
    ticker_ratios = collection_ratios.find_one({'ticker': ticker})
    ticker_results = collection_results.find_one({'ticker': ticker})
    # print(ticker_ratios['ticker'])
    # print(ticker_results['ticker'])

    current_price = ticker_ratios[PRICE]
    stock_pe = ticker_ratios[STOCK_PE]
    industry_pe = ticker_ratios[INDUSTRY_PE]
    intrinsicValue = ticker_ratios[INTRINSIC_VALUE]
    grahamNumber = ticker_ratios[GRAHAM_NUMBER]
    cfo = ticker_ratios[CFO]
    pat = ticker_ratios[PAT]
    roe = ticker_ratios[ROE]
    roce = ticker_ratios[ROCE]
    high = ticker_ratios[HIGH]
    low = ticker_ratios[LOW]

    str_q_sales = str(ticker_results['quarterlyData'][Q_SALES])
    str_q_expenses = str(ticker_results['quarterlyData'][Q_EXPENSES])
    str_q_pat = str(ticker_results['quarterlyData'][Q_PAT])

    str_a_sales = str(ticker_results['annualData'][A_SALES])
    str_a_expenses = str(ticker_results['annualData'][A_EXPENSES])
    str_a_pat = str(ticker_results['annualData'][A_PAT])

    link = ticker_results['latest_concall_transcript']

    # download_pdf(link, ticker)
    #
    # pdf_filename = f'{ticker}.pdf'
    # file_found = False
    # while True:
    #     pdf_files = glob.glob(os.path.join('', '*.pdf'))
    #     for pdf_file in pdf_files:
    #         print(pdf_file)
    #         if pdf_file == f'{ticker}.pdf':
    #             file_found = True
    #             break
    #     if file_found:
    #         break

    # print('file found')

    initial_prompt = """
            You are a financial analyst. 
            I will provide you with the text from a conference call for Quarterly results for a company.
            Go through the text line by line and understand it. 
            There might be some formatting errors in the text so proceed accordingly.
            Give me the most important takeaways from the text in terms of:
            1. Financial Performance Metrics
            2. Management Commentary and Guidance
            3. Market and Competitive Landscape 
            Limit your response to a maximum of 1 sentence for each criteria.
            Also indicate any information or word of caution that makes an investment in this company risky.
            Also provide me with a score from 0 to 10 from a potential investment perspective; 0 being strong dont buy and 10 being strong buy;  
            Justify the score you assign with a reason in 1 sentence.
            Provide the output in a json format as follows:
            {
                "criteria": [
                    {
                        title: '<criteria 1>', 
                        text: '<your response>'
                    }, 
                    {
                        title: '<criteria 2>', 
                        text: '<your response>'
                    }, 
                    {
                        title: '<criteria 3>', 
                        text: '<your response>'
                    }
                ], 
                "caution": "<your response>", 
                "score": {
                    "value": "<your response>", 
                    "reason:: "<your response>"
                }
            }
            Return a valid json. Do not return any characters before or after the valid json string.
            Check the response string for potential errors in json formatting. Try parsing the json 
            yourself to see if the string is a valid json. Only if it is a valid json, give me the result.
            Else retry and return a valid json.
            """

    financial_prompt = """
            You are a financial analyst. 
            I will provide you with a few fundamental ratios for a stock market equity instrument.
            I will also provide a comma separated list of quarterly results for revenue, expenses and profit after tax;
            this comma separated list of results are in crores of rupees.  
            Indicate any information or word of caution that makes an investment in this company risky. 
            Limit your response for caution to 2 sentences.
            Also provide me with a score from 0 to 10 from a potential investment perspective; 
            0 being most bearish and 10 being most bullish;  
            Justify the score you assign with a reason in 2 sentence.
            Provide the output in a json format as follows:
            {
                "caution": "<your response>", 
                "score": {
                    "value": "<your response>", 
                    "reason:: "<your response>"
                }
            }
            Return a valid json. Do not return any characters before or after the valid json string.
        """

    financial_context = f"""
            Current price: {current_price}, 
            52 week high: {high}, 
            52 week low: {low}, 
            Stock P/E ratio: {stock_pe}, 
            Industry P/E: {industry_pe}, 
            Intrinsic Value: {intrinsicValue}, 
            Graham Number: {grahamNumber}, 
            Cashflow from Operations: {cfo}, 
            Profit after Tax: {pat}, 
            ROE: {roe}, 
            ROCE: {roce}, 
            Revenue for last few quarters: {str_q_sales},
            Expenses for last few quarters: {str_q_expenses},
            Profit after Tax for last few quarters: {str_q_pat}, 
            Revenue for last few years: {str_a_sales},
            Expenses for last few years: {str_a_expenses},
            Profit after Tax for last few years: {str_a_pat} 
        """

    client = OpenAI(api_key=OPENAI_API)

    # completion = client.chat.completions.create(
    #     model="gpt-4-turbo",
    #     # model="gpt-3.5-turbo-instruct",
    #     messages=[
    #         {"role": "system", "content": initial_prompt},
    #         {"role": "user", "content": read_pdf(pdf_filename)}
    #     ]
    # )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": financial_prompt},
            {"role": "user", "content": financial_context}
        ]
    )

    output = completion.choices[0].message.content

    print(output)
    time.sleep(5)
    print()
    print()


