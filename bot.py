import websocket, json, pprint, numpy, ta
from binance.client import Client 
from binance.enums import *
import config


#default variables set to this, however can change depending on trading patterns
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.05

#where the streamed data is
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

#create array to append closing prices and checks for position
closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld ='us')

def order(symbol, quantity, side, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)

    except Exception as e:
        print('an exception occured-{}'.format(e))
        return False

    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    print('received message')
    print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = ta.momentum.RSIINDICATOR(np_closes, RSI_PERIOD)
            print("rsi calculated: ")
            print(rsi)
            last_rsi = rsi[-1]
            print("the last rsi is {}" +format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("SELL IT!")
                    #put binance sell logic here
                    order_succeeded =  order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought and don't own anything")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you own it")
                else:
                    print('BUY IT!')
                    #put binance buy logic here
                    order_succeeded = order(SIDE_BUY, TRADE_SYMBOL, TRADE_QUANTITY)
                    if order_succeeded:
                        in_position = True
            
            
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

 