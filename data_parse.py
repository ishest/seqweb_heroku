import pandas as pd
import ccxt
import datetime
import schedule
import time

okex = ccxt.okex({'type': 'futures'})
markets = okex.fetch_markets()


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
    # print(prices)

    for i in df_tickers:
        for k in df_tickers.index:
            df_tickers.replace(df_tickers[i].loc[k], float(prices.loc[df_tickers[i].loc[k]]), inplace=True)

    return df_tickers


def sum_prices():
    prices = get_prices()
    dict = {}
    for i in prices:
        biQ = prices[i].loc['bi-quarter']
        Q = prices[i].loc['quarter']
        biW = prices[i].loc['bi-weekly']
        W = prices[i].loc['weekly']

        dict[i] = {'date':  datetime.datetime.utcnow() + datetime.timedelta(hours=-8), 'biQ': biQ, 'Q': Q, 'biW': biW, 'W': W}

    return dict


def get_prices_in_file():
    print('Hello, I am running the process')
    for i in sum_prices():
        try:
            df = pd.read_csv('price_data/' + i + '.csv', index_col=0)
            df = df.append({'date': sum_prices()[i]['date'], 'biQ': sum_prices()[i]['biQ'],
                                        'Q': sum_prices()[i]['Q'], 'biW': sum_prices()[i]['biW'], 'W': sum_prices()[i]['W']},
                           ignore_index=True)
            df.to_csv('price_data/' + i + '.csv')

        except:
            print('no data')


schedule.every(20).minutes.do(get_prices_in_file)
while True:
    schedule.run_pending()
    time.sleep(1)
