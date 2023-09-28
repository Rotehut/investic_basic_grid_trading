# config path
import sys
sys.path.append('../Lib')

# import internal library
from mt5_package import MetaTrader

# import site packages
import pandas as pd
import numpy as np
import time, datetime, gc, json, logging

# Configure the logger
logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

""" Setup Grid """
screen_printing = f"# Setup Session"
MetaTrader().screen_printing(text=screen_printing)

symbol = "EURUSD"
grid_size = 0.00005  # Adjust this to your desired grid spread size
tp_size = 0.00005 # Adjust this to your desired grid tp size
lower_bound = 1.05500
upper_bound = 1.06500
order_size = 0.02  # Adjust this to your desired order size

time_to_sleep = 10

# Define your parameters
current_params = {
    "Setup Grid": {
        "symbol": symbol,
        "grid_size": grid_size,
        "tp_size": tp_size,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "order_size": order_size,
        "current_price": current_price
    }
}

# create grid info
num_levels = int((upper_bound - lower_bound) / grid_size)
grid_prices = [lower_bound + i * grid_size for i in range(num_levels + 1)]
df = pd.DataFrame(grid_prices, columns=['price'])

df['size'] = order_size
df['tp_buy_side'] = df['price'] + tp_size
df['tp_sell_side'] = df['price'] - tp_size
df['status'] = 'waiting'
df['ticket'] = None

# record total order
total_order = len(df)

""" boolean legacy check"""    
try:
    # migrate legacy db
    df_legacy = pd.read_csv(f'{symbol}_{lower_bound}_{upper_bound}.csv')
    df_legacy['ticket'] = df_legacy['ticket'].astype(int)

    # migrate legacy params
    loaded_params = json.load(open("setup_config.json", "r"))

    # legacy to check
    bool_stat = loaded_params == current_params
except:
    bool_stat = False


""" #0 Pre Session """
screen_printing = f"#0 Pre Sessopm"
MetaTrader().screen_printing(text=screen_printing)


# force clear opened order and pending order
while False:
    MetaTrader().close_all_opened_order(symbol=symbol)
    MetaTrader().cancel_all_pending_order(symbol=symbol)
    break

""" #1 Initiating Session """
screen_printing = f"#1 Initiaing Session"
MetaTrader().screen_printing(text=screen_printing)

# follow legacy path
while bool_stat:
    logging.warning('follow legacy path')

    MetaTrader().screen_printing(text=f"Legacy Grid Creation")
    df = df_legacy.copy()

    # clear non-related order
    MetaTrader().cancel_pending_out_of_list(df_col=df.ticket, symbol=symbol)
    MetaTrader().close_opened_out_of_list(df_col=df.ticket, symbol=symbol)

    break

# follow new path
while bool_stat == False:
    logging.warning('follow new path')
    MetaTrader().screen_printing(text=f"New Grid Creation")

    # Save to JSON file
    with open("setup_config.json", "w") as f:
        json.dump(current_params, f, indent=4)

    MetaTrader().cancel_pending_out_of_list(df_col=df.ticket, symbol=symbol)
    MetaTrader().close_opened_out_of_list(df_col=df.ticket, symbol=symbol)

    # update price
    current_price = MetaTrader().get_current_price(symbol=symbol)

    # execute and clear the waiting status out of the dataframe
    if current_price >= lower_bound and current_price <= upper_bound:  
        for idx, order in df.iterrows():
            if pd.isna(order['ticket']) and order['status'] == "waiting" and current_price > order['price']:
                # create buy order
                res = MetaTrader().place_limit_buy_order(symbol=symbol, lot=order['size'], price=order['price'], tp=order['tp_buy_side'])

                # record
                df.at[idx, 'ticket'] = res.order
                df.at[idx, 'status'] = "pending_buy"

            elif pd.isna(order['ticket']) and order['status'] == "waiting" and current_price < order['price']:
                # create sell order
                res = MetaTrader().place_limit_sell_order(symbol=symbol, lot=order['size'], price=order['price'], tp=order['tp_sell_side'])

                # record
                df.at[idx, 'ticket'] = res.order
                df.at[idx, 'status'] = "pending_sell"
    
    # save to csv
    df.to_csv(f'{symbol}_{lower_bound}_{upper_bound}.csv', index=False)
    break


""" #2 Trading Session"""
screen_printing = f"#2 Trading Session"
MetaTrader().screen_printing(text=screen_printing)

while True:
    # update current price 
    current_price = MetaTrader().get_current_price(symbol=symbol) 

    # update cache for pending order and opened order
    cache_pending = MetaTrader().update_cache_pending_order(symbol=symbol)
    cache_opened = MetaTrader().update_cache_opened_order(symbol=symbol)

    # Checking order
    MetaTrader().screen_printing(text=f"checking order")

    # Logging
    logging.info(f'start checking')
    logging.info(f'current_price: {current_price}')
    logging.info(f'cache pending: {cache_pending}')
    logging.info(f'cache pending: {cache_opened}')

    # loop to check
    for idx, order in df.iterrows():
        # MetaTrader().screen_printing(text=f"checking order uuid {idx+1} of {len(df)}")

        # Handling pending order
        if order['status'] == "pending_buy" or order['status'] == "pending_sell":
            if int(order['ticket']) in cache_pending:
                pass
            elif int(order['ticket']) in cache_opened and order['status'] == "pending_buy":
                df.at[idx, 'status'] = "opened_buy"
            elif int(order['ticket']) in cache_opened and order['status'] == "pending_sell":
                df.at[idx, 'status'] = "opened_sell"
            elif MetaTrader().check_close_order(ticket=order['ticket']):
                df.at[idx, 'status'] = "waiting"
                df.at[idx, 'ticket'] = None

        # Handling opened order
        elif order['status'] == "opened_buy" or order['status'] == "opened_sell":
            if int(order['ticket']) in cache_opened:
                pass
            elif MetaTrader().check_close_order(ticket=order['ticket']):
                df.at[idx, 'status'] = "waiting"
                df.at[idx, 'ticket'] = None

        # Handling waiting order
        elif order['status'] == "waiting":
            if current_price > float(order['price']):
                # create buy order
                res = MetaTrader().place_limit_buy_order(symbol=symbol, lot=order['size'], price=order['price'], tp=order['tp_buy_side'])
                df.at[idx, 'ticket'] = res.order
                df.at[idx, 'status'] = "pending_buy"
            elif current_price < float(order['price']):
                # create sell order
                res = MetaTrader().place_limit_sell_order(symbol=symbol, lot=order['size'], price=order['price'], tp=order['tp_sell_side'])
                df.at[idx, 'ticket'] = res.order
                df.at[idx, 'status'] = "pending_sell"

        # Handling weird status out of control===
        else:
            print("Weird status from NOWHERE")
    
    # save to csv
    df.to_csv(f'{symbol}_{lower_bound}_{upper_bound}.csv', index=False)

    logging.info(f'end checking')

    # time sleep until the next round
    time.sleep(time_to_sleep)