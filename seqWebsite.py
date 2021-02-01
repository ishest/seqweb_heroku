import streamlit as st
import pandas as pd
import ccxt
import time

okex = ccxt.okex({'type': 'futures'})
markets = okex.fetch_markets()

my_bar = st.progress(0)


st.header('THE BEST ANALYTICAL WEBSITE EVER')


def get_tickers():
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


for percent_complete in range(100):
    time.sleep(0.02)
    my_bar.progress(percent_complete + 1)


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


spread = spreads()
btc_spread = pd.DataFrame(spread.loc['BTC']).T

st.table(btc_spread)

st.table(spread.style.highlight_max())
