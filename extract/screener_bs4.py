import os
import time

import PyPDF2
import pymongo
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field

from openai import OpenAI

from dotenv import load_dotenv

from backend.data.extract_tickers import top_10_it_companies

from backend.constants import QUARTERS, Q_SALES, Q_EXPENSES, Q_OPM, \
    Q_OPM_PERCENT, Q_OTHER_INCOME, Q_INTEREST, Q_DEPRECIATION, \
    Q_PBT, Q_TAX, Q_PAT, Q_EPS, \
    Q_SALES_PERCENT, Q_EXPENSES_PERCENT, Q_PAT_PERCENT, \
    YEARS, A_SALES, A_EXPENSES, A_OPM, A_OPM_PERCENT, A_OTHER_INCOME, A_INTEREST, A_DEPRECIATION, \
    A_PBT, A_TAX, A_PAT, A_EPS, A_SALES_PERCENT, A_EXPENSES_PERCENT, A_PAT_PERCENT, Q_PDF, A_PDF

load_dotenv()

db_client = pymongo.MongoClient(os.getenv('MONGODB'))
db = db_client[os.getenv('DB_NAME')]
collection_results = db[os.getenv('COLLECTION_RESULTS')]

OPENAI_API = os.getenv('OPENAI_API')


@dataclass
class RangeTableRow:
    key: str
    value: str


@dataclass
class RangeTable:
    title: str = field(init=False)
    data: list[RangeTableRow] = field(init=False)


def download_pdf(url, ticker):
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
                with open(f'{ticker}.pdf', 'wb') as file:
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


def fetch_analysis_from_openai(pdf_filename: str):
    client = OpenAI(api_key=OPENAI_API)
    initial_prompt = """
    You are a financial analyst. 
    I will provide you with the text from a conference call for Quarterly results for a company.
    Go through the text line by line and understand it. 
    There might be some formatting errors in the text so proceed accordingly.
    Give me the most important takeaways from the text in terms of:
    1. Financial Performance Metrics
    2. Management Commentary and Guidance
    3. Market and Competitive Landscape 
    Limit your response to a maximum of 2 sentences for each criteria.
    Also indicate any information or word of caution that makes an investment in this company risky. 
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
        "caution": "<your response>"
    }
    Return a valid json. Do not return any characters before or after the valid json string.
    """

    # Tell me what has been the biggest focus for the company in the text: past, present or future.
    # Please only reply with one of these three options: (past, present, future)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": read_pdf(pdf_filename)}
        ]
    )

    return completion.choices[0].message.content


