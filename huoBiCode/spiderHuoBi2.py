import asyncio, json
import logging
from datetime import datetime
from aiowebsocket.converses import AioWebSocket
import gzip

import requests

"""
market.htusdt.trade.detail  请求 ht-ustd 实时交易价格

08-17 00:06:45   value_usdt    2.3496
08-14 00:00:50   atp_usdt     0.00319
08-09 00:03:00   act_usdt  0.017599
08-07 22:23:48   kan_usdt   0.005000
08-07 00:55:04   ach_usdt   0.174260

"""


currency_cate = [
    {"start_time": "08-17 00:06:45", 'buy_in_price': "2.3496", "currency": "value_usdt"},
]


async def startup(uri):
    async with AioWebSocket(uri) as aws:
        converse = aws.manipulator
        # message = '{"sub":"market.btcusdt.trade.detail","symbol":"btcusdt"}'
        # message = '{"sub":"market.tickers","symbol":"htusdt"}'
        # 最近24小时成交量、成交额、开盘价、收盘价、最高价、最低价、成交笔数等
        message = '{"sub":"market.btcusdt.detail","symbol":"btcusdt"}'
        while True:
            await converse.send(message)
            # print('{time}-Client send: {message}'
            #       .format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message=message))
            mes = await converse.receive()
            mes1 = gzip.decompress(mes).decode("utf-8")
            res = json.loads(mes1)
            print('{time}-Client receive: {rec}'
                  .format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rec=mes1))


def main():
    remote = 'wss://www.huobi.bo/-/s/pro/ws'
    try:
        asyncio.get_event_loop().run_until_complete(startup(remote))
    except KeyboardInterrupt as exc:
        logging.info('Quit.')


class SpiderControl(object):
    def __init__(self):
        pass




if __name__ == '__main__':
    # remote = 'ws://echo.websocket.org'
    main()
