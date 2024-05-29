import math
import time
from enum import Enum

import pandas as pd
import requests
import datetime
from tabulate import tabulate


def prepare_ticker(p_ticker, p_exchange):
    if p_exchange == 'NSE':
        return p_ticker + '.NS'
    elif p_exchange == 'BSE':
        return p_ticker + '.BO'
    else:
        return p_ticker


def get_current_date():
    # Get the current date
    current_date = datetime.date.today()

    # Extract day, month, and year
    day = current_date.day
    month = current_date.month
    year = current_date.year

    return day, month, year


def get_previous_date(day, month, year):
    today = datetime.date(year, month, day)
    next_date = today + datetime.timedelta(days=-1)

    day = next_date.day
    month = next_date.month
    year = next_date.year

    return day, month, year


def get_next_date(day, month, year):
    today = datetime.date(year, month, day)
    next_date = today + datetime.timedelta(days=1)

    day = next_date.day
    month = next_date.month
    year = next_date.year

    return day, month, year


def get_delta_date(number_of_days):
    tomorrows_date = (str(datetime.date.today() + datetime.timedelta(days=number_of_days))).split('-')
    temp_year = int(tomorrows_date[0])
    temp_month = int(tomorrows_date[1])
    temp_day = int(tomorrows_date[2])
    # print(temp_year, temp_month, temp_day)
    return int(time.mktime(datetime.datetime(temp_year, temp_month, temp_day, 23, 59).timetuple()))


def get_start_end_period(p_date, p_month, p_year) -> [int, int]:
    period1 = int(time.mktime(datetime.datetime(p_year, p_month, p_date, 8, 0).timetuple()))
    period2 = int(time.mktime(datetime.datetime(p_year, p_month, p_date, 18, 0).timetuple()))
    return period1, period2


def prepare_url(p_ticker, period1, period2, p_interval):
    interval = '1d'
    if p_interval == 'daily':
        interval = '1d'
    elif p_interval == 'weekly':
        interval = '1wk'
    elif p_interval == 'monthly':
        interval = '1mo'
    return f'https://query1.finance.yahoo.com/v7/finance/download/{p_ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'


# https://query1.finance.yahoo.com/v7/finance/download/LINCOLN.NS?period1=1595085832&period2=1626621832&interval=1d&events=history&includeAdjustedClose=true


def get_data_from_yahoo_finance(p_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36 '
    }
    # return requests.get(p_url, headers=headers).text
    response = requests.get(p_url, headers=headers).text
    # print(response)
    return response


def get_encoded_period(p_date, p_month, p_year):
    return int(time.mktime(datetime.datetime(p_year, p_month, p_date, 8, 30).timetuple()))


def first_monday_of_year(year):
    first_day = datetime.date(year, 1, 1)

    days_to_add = (0 - first_day.weekday() + 7) % 7
    first_monday_date = first_day + datetime.timedelta(days=days_to_add)

    day = first_monday_date.day

    return day


def dataIsInvalid(data):
    return data == "404 Not Found: Timestamp data missing."


def fetch_price_for_date_from_yf(day, month, year, ticker) -> float:
    period1, period2 = get_start_end_period(day, month, year)
    url = prepare_url(ticker + ".NS", period1, period2, 'daily')
    data = get_data_from_yahoo_finance(url)
    if dataIsInvalid(data):
        return 0
    # print(data)
    return round(float(data.split('\n')[1].split(',')[1]), 2)


def fetch_price_for_date(date, month, year, ticker, delta):
    price = 0
    while price == 0:
        price = fetch_price_for_date_from_yf(date, month, year, ticker)
        if price == 0:
            if delta == "next":
                date, month, year = get_next_date(date, month, year)
            else:
                date, month, year = get_previous_date(date, month, year)
        else:
            break
    return price


def fetch_current_price(ticker):
    date, month, year = get_current_date()
    return fetch_price_for_date(date, month, year, ticker, "previous")


def fetch_open_price_for_year(year, ticker):
    return fetch_price_for_date(1, 1, year, ticker, "next")


def compute_cagr(list_prices: list):
    for index, price in enumerate(list_prices):
        if index == 0:
            continue
        price_ending = list_prices[0]
        price_starting = list_prices[index]
        print(price_starting, price_ending, index)
        cagr = ((price_ending / price_starting) ** (1 / index)) - 1
        print(cagr * 100)
        print()


def fetch_data_for_cagr(ticker: str):
    list_prices = [fetch_current_price(ticker)]
    for year in [2024, 2023, 2022, 2021, 2020, 2019, 2018]:
        price = fetch_open_price_for_year(year, ticker)
        print(price)
        list_prices.append(price)
    print(list_prices)
    print(compute_cagr(list_prices))


