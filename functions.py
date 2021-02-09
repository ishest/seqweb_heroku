import streamlit as st
import pandas as pd
import ccxt
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import warnings
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')


okex = ccxt.okex({'type': 'futures'})


def market():
    return okex.fetch_markets()


def get_tickers():
    markets = market()
    fut_weekly_list = list(filter(lambda i: i['type'] == 'futures' and
                                              i['info']['quote_currency'] == 'USD' and
                                              i['info']['alias'] == 'this_week', markets))

    fut_biweekly_list = list(filter(lambda i: i['type'] == 'futures' and
                                     i['info']['quote_currency'] == 'USD' and
                           i['info']['alias'] == 'next_week', markets))

    fut_quarter_list = list(filter(lambda i: i['type'] == 'futures' and
                                              i['info']['quote_currency'] == 'USD' and
                                              i['info']['alias'] == 'quarter', markets))

    fut_biquarter_list = list(filter(lambda i: i['type'] == 'futures' and
                                              i['info']['quote_currency'] == 'USD' and
                                              i['info']['alias'] == 'bi_quarter', markets))

    coins = [i['base'] for i in fut_weekly_list]
    weekly = [i['id'] for i in fut_weekly_list]
    biweekly = [i['id'] for i in fut_biweekly_list]
    quarter = [i['id'] for i in fut_quarter_list]
    biquarter = [i['id'] for i in fut_biquarter_list]
    df = pd.DataFrame([weekly, biweekly, quarter, biquarter])
    df.columns = coins
    df.index = ['weekly', 'bi-weekly', 'quarter', 'bi-quarter']

    return df


def get_prices():
    df_tickers = get_tickers()
    all_tickers = []
    for i in df_tickers.values.tolist():
        for j in i:
            all_tickers.append(j)

    prices = okex.fetch_tickers(symbols=all_tickers, params={'type': 'futures'})

    for ticker in prices:
        prices[ticker] = prices[ticker]['last']

    prices = pd.DataFrame.from_dict(prices, orient='index')

    for i in df_tickers:
        for k in df_tickers.index:
            df_tickers.replace(df_tickers[i].loc[k], float(prices.loc[df_tickers[i].loc[k]]), inplace=True)

    return df_tickers


def spreads():
    prices = get_prices()
    dict = {}
    for i in prices:
        biQQ = (prices[i].loc['bi-quarter'] / prices[i].loc['quarter'] - 1) * 100
        biQBW = (prices[i].loc['bi-quarter'] / prices[i].loc['bi-weekly'] - 1) * 100
        biQW = (prices[i].loc['bi-quarter'] / prices[i].loc['weekly'] - 1) * 100

        QBW = (prices[i].loc['quarter'] / prices[i].loc['bi-weekly'] - 1) * 100
        QW = (prices[i].loc['quarter'] / prices[i].loc['weekly'] - 1) * 100

        biWW = (prices[i].loc['bi-weekly'] / prices[i].loc['weekly'] - 1) * 100

        dict[i] = {'biQ-Q': round(biQQ, 2), 'biQ-BW': round(biQBW, 2), 'biQ-W': round(biQW, 2), 'biW-W_RollOver': round(biWW, 2),
                  'Q-BW': round(QBW, 2), 'Q-W': round(QW, 2)}

    return pd.DataFrame.from_dict(dict, orient='index')


def btc_spread_df():
    btc = pd.read_csv('price_data/BTC.csv', index_col='date')
    btc.index = pd.to_datetime(btc.index, format="%Y-%m-%d %I:%M:%S.%f").strftime('%Y-%m-%d %I:%M')
    btc.drop(columns='Unnamed: 0', inplace=True)

    btc_spread = pd.DataFrame(columns=['biQ-Q', 'biQ-biW', 'biQ-W', 'biW-W', 'Q-biW', 'Q-W'])
    btc_spread['biQ-Q'] = round((btc.biQ / btc.Q - 1) * 100, 2)
    btc_spread['biQ-biW'] = round((btc.biQ / btc.biW - 1) * 100, 2)
    btc_spread['biQ-W'] = round((btc.biQ / btc.W - 1) * 100, 2)
    btc_spread['biW-W'] = round((btc.biW / btc.W - 1) * 100, 2)
    btc_spread['Q-biW'] = round((btc.Q / btc.biW-1) * 100, 2)
    btc_spread['Q-W'] = round((btc.Q / btc.W - 1) * 100, 2)
    btc_spread.index = pd.DatetimeIndex(btc_spread.index)

    return btc_spread


def plot_chart():
    btc_spreads = btc_spread_df()
    fig, ax = plt.subplots()

    # Add x-axis and y-axis
    ax.plot(btc_spreads.index.values,
           btc_spreads[['biQ-Q', 'biQ-biW', 'biQ-W', 'biW-W', 'Q-biW', 'Q-W']], linewidth=1
           )

    # Set title and labels for axes
    ax.set(xlabel="Date",
           ylabel="Spreads"
           )

    # Define the date format
    ax.legend(['biQ-Q', 'biQ-biW', 'biQ-W', 'biW-W', 'Q-biW', 'Q-W'], loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)
    date_form = DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    # ax.set_yticklabels()

    return st.pyplot()
