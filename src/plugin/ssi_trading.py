import requests
import json
from plugin.key.key import token
from plugin.ssi_data import data_setting

class trading_setting:
    # HOST = "http://127.0.0.1:8000"
    @staticmethod
    def getOTP(host,account):
        url = f"{host}/getOtp"
        lst_acc = data_setting.get_lst_trading()
        headers = {'accepts': "application/json"}
        response = requests.request("GET", url, headers=headers, data={}).json()
        if int(response['status']) == 200:
            for acc in lst_acc:
                if acc['id'] == account:
                    return f"Xác nhận thành công, đợi chút, kiểm tra và nhập mã OTP từ tin nhắn số điện thoại của {acc['name']}"
        else:
            return "Xác nhận lỗi"

    @staticmethod
    def verifyOtp(host,code):
        url = f"{host}/verifyCode?code={code}"
        headers = {'accept': 'application/json'}
        response = requests.request("GET", url, headers=headers, data={}).json()
        if response:
            return "Xác nhận thành công"

    @staticmethod
    def stockAccountBalance(host,account):
        url = f"{host}/stockAccountBalance?account={account}"
        headers = {'accepts': "application/json"}
        response = requests.request("GET", url, headers=headers, data={}).json()
        return f'Account Balance: {response}'

    @staticmethod
    def orderHistory(host,account,startDate, endDate):
        headers = {'accept': 'application/json'}
        url = f"{host}/orderHistory"
        payload = {
            "account": account,
            "startDate": startDate,
            "endDate": endDate
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}, {response.text}"

    @staticmethod
    def newOrder(host,account,Ticker, buySell, price, quantity):
        orderType = "LO"
        market = "VN"
        stopOrder = False
        stopPrice = 0
        stopType = ''
        stopStep = 0
        lossStep = 0
        profitStep = 0
        deviceId = token.deviceID()
        userAgent = ''

        url = f"{host}/newOrder"
        headers = {'accept': 'application/json'}
        payload = {
            'instrumentID': Ticker,
            'market': market,
            'buySell': buySell,
            'orderType': orderType,
            'price': price,
            'quantity': quantity,
            'account': account,
            'stopOrder': stopOrder,
            'stopPrice': stopPrice,
            'stopType': stopType,
            'stopStep': stopStep,
            'lossStep': lossStep,
            'profitStep': profitStep,
            'deviceId': deviceId,
            'userAgent': userAgent
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}, {response.text}"

    @staticmethod
    def maxBuyQty(host,account,ticker,price):
        url = f"{host}/maxBuyQty"
        headers = {'accept': 'application/json'}
        payload = {
            'account': account,
            'instrumentID': ticker,
            'price': price
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code == 200:
            return (response.json())['data']['maxBuyQty']
        else:
            return f"Error: {response.status_code}, {response.text}"

    @staticmethod
    def maxSellQty(host,account,ticker):
        url = f"{host}/maxSellQty"
        headers = {'accept': 'application/json'}
        payload = {
            'account': account,
            'instrumentID': ticker,
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code == 200:
            return (response.json())['data']['maxSellQty']
        else:
            return f"Error: {response.status_code}, {response.text}"

    @staticmethod
    def auditOrderBook(host,account,order_id):
        url = f"{host}/auditOrderBook"
        headers = {'accept': 'application/json'}
        payload = {
            'account': account,
        }
        response = requests.request("GET", url, headers=headers, params=payload)

        if response.status_code == 200:
            resp = response.json()
            orders = resp['data']['orders']
            for ord in orders:
                request_id = ord['uniqueID']
                if str(request_id) == str(order_id):
                    status = {
                        "status": ord['orderStatus'],
                        "reason": ord['rejectReason']
                    }
                    return status
        else:
            return f"Error: {response.status_code}, {response.text}"

    @staticmethod
    def stockPosition(host,account,symbol):
        url = f"{host}/stockPosition"
        headers = {'accept': 'application/json'}
        payload = {
            'account': account,
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        if response.status_code == 200:
            resp = response.json()

            orders = resp['data']['stockPositions']
            for ord in orders:
                instrumentID = ord['instrumentID'].upper()
                if instrumentID == symbol:
                    onHand = {
                        "onHand": int(ord['onHand']),
                        "avgPrice": int(ord['avgPrice'])
                    }
                    return onHand
        else:
            return f"Error: {response.status_code}, {response.text}"

          
# print(trading_setting.getOTP())
# print(trading_setting.verifyOtp('140382'))