def prepare_dataframe(p_response):
    list_date = []
    list_open = []
    list_high = []
    list_low = []
    list_close = []
    list_adj_close = []
    list_volume = []

    array_data = p_response.split('\n')
    # print('array_data', array_data)

    for i in range(1, len(array_data)):
        if array_data[i].split(',')[1] != 'null':
            list_date.append(array_data[i].split(',')[0])
            list_open.append(math.ceil(float(array_data[i].split(',')[1])))
            list_high.append(float(array_data[i].split(',')[2]))
            list_low.append(float(array_data[i].split(',')[3]))
            list_close.append(math.ceil(float(array_data[i].split(',')[4])))
            list_adj_close.append(float(array_data[i].split(',')[5]))
            list_volume.append(float(array_data[i].split(',')[6]))

    temp_df = pd.DataFrame(list(zip(list_date, list_open, list_high, list_low, list_close, list_adj_close, list_volume)))
    columns = array_data[0].split(',')
    # print(columns)
    temp_df.columns = columns

    return temp_df


def print_dataframe(p_dataframe):
    print(tabulate(p_dataframe, headers="keys", tablefmt="psql"))


def fetch_data_last_5_years(ticker):
    period1 = get_encoded_period(1, 1, 2019)
    period2 = get_delta_date(-30)
    url = prepare_url(ticker, period1, period2, p_interval='daily')
    print_dataframe(prepare_dataframe(get_data_from_yahoo_finance(url)))


# fetch_data_last_5_years('TCS.NS')


def get_up_or_down(df):
    for i in range(len(df)):
        if i > 0:
            if df.iloc[i]['Adj Close'] >= df.iloc[i-1]['Adj Close']:
                df.at[i, 'gain'] = df.iloc[i]['Adj Close'] - df.iloc[i-1]['Adj Close']
                df.at[i, 'loss'] = 0
            elif df.iloc[i]['Adj Close'] < df.iloc[i-1]['Adj Close']:
                df.at[i, 'loss'] = df.iloc[i-1]['Adj Close'] - df.iloc[i]['Adj Close']
                df.at[i, 'gain'] = 0
            else:
                df.at[i, 'gain'] = 0
                df.at[i, 'loss'] = 0
    return df


def get_average_gains(df, period):
    for i in range(len(df)):
        n, up, down = 0, 0, 0
        if i == period:
            while n < period:
                if df.iloc[i-n]['gain'] > 0:
                    up += df.iloc[i-n]['gain']
                elif df.iloc[i-n]['loss'] > 0:
                    down += df.iloc[i-n]['loss']
                else:
                    up += 0
                    down += 0
                n += 1
            df.at[i, 'ag'] = up/period
            df.at[i, 'al'] = down/period
        elif i > period:
            df.at[i, 'ag'] = (df.iloc[i-1]['ag'] * (period - 1) + df.iloc[i]['gain'])/period
            df.at[i, 'al'] = (df.iloc[i-1]['al'] * (period - 1) + df.iloc[i]['loss'])/period
            df['ag'] = df['ag'].fillna(0)
            df['al'] = df['al'].fillna(0)
    return df


def get_relative_strength(df, period):
    for i in range(len(df)):
        if i >= period:
            df.at[i, 'rs'] = df.iloc[i]['ag']/df.iloc[i]['al']
            df.at[i, 'rsi'] = (100-(100/(1+df.iloc[i]['rs'])))
    return df


def get_closing_prices_for_rsi(p_ticker, p_exchange):
    ticker = prepare_ticker(p_ticker, p_exchange)
    period1 = get_delta_date(-30)
    period2 = get_delta_date(1)
    url = prepare_url(ticker, period1, period2, 'daily')
    p_response = get_data_from_yahoo_finance(url)
    df = prepare_dataframe(p_response)
    print_dataframe(df)
    df = get_up_or_down(df)
    print_dataframe(df)

    df = get_average_gains(df, 14)
    print_dataframe(df)

    df = get_relative_strength(df, 14)
    print_dataframe(df)

    list_adj_close = []

    array_data = p_response.split('\n')
    # print('array_data', array_data)

    for i in range(1, len(array_data)):
        if array_data[i].split(',')[1] != 'null':
            list_adj_close.append(float(array_data[i].split(',')[5]))

    return list_adj_close[-14:]


def calculate_rsi(p_ticker, p_exchange):
    list_adj_close = get_closing_prices_for_rsi(p_ticker, p_exchange)
    print(len(list_adj_close))
    sum_gain = 0
    sum_loss = 0
    sum_gain_count = 0
    sum_loss_count = 0
    for index, val in enumerate(list_adj_close):
        if index == 0:
            continue
        net = list_adj_close[index] - list_adj_close[index - 1]
        if net >= 0:
            sum_gain += net
            sum_gain_count += 1
        else:
            sum_loss += (net * -1)
            sum_loss_count += 1

    rs = (sum_gain/14) / (sum_loss/14)
    return 100 - (100 / (1 + rs))


print(calculate_rsi('TATAPOWER', 'NSE'))
