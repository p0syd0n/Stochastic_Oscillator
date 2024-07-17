import ccxt
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
import matplotlib
matplotlib.use('TkAgg') # TkAgg Qt5Agg
import matplotlib.pyplot as plt
import mplcursors  

load_dotenv()
testnet = False
exchange = ccxt.bitmex()

if testnet:
    exchange.set_sandbox_mode(True)  # enable sandbox mode

def fetch_ohlcv(symbol, timeframe, limit):
    global exchange
    # Fetch OHLCV data
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    # Convert to DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


def main():
    symbol = "BTC/USDT"
    timeframe = "1d"
    limit = 1000
    data = fetch_ohlcv(symbol, timeframe, limit)
    print(data)

    lowest_low = data['low'].min() # Getting the minimim of all the values of low
    highest_high = data['high'].max() # Getting the maximum of all the values of high

    for index, row in data.iterrows():
        close = row['close']
        percentK = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        data.at[index, '%K'] = percentK

    data['%D'] = data['%K'].rolling(window=3).mean()
    print(data)
    print(data.iloc[-1]['%K'])

    fig, ax = plt.subplots()

    timestamps = data['timestamp']
    percent_k_point = data['%K']
    percent_d_point = data['%D']
    closing_price_set = data['close']

    line_k = ax.plot(timestamps, percent_k_point, marker='o', linestyle='-', color='b', label='%K')

    line_d = ax.plot(timestamps, percent_d_point, marker='o', linestyle='-', color='g', label='%D')

    def on_hover(sel):
        index = sel.target.index
        closing_price = closing_price_set.iloc[index]
        date = timestamps.iloc[index]

        sel.annotation.set_text(f'Date: {date} \n Closing Price : {closing_price}')


    # Customize the plot
    ax.set_xlabel('Day')
    ax.set_ylabel('%')
    ax.set_title('Stochastic Oscillator')
    ax.grid(True)
    ax.legend()

    # Connect mplcursors to the line plot
    mplcursors.cursor(line_k, hover=True).connect('add', on_hover)
    mplcursors.cursor(line_d, hover=True).connect('add', on_hover)

    plt.savefig('file.png')
    # Show the plot
    plt.show()


main()