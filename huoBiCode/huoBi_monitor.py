import asyncio, json, pickle, os
import logging, random
from datetime import datetime, timedelta, date
from aiowebsocket.converses import AioWebSocket
import gzip
from senMessageTool import SendMessageTool
from config.config import currency_cate


def handle(current_data, currency_data):
    buy_price = float(currency_data['buy_in_price'])
    new_price = float(current_data['close'])
    flag = (new_price - buy_price) / buy_price
    return flag > 0.9

# <a class="js-navigation-open Link--primary" title="redis.conf" data-pjax="#repo-content-pjax-container" href="/redis/redis/blob/unstable/redis.conf">redis.conf</a>

def cal_time(start_time:str, end_time:str)->str:
    st = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    ed = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    return str((ed-st).days)


def current_time(format='%Y-%m-%d %H:%M:%S', is_str=True):
    if is_str:
        return datetime.now().strftime(format)
    else:
        return datetime.now()


async def get_effective_data(uri, message_type:str, log):
    connect_times = 0
    while True:
        connect_times += 1
        async with AioWebSocket(uri) as aws:
            converse = aws.manipulator
            await converse.send(message_type)
            mes = await converse.receive()
            mes1 = gzip.decompress(mes).decode("utf-8")
            res = json.loads(mes1)
            if "status" in res and res['status'].lower() == 'ok':
                return converse
            print(f'{uri} 链接失败，尝试第{str(connect_times)} 次链接')
            print(f'{uri} 链接失败，尝试第{str(connect_times)} 次链接', file=log)
            # await asyncio.sleep(random.randint(300, 900))
            await asyncio.sleep(random.randint(1, 10))
            if connect_times >5:
                SendMessageTool.send_message_by_sms('')
                raise ('多次链接服务器错误， 请查看原因')



async def day_execute(uri,  parame, config):
    file = open(f'log/{config["log"]}', mode='a+', encoding='utf-8')
    current_day = ""
    while True:
        new_day = datetime.now().strftime('%Y-%m-%d')
        # if len(current_day) == 0:
        #    current_day = new_day

        if new_day != current_day:
            current_day_message = []
            for currency_data in parame:
                ct = currency_data['currency'].replace('_', '')
                message = '{"sub":"market.' + ct + '.kline.1min","symbol":"' + ct + '", "id": "id1"}'
                converse = await get_effective_data(uri, message, file)
                try:
                    await converse.send(message)
                    mes = await converse.receive()
                except Exception as e:
                    print(f'{current_time()}: 每日发送邮箱 converse.send() 获取数据失败{ct}, {e}', file=file)
                    continue

                mes1 = gzip.decompress(mes).decode("utf-8")
                res = json.loads(mes1)
                if "tick" not in res:
                    print(f'{current_time()}: 每日发送邮箱 {ct}统计数据失败', file=file)
                    continue

                name = currency_data["currency"].split('_')[0]
                newPrice = res['tick']['close']
                buy_price = float(currency_data['buy_in_price'])
                rate = str(round((newPrice - buy_price) / buy_price, 3))
                hold_money = currency_data['total_money']
                hold_time = cal_time(currency_data['start_time'], new_day + " 00:00:00")
                # name, 买入金额, 持有时间, 买入价, 当前价格, 增常率
                message = [f"{name},{hold_money}, {hold_time}, {str(buy_price)},{str(newPrice)}, {rate}"]
                current_day_message.extend(message)

            # 只发邮箱
            SendMessageTool.send_message_by_email(current_day_message)
            # 同时保存一个记录
            data_f = 'data/huoBi_monitor.pkl'
            if os.path.exists(data_f):
                with open(data_f, 'rb') as ff:
                    data = pickle.load(ff)
            else:
                data = {}

            data.update({
                new_day: current_day_message
            })
            with open(data_f, 'wb') as ff:
                pickle.dump(data, ff)

            if len(current_day) == 0:
                tmp_day = date(*[int(i) for i in new_day.split('-')]) + timedelta(days=1)
                tmp_new_day = datetime(tmp_day.year, tmp_day.month, tmp_day.day)
                sleep_time = (tmp_new_day - datetime.now()).seconds
            else:
                # 一天有多少秒
                sleep_time = 24 * 60 * 60-2
            current_day = new_day

            await asyncio.sleep(sleep_time)


