class SMSConfig:
    secretId = "***"
    secretKey = "***"
    SdkAppId = "***"
    signName = "程序员开发宝典"
    templateId = "***"
    sendPhone = ["+***"]
    TemplateParamSet = []


class EmailConfig:
    smtpserver = "smtp.qq.com"
    smtpport = 465
    from_mail = "***"
    password = "***"  # 16位授权码

    my_sender = '1392133729@qq.com'  # 发件人邮箱账号
    my_user = 'wsblx@outlook.com'  # 收件人邮箱账号，我这边发送给自己


currency_cate = [
    {'start_time': '2021-08-17 00:06:45', 'buy_in_price': '2.3496', 'currency': 'value_usdt', 'total_money': '46.99200000'},
    {'start_time': '2021-08-14 00:00:50', 'buy_in_price': '0.00319', 'currency': 'atp_usdt', 'total_money': '31.90000000', "remark": "建议处理掉，最近半年最高值才0。00588"},
    {'start_time': '2021-08-09 00:03:09', 'buy_in_price': '0.017599', 'currency': 'act_usdt', 'total_money': '67.995'},
    {'start_time': '2021-08-07 22:23:48', 'buy_in_price': '0.005000', 'currency': 'kan_usdt', 'total_money': '50.00000000'},
    {'start_time': '2021-08-07 00:55:04', 'buy_in_price': '0.174260', 'currency': 'ach_usdt', 'total_money': '87.13000000', 'remark': "ach一直在增常"},
    {'start_time': '2021-08-07 00:16:38', 'buy_in_price': '0.007164', 'currency': 'cnns_usdt', 'total_money': '71.64000000'},
    {'start_time': '2021-08-06 08:48:41', 'buy_in_price': '0.00158063', 'currency': 'ocn_usdt', 'total_money': '47.4189'},
    {'start_time': '2021-08-06 00:02:07', 'buy_in_price': '2.7696', 'currency': 'fis_usdt', 'total_money': '138.480'},
    {'start_time': '2021-08-05 07:36:25', 'buy_in_price': '0.005970', 'currency': 'top_usdt', 'total_money': '11.940'},
    # {'start_time': '2021-08-04 23:59:21', 'buy_in_price': '1.0566', 'currency': 'rndr_usdt', 'total_money': '52.830'},
    {'start_time': '2021-08-04 23:50:52', 'buy_in_price': '0.0170', 'currency': 'nest_usdt', 'total_money': '85.00'},
    {'start_time': '2021-08-04 19:02:01', 'buy_in_price': '0.000754', 'currency': 'node_usdt', 'total_money': '75.4'},
    {'start_time': '2021-09-04 19:02:01', 'buy_in_price': '7.0665', 'currency': 'agld_usdt', 'total_money': '70.665'},
    {'start_time': '2021-09-06 20:02:01', 'buy_in_price': '0.024715', 'currency': 'ogo_usdt', 'total_money': '49.43'},
    {'start_time': '2021-05-14 19:02:01', 'buy_in_price': '0.0000003776', 'currency': 'gsc_btc', 'total_money': '0.0001888'},
    {'start_time': '2021-09-20 00:20:01', 'buy_in_price': '2.4600', 'currency': 'algo_usdt', 'total_money': '49.2'}
]