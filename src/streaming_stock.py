# import ssi_fc_data
import plugin.key.config_data as config_data
from ssi_fc_data import fc_md_client , model
from plugin.ssi_data import data_setting
import json
from plugin.key.key import token
import datetime 
import time

client = fc_md_client.MarketDataClient(config_data)
dictionary = token.dictionary_file()
import telebot
Token = token.token_tele()
bot = telebot.TeleBot(Token)
today_weekday = datetime.datetime.today().strftime('%Y/%m/%d')
working_day = datetime.datetime.today().strftime('%A').upper()
work_wh = datetime.datetime.today()
current_date_ssi = datetime.datetime.today().strftime("%d/%m/%Y")
yesterday_date_ssi = (datetime.datetime.today() - datetime.timedelta(days=3)).strftime("%d/%m/%Y")
halfmonth_date_ssi = (datetime.datetime.today() - datetime.timedelta(days=15)).strftime("%d/%m/%Y")

def get_stock_data():
        lis_buf = []
        while(True):     
            try:
                lst_stock = data_setting.get_stock_sp()
                for stock in lst_stock:
                    dwn = 0
                    upt = 0   
                    buf = 0 
                    chat_id_user = stock['chat_id']
                    symbol = stock['stock']
                    phigh = stock['high']
                    plow = stock['low']
                    try:
                        intraday = client.intraday_ohlc(config_data, model.intraday_ohlc(symbol, yesterday_date_ssi, current_date_ssi, 1, 1000, True, 1))
                    except:
                        intraday = client.intraday_ohlc(config_data, model.intraday_ohlc(symbol, halfmonth_date_ssi, current_date_ssi, 1, 1000, True, 1))

                    value = int(intraday['data'][-1]['Value'])
                    tradingdate = intraday['data'][-1]['TradingDate']
                    tradingtime = intraday['data'][-1]['Time']
                    info_stock = {
                        "stock":symbol,
                        "price":value,
                        "trading_time": tradingtime,
                        "trading_date": tradingdate
                    }
                    if info_stock['stock'] not in str(lis_buf):
                        lis_buf.append(info_stock)
                    else:
                        for stock_buf in lis_buf:
                            try:
                                if info_stock['stock'] == stock_buf['stock'] and str(info_stock) not in str(lis_buf):
                                    try:
                                        for phi in phigh:
                                            if info_stock['price'] >= phi and (info_stock['price'] - stock_buf['price']) >= 50 and info_stock['trading_time'] != stock_buf['trading_time']:
                                                buf = info_stock['price'] - stock_buf['price']
                                                upt += 1
                                        for plw in plow:
                                            if info_stock['price'] <= plw and (info_stock['price'] - stock_buf['price']) <= -50 and info_stock['trading_time'] != stock_buf['trading_time']:
                                                buf = info_stock['price'] - stock_buf['price']
                                                dwn += 1
                                    except:
                                        pass
                                    lis_buf.remove(stock_buf)
                                    lis_buf.append(info_stock)
                            except:
                                pass
                    if  upt >= 1 :
                        content = f"<b>{'🟢'*upt} H{upt} {symbol} </b>.\
                                    \nGiá:{value} (+{buf}) tại {tradingtime} {tradingdate}."
                        # print(content)
                        # print('\n')
                        bot.send_message(chat_id_user,content, parse_mode="html")
                    elif dwn >= 1:
                        content = f"<b>{'🔴'*dwn} L{upt} {symbol} </b>.\
                                    \nGiá:{value} ({buf}) tại {tradingtime} {tradingdate}."
                        # print(content)
                        # print('\n')
                        bot.send_message(chat_id_user,content, parse_mode="html")
            except Exception as e:
                print(e)


get_stock_data()         
            


