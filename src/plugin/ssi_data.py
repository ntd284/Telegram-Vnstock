# import ssi_fc_trading
import subprocess
import sys
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Example usage

from ssi_fc_data import fc_md_client , model
import plugin.key.config_data as config_data
from plugin.key.key import token
from datetime import datetime
import pandas as pd
from vnstock import * 
import datetime
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except:
    install_package('plotly')
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots


import plotly.io as pio
import json

import time
onemonth_before = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
threemonth_before = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y-%m-%d")
year_before = (datetime.datetime.today() - datetime.timedelta(days=360)).strftime("%Y-%m-%d")
current_date = datetime.datetime.today().strftime("%Y-%m-%d")
current_date_ssi = datetime.datetime.today().strftime("%d/%m/%Y")
yesterday_date_ssi = (datetime.datetime.today() - datetime.timedelta(days=3)).strftime("%d/%m/%Y")
client = fc_md_client.MarketDataClient(config_data)

class data_setting():
    def get_lst_trading():
        with open(f"{token.dictionary_file()}/list_acc_trading.txt","r") as file:
            list_stock = file.read().splitlines()
            lst_stock = []
            for stock in list_stock:
                try:
                    json_stock = json.loads(stock.replace("'",'"'))
                    lst_stock.append(json_stock)
                except:
                    pass
            return lst_stock


    def save_stock_sp(info_json):
        with open(f"{token.dictionary_file()}/list_stock_sp.txt","r") as file:
            stock_sp = file.read().splitlines()
            lst=[]
            if info_json['stock'] not in str(stock_sp):
                stock_sp.append(info_json)
                lst = stock_sp
            else:
                for stock in stock_sp:
                    stock = json.loads(stock.replace("'",'"'))
                    if str(stock['stock']) == str(info_json['stock']):
                        stock = info_json
                        lst.append(stock)
                    else:
                        lst.append(stock)
            with open(f"{token.dictionary_file()}/list_stock_sp.txt","w") as file:
                str_stock_sp = str(lst).replace('"',"").replace('[{','{').replace('}, {',"}\n{").replace("}]","}").replace("['[]', ","")
                file.write(str_stock_sp)
                
    def update_stock_sp(lst_info_json):
        with open(f"{token.dictionary_file()}/list_stock_sp.txt","w") as file:
            str_stock_sp = str(lst_info_json).replace('"',"").replace('[{','{').replace('}, {',"}\n{").replace("}]","}")
            file.write(str_stock_sp)

    def get_stock_sp():
        with open(f"{token.dictionary_file()}/list_stock_sp.txt","r") as file:
            list_stock = file.read().splitlines()
            lst_stock = []
            for stock in list_stock:
                stock = json.loads(stock.replace("'",'"'))
                lst_stock.append(stock)
            return lst_stock
        
    def save_list_stock():
        pd_stock = listing_companies(live=True, source='SSI')
        list_stock = pd_stock.to_dict(orient='records')
        with open(f"{token.dictionary_file()}/list_stock.txt","a") as file:
            for ticker in list_stock:
                file.write(ticker['ticker'])
                file.write("\n")

    def get_list_stock():
        with open(f"{token.dictionary_file()}/list_stock.txt","r") as file:
            lst_stock = file.read().splitlines()
            return lst_stock
    
    def get_stock_info_1d(ticker):
        lst_stock = []
        data_lastest = price_depth(ticker)

        try:
            best_ask_buy = round((int(data_lastest['Giá bán 1'][0])),2)
            best_ask_vol = int(data_lastest['KL bán 1'][0])*10
            best_bid_sell = round((int(data_lastest['Giá mua 3'][0])),2)
            best_bid_vol = int(data_lastest['KL mua 3'][0])*10
        except:
            best_ask_buy = data_lastest['Giá bán 1'][0]
            best_ask_vol = data_lastest['KL bán 1'][0]
            best_bid_sell = data_lastest['Giá mua 3'][0]
            best_bid_vol = data_lastest['KL mua 3'][0]

        json_best_price = {
            "best_ask_buy" : best_ask_buy,
            "best_ask_vol" : best_ask_vol,
            "best_bid_sell": best_bid_sell,
            "best_bid_vol" : best_bid_vol
        }

        list_stocks = (client.daily_stock_price(config_data, model.daily_stock_price (ticker, yesterday_date_ssi, current_date_ssi, 1, 100, '')))['data']
        for stock in list_stocks:
            json_stock = {
                "Date": stock['TradingDate'],
                "Open": int(stock['OpenPrice']),
                "High": int(stock['HighestPrice']),
                "Close": int(stock['ClosePrice']),
                "Low": int(stock['LowestPrice']),
                "Adj Close" :float(stock['ClosePriceAdjusted']),
                "Volume": int(stock['TotalMatchVol']),
                "PriceChange": int(stock['PriceChange']),
                "PerPriceChange": float(stock['PerPriceChange']),
                "Foreign_Buy": int(stock['ForeignBuyVolTotal']),
                "Foreign_Sell": int(stock['ForeignSellVolTotal']),
            }
            lst_stock.append(json_stock)
        json_stock = lst_stock[-1]
        yes_json_stock = lst_stock[-2]
        if json_stock['PriceChange'] >= 0 and json_stock['PerPriceChange']>=0:
            status = f"{json_stock['Close']} 💹({json_stock['PriceChange']})"
        else:
            status = f"{json_stock['Close']} 🛑({json_stock['PriceChange']})"
        req = client.securities_details(config_data, model.securities_details(symbol ={ticker}))
        name_stock = req['data'][0]['RepeatedInfo'][0]['SymbolName']
        content = f"{json_stock['Date']}:🎟 CP <b> {ticker} </b>({name_stock}) \n\n💰 <b>Giá đóng cửa:</b> {yes_json_stock['Close']} ({yes_json_stock['Date']})\n<b>💰 Giá hiện tại:</b> {status}\n<b>🌕 Giá mở cửa:</b> {json_stock['Open']}\
                \n<b>⚖️ Giá cao nhất:</b>  {json_stock['High']}\
                \n<b>⚖️ Giá thấp nhất:</b> {json_stock['Low']}\
                \n<b>📊 khối lượng giao dịch:</b> {json_stock['Volume']/1000:,.3f} \
                \n<b>📥 khối lượng NN mua:</b> {json_stock['Foreign_Buy']/1000:,.3f} \
                \n<b>📤 khối lượng NN bán:</b> {json_stock['Foreign_Sell']/1000:,.3f}"
        return json_stock,content,json_best_price,yes_json_stock
    
    
    def get_stock_price_6m(ticker):
        lst_stock  = []
        df_lst_stock = stock_historical_data(symbol=ticker, start_date=threemonth_before, end_date=current_date, resolution="1D", type="stock", beautify=True, decor=False, source='DNSE')
        list_stocks = df_lst_stock.to_dict(orient='records')
        for stock in list_stocks:
            json_stock = {
                "Date": stock['time'],
                "Open": int(stock['open']),
                "High": int(stock['high']),
                "Close": int(stock['close']),
                "Low": int(stock['low']),
                "Volume": int(stock['volume']),
            }
            lst_stock.append(json_stock)
        df_stock = pd.DataFrame(lst_stock)
        df_stock['sma_20'] = df_stock['Close'].rolling(window=20).mean()
        df_stock['sma_5'] = df_stock['Close'].rolling(window=5).mean()
        min_date = (df_stock['Date'].min()).strftime('%d/%m/%Y')
        max_date = (df_stock['Date'].max()).strftime('%d/%m/%Y')

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.1, subplot_titles=(f"{ticker}({min_date}-{max_date})", 'Volume'), 
               row_width=[0.2, 0.4])
        
        fig.add_trace(go.Candlestick(x=df_stock["Date"], open=df_stock["Open"], high=df_stock["High"],
                low=df_stock["Low"], close=df_stock["Close"], name = "Price(Vnđ)"), 
                row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_stock["Date"], y=df_stock['sma_20'],name = "sma_20"), row=1, col=1)
        
        df_stock['diff_Open_Close'] = df_stock['Close'] - df_stock['Open']
        df_stock['BarColor'] = df_stock['diff_Open_Close'].apply(lambda x: 'green' if x >= 0 else 'red')
        fig.add_trace(go.Bar(x=df_stock['Date'], y=df_stock['Volume'],  marker=dict(color=df_stock['BarColor']),showlegend=True, name = "Volume"), row=2, col=1)
        fig.update(layout_xaxis_rangeslider_visible=False)
        buffer = pio.to_image(fig,format="png",scale=1, width=1000, height=800)
        if lst_stock[-1]['Close'] >= lst_stock[0]['Close']:
            status = f"📈 Tăng: {round(((lst_stock[-1]['Close']-lst_stock[0]['Close'])*100/lst_stock[0]['Close']),2)}%"
        else:
            status = f"📉 Giảm: {round(((lst_stock[0]['Close']-lst_stock[-1]['Close'])*100/lst_stock[0]['Close']),2)}%"

        caption = f"Biểu đồ 6 tháng của cổ phiếu {ticker}: \n{status}"
        return lst_stock,buffer,caption
    