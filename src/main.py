# from plugin.open_ai import openai_setting
from plugin.ssi_data import data_setting
from plugin.ssi_trading import trading_setting
import telebot
from telebot import types
from plugin.key.key import token
import json
import pandas as pd
import time
import io
import dataframe_image as dfi
Token = token.token_tele()
bot = telebot.TeleBot(Token)

class telegram():
    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/GETOTP"))
    def getotp(message):
        chat_id_user = message.chat.id
        lst_acc = data_setting.get_lst_trading()
        markup = types.ReplyKeyboardMarkup(row_width = 3)
        lst = []
        for acc in lst_acc:
            lst.append(types.KeyboardButton(f"/OTP {acc['name']} {acc['id']}"))
        
        markup.add(*lst)
        content = "<b>Danh sách tài khoản</b>"
        bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
    
    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/OTP"))
    def otp(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        lst_acc = data_setting.get_lst_trading()
        name = lst[1]
        id = lst[2]
        markup = types.ForceReply(selective=True)
        if id in str(lst_acc):
            for acc in lst_acc:
                if id == acc['id'] and name == acc['name']:
                    content = f"/OTP {acc['name']} {acc['id']}"
                    response = trading_setting.getOTP(acc['host'],acc['id']) 
                    bot.send_message(chat_id_user,response)
                    bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')
    
    @bot.message_handler(func=lambda message: message.text.upper().startswith("/OTP") or message.reply_to_message is not None and message.reply_to_message.text is not None and message.reply_to_message.text.upper().startswith("/OTP"))
    def verify(message):
        chat_id_user = message.chat.id
        lst_acc = data_setting.get_lst_trading()
        reply_mess = message.reply_to_message.text.upper().split()
        name = reply_mess[1]
        id = reply_mess[2]
        try:
            code_otp = int((message.text.upper().split())[0])
            if str(id) in str(lst_acc):
                for acc in lst_acc:
                    if id == acc['id']:
                        response = trading_setting.verifyOtp(acc['host'],code_otp)
                        bot.send_message(chat_id_user, response, parse_mode='html')                      
            else:
                bot.send_message(chat_id_user, "id không thuộc danh sách", parse_mode='html')  
                    
        except:
            content = "Sai Mã code. Vd: 123456 "
            bot.send_message(chat_id_user, content,parse_mode='html')
            markup = types.ForceReply(selective=True)
            content = f"/OTP {name} {id}"
            bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html') 

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/IF"))
    def info(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        chatid = token.chat_admin_id()
        lst_stock = data_setting.get_list_stock()
        stock_info = data_setting.get_stock_sp()

        if len(lst) == 1:
            bot.send_message(chat_id_user, f"<b>Ví dụ về lấy thông tin mã cổ phiếu :</b> \n/if SSI\n/if ACB",parse_mode='html')
        else:
            if lst[1] in lst_stock:
                ticker = lst[1]
                lst_stock,buffer,caption = data_setting.get_stock_price_6m(ticker)
                json_stock,content,json_best_price,yes_json_stock = data_setting.get_stock_info_1d(ticker)
                bot.send_message(chat_id_user,content, parse_mode='html')
                bot.send_photo(chat_id_user,buffer,caption)
            else:
                bot.send_message(chat_id_user, f"{lst[1]} Không có trong danh sách ")

        stock_al = []
        markup = types.ReplyKeyboardMarkup(row_width = 5)
        for stock in stock_info:
            stock_al.append(types.KeyboardButton(f"/IF {stock['stock']}"))

        markup.add(*stock_al)
        content = "<b>Danh sách CP đã có chọn ngưỡng</b>"
        bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
           

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/START") )
    def start(message):
        chat_id_user = message.chat.id
        commands=[
            telebot.types.BotCommand('/getotp', 'gửi mã otp để xác nhận tk'),
            telebot.types.BotCommand('/vf', 'xác nhận mã otp'),
            telebot.types.BotCommand('/if', 'Xem thông tin CP [ vd. /if ssi ]'),
            telebot.types.BotCommand('/lal', 'Xem CP trong danh sách ALERT [ vd. /lal ]'),
            telebot.types.BotCommand('/al', 'Tạo mức giá Alert [ vd. /al ssi ]'),
            # telebot.types.BotCommand('/tr', 'Giao dịch [ vd. /tr ssi ]'),
            ]
        try:
            bot.set_my_commands(commands,scope=telebot.types.BotCommandScopeChat(chat_id_user))
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error updating commands: {e}")

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/LAL"))
    def lstalert(message):
        chat_id_user = int(message.chat.id) # type: ignore
        stock_info = data_setting.get_stock_sp()
        if stock_info == [[]]:
            message = "EMPTY"
            markup = types.ReplyKeyboardRemove(selective=False)
            bot.send_message(chat_id_user, message, reply_markup=markup)
            return False
        else:
            pass
        df = pd.DataFrame(stock_info)
        df.pop('chat_id')
        buffer = io.BytesIO()
        dfi.export(df, buffer, table_conversion="matplotlib")
        image = buffer.getvalue()
        bot.send_photo(chat_id_user,image)  
        markup = types.ReplyKeyboardMarkup(row_width = 2)  
        stock_al = []
        stock_lvedl = []
        stock_cpdel = []
        lst_cont = []

        for stock in stock_info:
            stock_al.append(types.KeyboardButton(f"/AL⚖ {stock['stock']}"))
            stock_lvedl.append(types.KeyboardButton(f"/LVDEL🚦 {stock['stock']}"))
            stock_cpdel.append(types.KeyboardButton(f"/CPDEL❌ {stock['stock']}"))

        markup.add(*stock_al)
        markup.add(*stock_lvedl)
        markup.add(*stock_cpdel)

        bot.send_message(chat_id_user, "<b>/AL⚖:</b> Thêm ngưỡng HIGH/LOW/SET.\
                                        \n<b>/LVDEL🚦:</b> Xóa ngưỡng HIGH/LOW.\
                                        \n<b>/CPDEL❌:</b> Xóa cổ phiếu",reply_markup=markup,parse_mode='html')
    
    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/LVDEL"))
    def lvdel(message):
        chat_id_user = int(message.chat.id) # type: ignore
        lst = message.text.upper().split()
        stock_info = data_setting.get_stock_sp()
        ticker = lst[1]
        stock_lst = []
        cnt = 0
        markup = types.ReplyKeyboardMarkup(row_width=5)  
        lst_stock = data_setting.get_list_stock()

        if ticker in lst_stock:
            for stock in stock_info:
                if stock['stock'] == ticker:
                    if stock['high'] != [] or stock['low'] != []:
                        for hig in stock['high']:
                            itemh = types.KeyboardButton(f"/DEL HIGH {ticker} {hig} 🟢❌")
                            markup.add(itemh)
                        for lw in stock['low']:
                            iteml = types.KeyboardButton(f"/DEL LOW {ticker} {lw} 🔴❌")
                            markup.add(iteml) 
                        cnt+=1                    
                else:
                    stock_lst.append(types.KeyboardButton(f"/LVDEL {stock['stock']}"))
            markup.add(*stock_lst)

            if cnt == 1:
                content = f"Danh sách của mã <b>{ticker}</b>:"
            else:
                content = f"Danh sách <b>{ticker}: EMPTY</b>:"

            bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
        else:
            content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /LVDEL Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/DEL"))
    def dellv(message):
        chat_id_user = int(message.chat.id) # type: ignore
        lst = message.text.upper().split()
        stock_info = data_setting.get_stock_sp()
        lst_stock = data_setting.get_list_stock()
        type = lst[1].lower()
        ticker = lst[2]
        if ticker in lst_stock:
            price = int(lst[3])
            for stock in stock_info:
                if stock['stock'] == ticker:
                    if price in stock[f'{type}']:
                        stock[f'{type}'].remove(price)
                        data_setting.save_stock_sp(stock)
            markup = types.ReplyKeyboardMarkup(row_width=5)  
            stock_lst = []
            for stock in stock_info:
                if stock['stock'] == ticker:
                    for hig in stock['high']:
                        itemh = types.KeyboardButton(f"/DEL HIGH {ticker} {hig} 🟢❌")
                        markup.add(itemh)
                    for lw in stock['low']:
                        iteml = types.KeyboardButton(f"/DEL LOW {ticker} {lw} 🔴❌")
                        markup.add(iteml)
                else:
                    stock_lst.append(types.KeyboardButton(f"/LVDEL {stock['stock']}"))
                    
            markup.add(*stock_lst)

            df = pd.DataFrame(stock_info)
            df.pop('chat_id')
            buffer = io.BytesIO()
            dfi.export(df, buffer, table_conversion="matplotlib")
            image = buffer.getvalue()
            bot.send_photo(chat_id_user,image,parse_mode='html')  
            content = "Chọn để xóa: "
            bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
        else:            
            content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /DEL Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  


    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/AL"))
    def alert(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        lst_stock = data_setting.get_list_stock()
        lst_stock_al = data_setting.get_stock_sp()  
        stock_lst = []
        if len(lst) > 2:
            content = f"{lst[1:]} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /SET Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  
            return False
        elif len(lst) == 1:
            bot.send_message(chat_id_user, f"<b>Ví dụ về đặt alert với mã cổ phiếu:</b> \n/al SSI\n/al ACB",parse_mode='html')
        else:
            if lst[1] in lst_stock:
                ticker = lst[1]
                json_stock,content,json_best_price,yes_json_stock = data_setting.get_stock_info_1d(ticker)
                markup = types.ReplyKeyboardMarkup(row_width = 5)
                setnew= types.KeyboardButton(f"/SET {ticker}")
                setH= types.KeyboardButton(f"/HIGH🟢 {ticker}")
                setL= types.KeyboardButton(f"/LOW🔴 {ticker}")
                try:
                    stock_onhand_D = trading_setting.stockPosition(token.hostD(),token.accountD(),ticker)
                    onhand_D = stock_onhand_D['onHand']
                    aver_price_D = stock_onhand_D['avgPrice']
                except:
                    onhand_D = 0
                    aver_price_D = 0


                content = f"<b>CP: {ticker}</b>. {json_stock['Date']}\
                        \n<b>Số lượng CP onHand Duong:</b> {onhand_D} ({aver_price_D})\
                        \n\n💰 <b>Giá đóng cửa:</b> {yes_json_stock['Close']} ({yes_json_stock['Date']})\
                        \n💰 <b>Giá CP hiện tại/closed:</b> {json_stock['Close']}\
                        \n💰 <b>Giá BUY</b> hiện tại: {json_best_price['best_ask_buy']}\
                        \n💰 <b>Giá SELL</b> hiện tại: {json_best_price['best_bid_sell']}"

                    
                if ticker not in str(lst_stock_al):
                    markup.row(setnew)
                else:
                    for stock_al in lst_stock_al:
                        if stock_al['stock'] == ticker:
                            content+=f"\n➡️ <b>Giá SET: </b>{stock_al['price']}"
                            markup.row(setH,setL,setnew)
                        else:
                            stock_lst.append(types.KeyboardButton(f"/AL⚖ {stock_al['stock']}"))

                    markup.add(*stock_lst)                 
                bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
            else:
                bot.send_message(chat_id_user, f"{lst[1]} Không có trong danh sách ")

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/CPDEL"))
    def cpdel(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        lst_stock = data_setting.get_list_stock()
        lst_stock_al = data_setting.get_stock_sp() 
        sdel_lst = []
        lst_cont = []
        ticker = lst[1]

        if lst_stock_al == [[]]:
            message = "EMPTY"
            markup = types.ReplyKeyboardRemove(selective=False)
            bot.send_message(chat_id_user, message, reply_markup=markup)
            return False
        else:
            pass
        markup = types.ReplyKeyboardMarkup()  

        if len(lst) > 2:
            content = f"{lst[1:]} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /SET Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  
            return False
        else:
            pass

        if ticker in lst_stock:
            for stock in lst_stock_al:
                if stock['stock'] != ticker:
                    lst_cont.append(stock)
                    sdel_lst.append(types.KeyboardButton(f"/CPDEL {stock['stock']}"))
            data_setting.update_stock_sp(lst_cont)
            markup.add(*sdel_lst)
            bot.send_message(chat_id_user, "<b>LVDEL:</b> Xóa ngưỡng HIGH/LOW/SET.\
                                            \n<b>CPDEL:</b> Xóa cổ phiếu",reply_markup=markup,parse_mode='html')
            
            lst_stock_al = data_setting.get_stock_sp()    
            df = pd.DataFrame(lst_stock_al)
            df.pop('chat_id')
            buffer = io.BytesIO()
            dfi.export(df, buffer, table_conversion="matplotlib")
            image = buffer.getvalue()
            bot.send_photo(chat_id_user,image)  
        else:            
            content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /CPDEL Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  

    @bot.message_handler(func=lambda message: message.text.upper().startswith("/SET") or message.reply_to_message is not None and message.reply_to_message.text is not None and message.reply_to_message.text.upper().startswith("/SET"))
    def alert(message):
        chat_id_user = message.chat.id
        mess = message.text.upper().split() 
        lst_stock = data_setting.get_list_stock()
        lst_stock_al = data_setting.get_stock_sp() 
        if len(mess) > 2:
            content = f"{mess[1:]} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /SET Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  
            return False
        else:
            pass

        try:
            ticker = mess[1]
        except:
            mess_reply = message.reply_to_message.text.upper().split()
            ticker = mess_reply[1]

        markup = types.ReplyKeyboardMarkup()
        if ticker in lst_stock:
            if ticker not in str(lst_stock_al):
                info_json = {
                    "chat_id":chat_id_user,
                    "stock":ticker,
                    "price":0,
                    "high":[],
                    "low":[]
                }
                try:
                    if message.reply_to_message.text.upper().startswith("/SET"):
                        info_json['price'] = int(mess[0])
                        data_setting.save_stock_sp(info_json)
                        setnew= types.KeyboardButton(f"/SET {ticker}")
                        setH= types.KeyboardButton(f"/HIGH🟢 {ticker}")
                        setL= types.KeyboardButton(f"/LOW🔴 {ticker}")
                        markup.row(setH,setL,setnew)
                        content = f"Đã set giá tham chiếu: {info_json['price']}\
                                    Chọn HIGH/LOW/SET\n"
                        bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  

                        lst_stock_al = data_setting.get_stock_sp()    
                        df = pd.DataFrame(lst_stock_al)
                        df.pop('chat_id')
                        buffer = io.BytesIO()
                        dfi.export(df, buffer, table_conversion="matplotlib")
                        image = buffer.getvalue()
                        bot.send_photo(chat_id_user,image)  

                except:
                    bot.send_message(chat_id_user, "Chọn mức giá tham chiếu. Vd: 40000", reply_markup=markup,parse_mode='html')  
                    markup = types.ForceReply(selective=True)
                    content = f"/SET {ticker}"
                    bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  
            else:
                for stock_al in lst_stock_al:
                    if stock_al['stock'] == ticker:
                        try:
                            stock_al['price'] = int(mess[0])
                            data_setting.save_stock_sp(stock_al)
                            setnew= types.KeyboardButton(f"/SET {ticker}")
                            setH= types.KeyboardButton(f"/HIGH🟢 {ticker}")
                            setL= types.KeyboardButton(f"/LOW🔴 {ticker}")
                            markup.row(setH,setL,setnew)
                            content = f"Đã set giá tham chiếu: {stock_al['price']}\
                                        Chọn HIGH/LOW/SET\n"
                            bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')  

                            lst_stock_al = data_setting.get_stock_sp()    
                            df = pd.DataFrame(lst_stock_al)
                            df.pop('chat_id')
                            buffer = io.BytesIO()
                            dfi.export(df, buffer, table_conversion="matplotlib")
                            image = buffer.getvalue()
                            bot.send_photo(chat_id_user,image) 
                        except:
                            bot.send_message(chat_id_user, "Chọn mức giá tham chiếu. Vd: 40000", reply_markup=markup,parse_mode='html')  
                            markup = types.ForceReply(selective=True)
                            content = f"/SET {ticker}"
                            bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')
        else:
            content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /SET Stock"
            bot.send_message(chat_id_user, content,parse_mode='html')  


    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/HIGH") or message.reply_to_message is not None and message.reply_to_message.text is not None and message.reply_to_message.text.upper().startswith("/HIGH"))
    def balance(message):

        chat_id_user = message.chat.id
        mess = message.text.upper().split()
        lst_stock_al = data_setting.get_stock_sp()  
        lst_stock = data_setting.get_list_stock()
        
        try:
            mess_reply = message.reply_to_message.text.upper().split()
            type_stock = mess_reply[0]          
            ticker = mess_reply[1]
            if ticker in lst_stock:
                for stock_al in lst_stock_al:
                    for stock_H in mess:
                        try:
                            if ticker == str(stock_al['stock']):
                                if str(stock_H) not in str(stock_al['high']):
                                    stock_al['high'].append(stock_H)
                                    bot.send_message(chat_id_user, f"Đã thêm {stock_H} vào danh sách HIGH",parse_mode='html')  

                                else:
                                    content = f"{stock_H} . <b>Đã bị trùng, đặt lại ({stock_al['price']}) rùi</b>"
                                    bot.send_message(chat_id_user, content,parse_mode='html')  
                        except:
                            pass
                    try:
                        lst_hi = [int(high) for high in stock_al['high'] if high != []]
                        lst_hi.sort()
                    except:
                        lst_hi = []
                    stock_al['high'] = lst_hi
                    data_setting.save_stock_sp(stock_al)

                markup = types.ReplyKeyboardMarkup(row_width=1)    
                setnew= types.KeyboardButton(f"/SET {ticker}")
                setH= types.KeyboardButton(f"/HIGH🟢 {ticker}")
                setL= types.KeyboardButton(f"/LOW🔴 {ticker}")
                markup.row(setnew,setH,setL)
                content = f"Chọn HIGH/LOW/SET\n"
                bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html') 

                lst_stock_al = data_setting.get_stock_sp()  
                df = pd.DataFrame(lst_stock_al)
                df.pop('chat_id')
                buffer = io.BytesIO()
                dfi.export(df, buffer, table_conversion="matplotlib")
                image = buffer.getvalue()
                bot.send_photo(chat_id_user,image) 
            else:
                content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /HIGH Stock"
                bot.send_message(chat_id_user, content, parse_mode='html')  

        except:
            type_stock = mess[0]
            ticker = mess[1]   
            if ticker in lst_stock:
                bot.send_message(chat_id_user, "Chọn ngưỡng trên 'reply /HIGH {stock}'.\nVd: 30000 40000 50000",parse_mode='html')  
                markup = types.ForceReply(selective=True)
                content = f"{type_stock} {ticker}"
                bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')
            else:
                content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /HIGH Stock"
                bot.send_message(chat_id_user, content, parse_mode='html')  


        
    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/LOW") or message.reply_to_message is not None and message.reply_to_message.text is not None and message.reply_to_message.text.upper().startswith("/LOW"))
    def balance(message):
        chat_id_user = message.chat.id
        mess = message.text.upper().split()
        lst_stock_al = data_setting.get_stock_sp()
        lst_stock = data_setting.get_list_stock()

        try:
            mess_reply = message.reply_to_message.text.upper().split()
            ticker = mess_reply[1]
            type_stock = mess_reply[0]      
            if  ticker in lst_stock:
                for stock_al in lst_stock_al:
                    for stock_L in mess:
                        try:
                            if ticker == str(stock_al['stock']):
                                if str(stock_L) not in str(stock_al['low']):
                                    stock_al['low'].append(stock_L)
                                    bot.send_message(chat_id_user, f"Đã thêm {stock_L} vào danh sách LOW",parse_mode='html')  
                                
                                else:
                                    content = f"{stock_L} . <b>Đặt lại mức thấp, đang lớn hơn mức tham chiếu ({stock_al['price']}) rùi</b>"
                                    bot.send_message(chat_id_user, content,parse_mode='html')  
                        except:
                            pass
                    try:
                        lst_hi = [int(low) for low in stock_al['low'] if low != []]
                        lst_hi.sort()
                    except:
                        lst_hi = []
                    stock_al['low'] = lst_hi
                    data_setting.save_stock_sp(stock_al)
                markup = types.ReplyKeyboardMarkup(row_width=1)    
                setnew= types.KeyboardButton(f"/SET {ticker}")
                setH= types.KeyboardButton(f"/HIGH🟢 {ticker}")
                setL= types.KeyboardButton(f"/LOW🔴 {ticker}")
                markup.row(setnew,setH,setL)
                content = f"Chọn HIGH/LOW/SET\n"
                bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html') 

                lst_stock_al = data_setting.get_stock_sp()  
                df = pd.DataFrame(lst_stock_al)
                df.pop('chat_id')
                buffer = io.BytesIO()
                dfi.export(df, buffer, table_conversion="matplotlib")
                image = buffer.getvalue()
                bot.send_photo(chat_id_user,image) 
            else:
                content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /LOW Stock"
                bot.send_message(chat_id_user, content, parse_mode='html')  

        except:
            type_stock = mess[0]
            ticker = mess[1]   
            if ticker in lst_stock:
                bot.send_message(chat_id_user, "Chọn ngưỡng trên 'reply /LOW {stock}'.\nVd: 30000 40000 50000",parse_mode='html')  
                markup = types.ForceReply(selective=True)
                content = f"{type_stock} {ticker}"
                bot.send_message(chat_id_user, content, reply_markup=markup,parse_mode='html')
            else:
                content = f"{ticker} không thuộc danh sách CP, hoặc Sai cú pháp.\nVd: /LOW Stock"
                bot.send_message(chat_id_user, content, parse_mode='html')  

    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/TR"))
    def show_lst_tr(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        lst_acc = data_setting.get_lst_trading()
        lst_stock = data_setting.get_list_stock()
        lst_item = []
        if len(lst) == 1:
            bot.send_message(chat_id_user, f"<b>Ví dụ về giao dịch với mã cổ phiếu:</b> \n/tr SSI/tr ACB",parse_mode='html')
        else:
            ticker = lst[1]

            if ticker in lst_stock:
                for acc in lst_acc:
                    item = types.KeyboardButton(f"/BS {acc['name']} {ticker}")
                    lst_item.append(item)
                markup = types.ReplyKeyboardMarkup()
                markup.add(*lst_item)
                json_stock,content,json_best_price,yes_json_stock = data_setting.get_stock_info_1d(ticker)
                bot.send_message(chat_id_user, f"   \n💰 <b>Giá BUY</b> hiện tại: {json_best_price['best_ask_buy']}\n📊 <b>KL BUY:</b> {json_best_price['best_ask_vol']}\
                                                    \n💰 <b>Giá SELL</b> hiện tại: {json_best_price['best_bid_sell']}\n📊 <b>KL SELL:</b> {json_best_price['best_bid_vol']} ",parse_mode='html')
                bot.send_message(chat_id_user, "Hãy chọn Mã CK:", reply_markup=markup)
    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/BS"))
    def buysell(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        name = lst[1]
        ticker = lst[2]
        lst_acc = data_setting.get_lst_trading()
        json_stock,content,json_best_price,yes_json_stock = data_setting.get_stock_info_1d(ticker)
        markup = types.ReplyKeyboardMarkup()

        if name in str(lst_acc):
            for acc in lst_acc:
                if name == acc['name']:
                    item_sell = types.KeyboardButton(f"/SELL({trading_setting.maxSellQty(acc['host'],acc['id'],ticker)}) {acc['id']} {ticker}")
                    item_buy = types.KeyboardButton(f"/BUY({trading_setting.maxBuyQty(acc['host'],acc['id'],ticker,json_best_price['best_ask_buy'])}) {acc['id']} {ticker}")
                    markup.add(item_sell,item_buy)
                    bot.send_message(chat_id_user, "Hãy chọn cách thức:", reply_markup=markup)
        else:
            bot.send_message(chat_id_user, f"{lst[1]} Không có trong danh sách ")


    @bot.message_handler(func=lambda message: True == message.text.upper().startswith("/SELL") or message.text.upper().startswith("/BUY"))
    def Sell(message):
        chat_id_user = message.chat.id
        lst = message.text.upper().split()
        lst_acc = data_setting.get_lst_trading()
        type_tr = (lst[0].split("("))[0]
        id = lst[1]
        ticker = lst[2]        
        lst_stock = data_setting.get_list_stock()
        if ticker in str(lst_stock):
            if id in str(lst_acc):
                json_stock,content,json_best_price,yes_json_stock = data_setting.get_stock_info_1d(ticker)
                markup = types.ForceReply(selective=True)
                str_user = f"{type_tr} {id} {ticker} {json_best_price['best_bid_sell']}"
                bot.send_message(chat_id_user, f"<b> Cú pháp nhập số lượng. Ví dụ:</b> \n1000\n1",parse_mode='html')
                bot.send_message(chat_id_user, str_user, reply_markup=markup)
        else:
            bot.send_message(chat_id_user, f"{lst[1]} Không có trong danh sách ")

    @bot.message_handler(func=lambda message: message.reply_to_message is not None and message.reply_to_message.text is not None and ( message.reply_to_message.text.upper().startswith("/SELL") or message.reply_to_message.text.upper().startswith("/BUY")))
    def Buy(message):
        chat_id_user = message.chat.id
        lst_reply_mess = message.reply_to_message.text.upper().split()
        lst_stock = data_setting.get_list_stock()
        lst_acc = data_setting.get_lst_trading()
        lst_mess = message.text.upper()
        status_codes = ["WA", "RS", "SD", "QU", "FF", "PF", "FFPC", "WM", "WC", "CL", "RJ", "EX", "SOR", "SOS", "IAV", "SOI"]
        status_codes_vn = [
            "Chờ duyệt", "Chờ gửi lên sàn", "Đang gửi lên sàn", "Chờ khớp tại sàn", "Khớp toàn phần", "Khớp một phần",
            "Khớp 1 phần hủy phần còn lại", "Chờ sửa", "Chờ hủy", "Đã hủy", "Từ chối", "Hết hiệu lực", "Chờ kích hoạt",
            "Đã kích hoạt", "Lệnh trước phiên", "Lệnh ĐK trước phiên"
        ]
        status_mapping = dict(zip(status_codes, status_codes_vn))

        try:
            quantity = int(lst_mess)
            types_tr = lst_reply_mess[0]
            id = lst_reply_mess[1]
            ticker = lst_reply_mess[2]
            price = int(lst_reply_mess[3])
            markup = types.ForceReply(selective=True)
            if ticker in str(lst_stock):
                if id in str(lst_acc):
                    str_user = f"{types_tr} {id} {ticker} {price} {quantity}"
                    content = f"Xác nhận lệnh {types_tr}:\nID: <b>{id}</b>\n⌨ Nhập Y/N (yes/no)?\n\n🎟CP: {ticker}\n💰 Giá: {price}\n📊 Số lượng:{quantity}."
                    bot.send_message(chat_id_user, content,parse_mode = 'html')
                    bot.send_message(chat_id_user, str_user, reply_markup=markup)
            else:
                bot.send_message(chat_id_user, f"{lst_reply_mess[1]} Không có trong danh sách ")
        except:
            types_tr = lst_reply_mess[0]
            id = lst_reply_mess[1]
            ticker = lst_reply_mess[2]
            price = int(lst_reply_mess[3])
            quantity = int(lst_reply_mess[4])
            if lst_mess[0] == "Y" or lst_mess[0] == "YES" :
                if id in str(lst_acc):
                    for acc in lst_acc:
                        if int(id) == int(acc['id']): 
                            if "SELL" in types_tr:
                                response = trading_setting.newOrder(acc['host'],acc['id'],ticker,"S",price,quantity)
                            elif "BUY" in types_tr:
                                response = trading_setting.newOrder(acc['host'],acc['id'],ticker,"B",price,quantity)
                try:
                    if response['status'] == 200:
                        orderId = response['data']['requestID']
                        if id in str(lst_acc):
                            for acc in lst_acc:
                                if int(id) == int(acc['id']):
                                    time.sleep(2)
                                    status = trading_setting.auditOrderBook(acc['host'],acc['id'],orderId)
                                    state = status['status']
                                    reason = status['reason']
                                    if state in status_codes:
                                        for code,description in status_mapping.items():
                                            if state == code:
                                                if state == "FF":
                                                    content = f"<b>✅ Thực hiện lệnh {types_tr} thành công</b>\
                                                        \n\n🎟 CP: {ticker}\
                                                        \n💰 Giá: {price}\
                                                        \n📊 Số lượng: {quantity}\
                                                        \n\n<b>Trạng thái: {description} - {reason}</b>"
                                                
                                                else:
                                                    content = f"<b>🔴 {types_tr} chưa thành công</b>\
                                                        \n\n🎟 CP: {ticker}\
                                                        \n💰 Giá: {price}\
                                                        \n📊 Số lượng: {quantity}\
                                                        \n\n<b>Trạng thái: {description} - {reason}</b>"
                                                bot.send_message(chat_id_user, content, parse_mode = 'html')   
                except:
                    bot.send_message(chat_id_user, f"🔴 {types_tr} chưa thành công")
            else:
                bot.send_message(chat_id_user, f"🔴 {types_tr} chưa thành công")

bot.infinity_polling()