def get_data_from_screener_using_bs4(ticker: str) -> dict:
    start_time = time.time_ns()
    url = f'https://www.screener.in/company/{ticker}/consolidated/'

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    range_tables = soup.find_all(False, {'class': ['ranges-table']})

    dictionary = {
        'range_tables': [],
        'quarterlyData': {},
        'annualData': {}
    }

    for table in range_tables:
        range_table = RangeTable()
        rows = table.find_all('tr')
        title = rows[0].text.strip()
        list_rows = []
        for row in rows[1:]:
            cols = row.find_all('td')
            key = cols[0].text
            val = cols[1].text
            list_rows.append(RangeTableRow(key, val).__dict__)
        range_table.title = title
        range_table.data = list_rows
        # print(range_table.__dict__)
        dictionary['range_tables'].append(range_table.__dict__)

    table_metadata = [
        [QUARTERS, Q_SALES, Q_EXPENSES, Q_OPM, Q_OPM_PERCENT, Q_OTHER_INCOME, Q_INTEREST, Q_DEPRECIATION,
         Q_PBT, Q_TAX, Q_PAT, Q_EPS, Q_PDF],
        [YEARS, A_SALES, A_EXPENSES, A_OPM, A_OPM_PERCENT, A_OTHER_INCOME, A_INTEREST, A_DEPRECIATION,
         A_PBT, A_TAX, A_PAT, A_EPS, A_PDF],
    ]

    table_dictionary = {}

    try:
        tables = soup.find_all(False, {'class': ['responsive-holder fill-card-width']})[:2]
        for table_index, table in enumerate(tables):
            header_cols = table.find('thead').find('tr').find_all('th')[1:]
            table_dictionary[table_metadata[table_index][0]] = [col.text.strip() for col in header_cols]

            body_rows = table.find('tbody').find_all('tr')
            for row_index, row in enumerate(body_rows[:-1]):
                cols = row.find_all('td')
                # print(cols[0].text.strip(), [col.text.strip().replace(',', '') for col in cols[1:]])
                # dictionary[table_metadata[t_index][r
                # _index + 1]] = [col.text.strip().replace(',', '') for col in cols[1:]]
                table_dictionary[table_metadata[table_index][row_index + 1]] = \
                    [col.text.strip() for col in cols[1:]]

        q_sales = table_dictionary[Q_SALES]
        q_expenses = table_dictionary[Q_EXPENSES]
        q_net_profit = table_dictionary[Q_PAT]
        # print(q_sales)

        q_sales = [int(val.replace(',', '')) for val in q_sales]
        q_expenses = [int(val.replace(',', '')) for val in q_expenses]
        q_net_profit = [int(val.replace(',', '')) for val in q_net_profit]

        dictionary['quarterlyData'][QUARTERS] = table_dictionary[QUARTERS]
        dictionary['quarterlyData'][Q_SALES] = q_sales
        dictionary['quarterlyData'][Q_EXPENSES] = q_expenses
        dictionary['quarterlyData'][Q_PAT] = q_net_profit

        temp_q_sales = q_sales
        temp_q_expenses = q_expenses
        temp_q_net_profit = q_net_profit

        try:
            q_sales_percent = \
                [round(((temp_q_sales[index + 1] - val) / val * 100), 2) for index, val in enumerate(temp_q_sales[:-1])]
            q_expenses_percent = \
                [round(((temp_q_expenses[index + 1] - val) / val * 100), 2) for index, val in
                 enumerate(temp_q_expenses[:-1])]
            q_net_profit_percent = \
                [round(((temp_q_net_profit[index + 1] - val) / val * 100), 2)
                 for index, val in enumerate(temp_q_net_profit[:-1])]

            dictionary['quarterlyData'][Q_SALES_PERCENT] = q_sales_percent
            dictionary['quarterlyData'][Q_EXPENSES_PERCENT] = q_expenses_percent
            dictionary['quarterlyData'][Q_PAT_PERCENT] = q_net_profit_percent
        except ZeroDivisionError as e:
            print('Exception: ZeroDivisionError while transforming data for', ticker)
            print(str(e))
            return None

        a_sales = table_dictionary[A_SALES]
        a_expenses = table_dictionary[A_EXPENSES]
        a_net_profit = table_dictionary[A_PAT]

        a_sales = [int(val.replace(',', '')) for val in a_sales]
        a_expenses = [int(val.replace(',', '')) for val in a_expenses]
        a_net_profit = [int(val.replace(',', '')) for val in a_net_profit]

        dictionary['annualData'][YEARS] = table_dictionary[YEARS]
        dictionary['annualData'][A_SALES] = a_sales
        dictionary['annualData'][A_EXPENSES] = a_expenses
        dictionary['annualData'][A_PAT] = a_net_profit

        temp_a_sales = a_sales
        temp_a_expenses = a_expenses
        temp_a_net_profit = a_net_profit

        try:
            a_sales_percent = \
                [round(((temp_a_sales[index + 1] - val) / val * 100), 2) for index, val in enumerate(temp_a_sales[:-1])]
            a_expenses_percent = \
                [round(((temp_a_expenses[index + 1] - val) / val * 100), 2) for index, val in
                 enumerate(temp_a_expenses[:-1])]
            a_net_profit_percent = \
                [round(((temp_a_net_profit[index + 1] - val) / val * 100), 2)
                 for index, val in enumerate(temp_a_net_profit[:-1])]

            dictionary['annualData'][A_SALES_PERCENT] = a_sales_percent
            dictionary['annualData'][A_EXPENSES_PERCENT] = a_expenses_percent
            dictionary['annualData'][A_PAT_PERCENT] = a_net_profit_percent
        except ZeroDivisionError as e:
            print('Exception: ZeroDivisionError while transforming data for', ticker)
            print(str(e))
            return None

        box_con_calls = soup.find_all(False, {'class': ['show-more-box']})[-1]
        link_first_transcript = box_con_calls.find('li').find('a')['href']
        dictionary['latest_concall_transcript'] = link_first_transcript
        # download_pdf(link_first_transcript, ticker)
        #
        # file_found = False
        # while True:
        #     pdf_files = glob.glob(os.path.join('', '*.pdf'))
        #     for pdf_file in pdf_files:
        #         print(pdf_file)
        #         if pdf_file == f'{ticker}.pdf':
        #             print('Found file')
        #             file_found = True
        #             break
        #     if file_found:
        #         break

        # print('Fetching data from OpenAI')
        # openai_response = fetch_analysis_from_openai(ticker + '.pdf')
        # print(openai_response)
        # dictionary['openai_analysis'] = json.loads(openai_response)

    except Exception as e:
        print('Exception in extract.py:', str(e.args))
        return {}
    print('Total time:', (time.time_ns() - start_time) / 1_000_000_000)
    dictionary['ticker'] = ticker
    return dictionary


for ticker in top_10_it_companies:
    data = get_data_from_screener_using_bs4(ticker)
    result = collection_results.insert_one(data)
    if result.acknowledged:
        print('Document inserted successfully', ticker)
    time.sleep(5)
