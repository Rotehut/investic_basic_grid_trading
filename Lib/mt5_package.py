import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import datetime as datetime
import time, logging

class MetaTrader():
    def __init__(self):
        # Create the bound between MT5 and Python
        mt5.initialize()
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()

        logging.basicConfig(filename='trading_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
            
    def place_market_buy_order(self,symbol,lot,deviation,filling_type):
        # Create dictionnary request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "deviation": deviation,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC
        }
        order_res = mt5.order_send(request)
        
        logging.info(f'place market buy order, REQUEST: {request}')
        logging.info(f'place market buy order, RETURN:{order_res}')

        return order_res
        
    def place_market_sell_order(self,symbol,lot,deviation,filling_type):
        # Create dictionnary request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "deviation": deviation,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC
        }
        order_res = mt5.order_send(request)

        logging.info(f'place market sell order, REQUEST: {request}')
        logging.info(f'place market sell order, RETURN:{order_res}')

        return order_res
        
    def close_opened_buy_order(self,symbol,lot,deviation,filling_type,position):
        # Close buy order
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "position":position,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "deviation": deviation,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC
        }
        order_res = mt5.order_send(request)

        logging.info(f'close opened buy order, REQUEST: {request}')
        logging.info(f'close opened buy order, RETURN:{order_res}')

        return order_res
        
    def close_opened_sell_order(self,symbol,lot,deviation,filling_type,position):
        # Close sell order
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "position":position,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "deviation": deviation,
            "type_filling": filling_type,
            "type_time": mt5.ORDER_TIME_GTC
        }
        order_res = mt5.order_send(request)

        logging.info(f'close opened sell order, REQUEST: {request}')
        logging.info(f'clsoe opened sell order, RETURN:{order_res}')

        return order_res
        
    def close_all_opened_buy_order(self, symbol):
        # Close all buy order by ticker
        open_orders = mt5.positions_get(symbol=str(symbol))
        logging.warning(f'close all opened buy order, OPEN_ORDERS: {open_orders}')

        for order in open_orders:
            if order.type == 0:
                self.close_opened_buy_order(
                    symbol=symbol,
                    lot=order.volume,
                    deviation=10,
                    filling_type=1,
                    position=order.ticket)
        
    def close_all_opened_sell_order(self, symbol):
        # Close all sell order by ticker
        open_orders = mt5.positions_get(symbol=str(symbol))
        logging.warning(f'close all opened sell order, OPEN_ORDERS: {open_orders}')
        for order in open_orders:
            if order.type == 1:
                self.close_opened_sell_order(
                    symbol=symbol,
                    lot=order.volume,
                    deviation=10,
                    filling_type=1,
                    position=order.ticket)
                
    def close_all_opened_order(self, symbol):
        # Close all buy order by ticker
        open_orders = mt5.positions_get(symbol=str(symbol))
        logging.warning(f'close all opened order, OPEN_ORDERS: {open_orders}')
        for order in open_orders:
            if order.type == 0:
                self.close_opened_buy_order(
                    symbol=symbol,
                    lot=order.volume,
                    deviation=10,
                    filling_type=1,
                    position=order.ticket)
            
            elif order.type == 1:
                self.close_opened_sell_order(
                    symbol=symbol,
                    lot=order.volume,
                    deviation=10,
                    filling_type=1,
                    position=order.ticket)
                
    def account_info(self):
        account_info = mt5.account_info()
        if account_info != None:
            print(account_info)
            print("Show account_info()._asdict():")
            account_info_dict = mt5.account_info()._asdict()
            for prop in account_info_dict:
                print("{}={}".format(prop, account_info_dict[prop]))
    
            # convert the dictionary into DataFrame and print
            df=pd.DataFrame(list(account_info_dict.items()),columns=['property','value'])
            print("account_info() as dataframe:")
            print(df)
        else:
            print("failed to connect")

        logging.info(f'account info: {account_info}')
        return account_info

    def place_limit_buy_order(self, symbol, lot, price, **kwargs):
        # Send a limit buy order with optional take-profit (tp)
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": float(price),
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Check if tp is provided in kwargs; if yes, add it to the request
        if 'tp' in kwargs:
            request['tp'] = float(kwargs['tp'])

        order_res = mt5.order_send(request)

        if order_res.retcode == mt5.TRADE_RETCODE_DONE:
            screen_txt = f"place pending buy order {symbol}, {lot} lot @ {price:5.5f}"
            self.screen_printing(text=screen_txt)

        logging.info(f'place limit buy order, REQUEST: {request}')
        logging.info(f'place limit buy order, RETURN:{order_res}')

        return order_res

    def place_limit_sell_order(self, symbol, lot, price, **kwargs):
        # Send a limit sell order with optional take-profit (tp)
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": float(price),
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Check if tp is provided in kwargs; if yes, add it to the request
        if 'tp' in kwargs:
            request['tp'] = float(kwargs['tp'])

        order_res = mt5.order_send(request)

        if order_res.retcode == mt5.TRADE_RETCODE_DONE:
            screen_txt = f"place pending sell order {symbol}, {lot} lot @ {price:5.5f}"
            self.screen_printing(text=screen_txt)

        logging.info(f'place limit sell order, REQUEST: {request}')
        logging.info(f'place limit sell order, RETURN:{order_res}')

        return order_res

    def get_position_by_symbol(self, symbol):
        pos_res = mt5.positions_get(symbol=str(symbol))
        logging.info(f'get position by symbol, REQUEST: {symbol}')
        logging.info(f'get position by symbol, RETURN: {pos_res}')
        return pos_res

    def get_order_by_symbol(self, symbol):
        order_res = mt5.orders_get(symbol=str(symbol))
        logging.info(f'get order by symbol, REQUEST: {symbol}')
        logging.info(f'get order by symbol, RETURN: {order_res}')
        return order_res

    def cancel_order(self, order_number):
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order_number,
        }

        order_res = mt5.order_send(request)

        if order_res.retcode == mt5.TRADE_RETCODE_DONE:
            screen_txt = f"order number {order_number} has been cancelled"
            self.screen_printing(text=screen_txt)

        logging.info(f'cancel order, REQUEST: {request}')
        logging.info(f'cancel order, RETURN: {order_res}')

        return order_res
    
    def cancel_all_pending_sell_order(self, symbol):
        order_res = mt5.orders_get(symbol=str(symbol))
        logging.warning(f'close all pending sell order, PENDING_ORDERS: {order_res}')
        for order in order_res:
            if order.type == 3:
                res = self.cancel_order(order_number=order.ticket)

    def cancel_all_pending_buy_order(self, symbol):
        order_res = mt5.orders_get(symbol=str(symbol))
        logging.warning(f'close all pending buy order, PENDING_ORDERS: {order_res}')
        for order in order_res:
            if order.type == 2:
                res = self.cancel_order(order_number=order.ticket)

    def cancel_all_pending_order(self, symbol):
        order_res = mt5.orders_get(symbol=str(symbol))
        logging.warning(f'close all pending, PENDING_ORDERS: {order_res}')
        for order in order_res:
            if order.type == 2:
                res = self.cancel_order(order_number=order.ticket)

            elif order.type == 3:
                res = self.cancel_order(order_number=order.ticket)

    def update_cache_pending_order(self, symbol):
        order_res = mt5.orders_get(symbol=symbol)
        logging.warning(f'update cache pending order')
        self.cache_order = [order.ticket for order in order_res]

        screen_txt = f"updated cache of pending order for {symbol}"
        self.screen_printing(text=screen_txt)

        return self.cache_order
    
    def update_cache_opened_order(self, symbol):
        pos_res = mt5.positions_get(symbol=symbol)
        logging.warning(f'update cache opened order')
        self.cache_opened_order = [pos.ticket for pos in pos_res]

        screen_txt = f"updated cache of opened (active) order for {symbol}"
        self.screen_printing(text=screen_txt)

        return self.cache_opened_order
    
    def check_close_order(self, ticket):
        ticket_order = mt5.history_orders_get(position=ticket)
        try:
            if len(ticket_order) >= 2 or len(ticket_order) == 0:
                bool = True
                if len(ticket_order) == 0:
                    logging.warning(f'check close order {ticket}, RETURN: cancelled pending order')
                elif len(ticket_order) >= 0:
                    logging.warning(f'check close order {ticket}, RETURN: closed order')
            else:
                bool = False
        except (TypeError, AttributeError):
            bool = False
        return bool

    def cancel_pending_out_of_list(self, df_col, symbol):
        ref_list = list(df_col)
        res_list = self.update_cache_pending_order(symbol=symbol)
        set_list = set(res_list) - set(ref_list)
        diff_list = list(set_list)

        logging.info(f'cancel pending out of list, ORDERS_LIST: {diff_list}')

        if len(diff_list) > 0:
            for lst in diff_list:
                self.cancel_order(order_number=lst)
                screen_txt = f"ticket {lst} has been cancelled"
                self.screen_printing(text=screen_txt)
            
            screen_txt = f"close opened (active) order out of list {symbol}"
            self.screen_printing(text=screen_txt)

    def close_opened_out_of_list(self, df_col, symbol):
        ref_list = list(df_col)
        order_list = self.update_cache_opened_order(symbol=symbol)
        diff_list = list(set(order_list) - set(ref_list))

        logging.info(f'close opened out of list, ORDERS_LIST: {diff_list}')

        if len(diff_list) > 0:
            for lst in diff_list:
                mt5.Close(symbol, ticket=lst)
                screen_txt = f"ticket {lst} has been closed"
                self.screen_printing(text=screen_txt)

            screen_txt = f"close opened (active) order out of list {symbol}"
            self.screen_printing(text=screen_txt)

    def get_current_price(self, symbol):
        return (mt5.symbol_info_tick(symbol).bid + mt5.symbol_info_tick(symbol).ask) / 2
    
    def screen_printing(self, text):
        curr_time = datetime.datetime.now().strftime('%A, %B %d, %Y %H:%M:%S')
        print(f"{curr_time} : {text}")

class grid():
    def __init__(self):
        ...

    def validate_legacy_columns(self, df1, df2, columns, exact_status):
        # Selecting the specific columns from each DataFrame
        selected_columns = columns 
        selected_df = df1[selected_columns]
        selected_df_legacy = df2[selected_columns]

        try:
            pd.testing.assert_frame_equal(selected_df, selected_df_legacy, check_exact=exact_status)
            is_almost_equal = True
        except AssertionError:
            print("Assertion Error")
            is_almost_equal = False
            
        return is_almost_equal

    
    
