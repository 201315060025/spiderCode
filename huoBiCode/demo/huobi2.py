from websocket import create_connection
import gzip
import time


#链接redis数据库服务器
# r = redis.Redis(host="159.138.22.220",port=6379,password="Wu123456789!@#",db=2)

redis_key = ['btcusdt_trade_detail','ethusdt_trade_detail','eosusdt_trade_detail','xrpusdt_trade_detail','btcusdt_trade_kline','ethusdt_trade_kline','eosusdt_trade_kline','xrpusdt_trade_kline','btcusdt_trade_depth','ethusdt_trade_depth','eosusdt_trade_depth','xrpusdt_trade_depth','btcusdt_detail','ethusdt_detail','eosusdt_detail','xrpusdt_detail']

#获取字典的集合

ch_trade_detail = ["market.btcusdt.trade.detail","market.ethusdt.trade.detail","market.eosusdt.trade.detail","market.xrpusdt.trade.detail"]

#需要获取k线的列表
ch_trade_kline = ["market.btcusdt.kline.1min","market.ethusdt.kline.1min","market.eosusdt.kline.1min","market.xrpusdt.kline.1min"]

#需要获取深度的列表
ch_trade_deepth = ["market.btcusdt.depth.step0","market.ethusdt.depth.step0","market.eosusdt.depth.step0","market.xrpusdt.depth.step0"]

#需要获取的市场列表
ch_trade_market = ["market.btcusdt.detail","market.ethusdt.detail","market.eosusdt.detail","market.xrpusdt.detail"]

#定义成交记录和价格和成交量
def marketTrade(args):
    # 订阅 btc Trade Detail 数据
    tradeStr = """{"sub": """+'"'+args+'"'+""", "id": "id10"}"""
    return tradeStr

#定义k线
def marketKline(args):
    start_time = str(int(time.time()))
    end_time = str(int(time.time() + 1000))
    tradeLine = """{"sub": """+ '"'+ args +'"'+ """, "id": "id10","from":"""+start_time+""","to":"""+end_time+"""}"""
    return tradeLine
#定义深度
def marketDepth(args):
    tradedepth = """{"sub": """ +'"'+ args +'"'+ """, "id": "id10"}"""
    return tradedepth

#定义成交量
def market(args):
    tradeMarket = """{"sub": """ +'"'+ args + '"'+""", "id": "id12"}"""
    return tradeMarket



#请求数据
def getList(args):
    ws.send(args)
    trade_id = ""
    while (1):
        compressData = ws.recv()
        result = gzip.decompress(compressData).decode("utf-8")
        if result[:7] == '{"ping"':
            ts = result[8:21]
            pong = '{"pong":' + ts + "}"
            ws.send(pong)
            ws.send(args)
        else:
            try:
                if trade_id == result["data"]["id"]:
                    print("重复的id")
                    break
                else:
                    trade_id = result["data"]["id"]
            except Exception:
                pass
            print(result)
            return result


#存储redis
# def saveData(key,value):
#     keys = redis_key[key]
#     r.set(keys,value)



if __name__ == "__main__":
    # 定义一个全局的交易对的列表
    arr = []
    for j in ch_trade_detail:
        trade_str = marketTrade(j)
        arr.append(trade_str)

    for k in ch_trade_kline:
        trade_kline = marketKline(k)
        arr.append(trade_kline)

    for l in ch_trade_deepth:
        trade_depth = marketDepth(l)
        arr.append(trade_depth)

    for m in ch_trade_market:
        trade_market = market(m)
        arr.append(trade_market)



    while True:
        try:
            ws = create_connection("wss://www.huobi.bo/-/s/pro/ws")
            break
        except:
            print("请使用中国大陆以外的服务器访问API")
            time.sleep(5)

    while True:

        for i in arr:

            result = getList(i)
            result1 = eval(result)
            print(arr)
            if "ch" in result :
                str = result1["ch"]

                print(type(arr))

                print(type(str))
                #number = arr.index(str)
                #print(number)
            time.sleep(10)

    # while True:
    #     for i in arr:
    #         result = getList(i)
    #         print(result)
    #         time.sleep(5)
            #result1 = eval(result)

            # if i in arr:
            #     numer = arr.index(i)
            #     saveData(numer,result)
            # print(result1)
            # for key in result1:
            #     if key == "ch":
            #         print(result1[key])
           # time.sleep(5)


















