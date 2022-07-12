# Download the helper library from https://www.twilio.com/docs/python/install
import os, time
from twilio.rest import Client

# account_sid = 'AC09a329dda7a8a387a02303d78caab34f'
# auth_token = '5cbdbbd33e958d807ad0fa223d31cbcabd33e958d807ad0fa223d31cbca'
# client = Client(account_sid, auth_token)
#
# # message = "hello world blx test"
# message = client.messages \
#                 .create(
#                      body="hello world",
#                      from_='+1 415 985 6681',
#                      to='+8618811053424'
#                  )
#
# print(time.strftime('%X'))
# print(message.sid)

#
# from twilio.rest import Client
#
# account_sid = 'AC09a329dda7a8a387a02303d78caab34f'
# auth_token = '5cbdbbd33e958d807ad0fa223d31cbca'
# client = Client(account_sid, auth_token)
#
# message1 = """
# <table>
# <tr><td>时间</td><td>价格</td></tr>
# <tr><td>2020-01-01 00：00：00</td><td>10</td></tr>
# </table>
# """
# message2 = "aaa"
#
#
# model = """
# 日期：{date},
# """
#
# message = client.messages.create(
#     messaging_service_sid='MGa97cf7751365ec9e05b23d491f66e23a',
#     body=message2,
#     to='+8618811053424'
# )
# print(message.sid)


# f = "log.txt"
f = open("log.txt", 'a+')
print('12', file=f)
print('13', file=f)