async def startup(uri, ct, parame, config):
    file = open(f'log/{config["log"]}', mode='a+', encoding='utf-8')
    message = '{"sub":"market.' + ct + '.kline.1min","symbol":"' + ct + '", "id": "id1"}'
    converse = None
    count = 0
    start_minute = datetime.now().minute
    new_day = datetime.now().strftime('%Y-%m-%d')

    while True:
        print("开始获取数据。。")
        currency_date = datetime.now().minute
        if converse is None:
            print('建立链接。。')
            converse = await get_effective_data(uri, message, file)
            # SendMessageTool.send_message_by_sms('')
            # raise ('多次链接服务器错误， 请查看原因')
        else:
            try:
                await converse.send(message)
                mes = await converse.receive()
            except Exception as e:
                if currency_date - start_minute == 1:
                    print(f"{current_time()}: converse.send() 获取数据失败{ct}, {e}", file=file)
                    start_minute = currency_date
                continue
            # gzip.BadGzipFile: Not a gzipped file
            try:
                mes1 = gzip.decompress(mes).decode("utf-8")
                res = json.loads(mes1)
                print("解析数据...")
            except Exception as e:
                if currency_date - start_minute == 1:
                    print(f"{current_time()}: gzip.decompress 解析失败{ct}, {e}", file=file)
                    start_minute = currency_date
                continue

            if "tick" not in res:
                # 请求开始 没有数据
                # return
                continue

            # 每隔一个小时输出一条日志，主要是证明程序还在运行
            currency_date = datetime.now().minute
            if currency_date - start_minute == 1:
                print(
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {ct} ， 买入价格：{parame["buy_in_price"]}, 当前价格：{res["tick"]["close"]}',
                    )
                print(
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {ct} ， 买入价格：{parame["buy_in_price"]}, 当前价格：{res["tick"]["close"]}',
                    file=file)
                start_minute = currency_date

            # 判断是否发短信
            if handle(res['tick'], parame) and count == 0:
                # 已经大雨30¥ 可以考虑卖出
                name = parame["currency"].split('_')[0]
                buy_price = float(parame['buy_in_price'])
                newPrice = res['tick']['close']
                rate = str(round((newPrice - buy_price) / buy_price, 3))
                hold_money = parame['total_money']
                hold_time = cal_time(parame['start_time'], new_day + " 00:00:00")
                send_message = [f"{name}, {str(buy_price)}, {str(newPrice)}, {rate}"]
                send_email_message = [f"{name},{hold_money}, {hold_time}, {str(buy_price)},{str(newPrice)}, {rate}"]
                # 同时邮箱发送和 短信发送
                SendMessageTool.send_message_by_email(send_email_message)
                SendMessageTool.send_message_by_sms(send_message)
                count += 1
                print(f'{parame["currency"]} 已经达到了增常率， 可以考虑出手', file=file)
            await asyncio.sleep(1)

async def get_data_from_huobi(config):
    print('12')
    remote = 'wss://www.huobi.tf/-/s/pro/ws'
    try:
        # task1 = asyncio.create_task(startup(remote, ct, parame))
        gather_list = []
        # 1: 监控每个币种的实时价格
        for currency_data in currency_cate:
            gather_list.append(
                startup(remote, currency_data['currency'].replace('_', ''), currency_data, config)
            )
        # 2： 统计每个币种每天的变化趋势
        gather_list.append(day_execute(remote, currency_cate, config))
        await asyncio.gather(*gather_list)
    except KeyboardInterrupt as exc:
        logging.info('Quit.')
    # pass


def main(config):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_data_from_huobi(config))

main({"log": "ab.txt"})
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(get_data_from_huobi())
    # asyncio.run(get_data_from_huobi())