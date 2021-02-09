from functions import spreads, plot_chart
import streamlit as st
import ccxt
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import warnings
warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)

okex = ccxt.okex({'type': 'futures'})
markets = okex.fetch_markets()

st.header('THE BEST ANALYTICAL WEBSITE EVER')

if __name__ == '__main__':

    spreads = spreads()

    btc_spread = pd.DataFrame(spreads.loc['BTC']).T
    st.text('BTC price: ' + str(okex.fetch_ticker('BTC/USDC')['last']))
    st.table(btc_spread.style.format("{:.2%}"))

    st.table(spreads.style.highlight_max().highlight_min(color='lightgreen').format("{:.2%}"))

    if st.button('Show Plots'):
        st.header('BTC Spreads')
        try:
            plot_chart()
        except:
            print('error')
