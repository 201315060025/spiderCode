# coding: utf-8
"""
1: 获取大众点评数据分为两步
1： 获取所有饮品店的list
2: 根据饮品店list 循环获取每家店的详情
"""
import time
import random
import requests
from pathlib import Path
import numpy as np
import pandas as pd
from requests_html import HTMLSession
from requests_html import HTML
from fake_useragent import UserAgent


session = HTMLSession()
data_dir = Path('D:\dzdp')


headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "_lxsdk_cuid=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _lxsdk=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _hc.v=1c5d904d-e762-ab71-daf7-207f41ee7b11.1558753536; cy=175; cye=zhoukou; s_ViewType=10; _dp.ac.v=68ecf50b-8b9f-4522-a731-7a406ddaff80; dper=260cf7b274ef035c259b9a8a0986f5f28060dad0536527b70ca91836fc6da20720e47c884c2514a3a0f15b8e3f6e59c04a4119159962b6e9dd7ebe491853afa1d78fa5722e415c954dc3688d1560efe61386eea649ba23e0c5fc5d2e9fed59f5; ua=dpuser_9764478807; ctu=4005ec8968b9429cf57db52d599901b198cd1ec6a3175627f7d3242f5cf02981; ll=7fd06e815b796be3df069dec7836c3df; _lxsdk_s=16ba2022439-a4c-9df-506%7C%7C140; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic",
    "Host": "www.dianping.com",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}


page_comment_header = {'Host': 'www.dianping.com',
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
                # 'User-Agent': UserAgent().random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cookie': '_lxsdk_cuid=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _lxsdk=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _hc.v=1c5d904d-e762-ab71-daf7-207f41ee7b11.1558753536; cy=175; cye=zhoukou; s_ViewType=10; _dp.ac.v=68ecf50b-8b9f-4522-a731-7a406ddaff80; dper=260cf7b274ef035c259b9a8a0986f5f28060dad0536527b70ca91836fc6da20720e47c884c2514a3a0f15b8e3f6e59c04a4119159962b6e9dd7ebe491853afa1d78fa5722e415c954dc3688d1560efe61386eea649ba23e0c5fc5d2e9fed59f5; ua=dpuser_9764478807; ctu=4005ec8968b9429cf57db52d599901b198cd1ec6a3175627f7d3242f5cf02981; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1561792912; ll=7fd06e815b796be3df069dec7836c3df; _lxsdk_s=16bcb7fd326-1ac-935-e82%7C%7C370; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic',
                'Upgrade-Insecure-Requests': '1'}

def get_shop_list():
    """
    获取所有商店列表
    :return:
    """
    shop_list = list()
    for pg in range(51):
        print(pg)
        if pg == 0:
            url = 'https://www.dianping.com/search/keyword/175/0_%E9%A5%AE%E5%93%81'
        else:
            url = 'http://www.dianping.com/search/keyword/175/0_%E9%A5%AE%E5%93%81/p{0}'.format(pg)
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            return

        result_shop_list = response.html.find('li a')
        pg_shop_list = set()
        for shop in result_shop_list:
            shop_url = shop.attrs.get('href')
            if not shop_url:
                continue
            shop_url_list = shop_url.split('/')
            if not shop_url_list or len(shop_url_list) < 2:
                continue

            if shop_url_list[-2]=='shop' and shop_url_list[-1].isdigit():
                pg_shop_list.add(shop_url)
        shop_list += pg_shop_list
        print(pg)
    df = pd.DataFrame({'shop_url': shop_list})
    df.to_csv(data_dir / 'shop.csv', index=False)



def get_shop_list_2():
    """只包含周口市的奶茶店"""
    shop_list = list()
    for pg in range(51):
        print(pg)
        if pg == 0:
            url = 'http://www.dianping.com/search/keyword/175/0_%E9%A5%AE%E5%93%81/r4529'
        else:
            url = 'http://www.dianping.com/search/keyword/175/0_%E9%A5%AE%E5%93%81/r4529p{0}'.format(pg)
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            return

        result_shop_list = response.html.find('li a')
        pg_shop_list = set()
        for shop in result_shop_list:
            shop_url = shop.attrs.get('href')
            if not shop_url:
                continue
            shop_url_list = shop_url.split('/')
            if not shop_url_list or len(shop_url_list) < 2:
                continue

            if shop_url_list[-2] == 'shop' and shop_url_list[-1].isdigit():
                pg_shop_list.add(shop_url)
        shop_list += pg_shop_list
        print(pg)
    df = pd.DataFrame({'shop_url': shop_list})
    df.to_csv(data_dir / 'shop_2.csv', index=False)




def get_shop_detail(url, ip):
    """获取商店基本信息"""
    shop_id = url.split('/')[-1]
    url = url + '/review_all'

    header2 = {
        'Host': 'www.dianping.com',
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cookie': '_lxsdk_cuid=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _lxsdk=16aecf36807c8-03788c4e37927e-4c312d7d-100200-16aecf36808c8; _hc.v=1c5d904d-e762-ab71-daf7-207f41ee7b11.1558753536; cy=175; cye=zhoukou; s_ViewType=10; _dp.ac.v=68ecf50b-8b9f-4522-a731-7a406ddaff80; dper=260cf7b274ef035c259b9a8a0986f5f28060dad0536527b70ca91836fc6da20720e47c884c2514a3a0f15b8e3f6e59c04a4119159962b6e9dd7ebe491853afa1d78fa5722e415c954dc3688d1560efe61386eea649ba23e0c5fc5d2e9fed59f5; ua=dpuser_9764478807; ctu=4005ec8968b9429cf57db52d599901b198cd1ec6a3175627f7d3242f5cf02981; ll=7fd06e815b796be3df069dec7836c3df; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1561792912; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1561792912; _lxsdk_s=16ba28771e3-95b-083-f86%7C%7C139; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic',
        'Upgrade-Insecure-Requests': '1'
    }

    # set proxis
    # response = session.get(url, headers=header2, proxies=ip)
    response = session.get(url, headers=header2)
    if response.status_code != 200:
        print('response Error..')
        return None
    try:
        name = response.html.find('.review-shop-wrap .shop-name')[0].text
    except Exception as e:
        print(e)
        name = np.nan

    try:
        XingJi = response.html.find('.review-shop-wrap .rank-info span')[0].attrs['class'][1]
    except Exception as e:
        print(e)
        XingJi = np.nan

    try:
        ZongPin = response.html.find('.review-shop-wrap .reviews')[0].text
    except Exception as e:
        print(e)
        ZongPin = np.nan

    try:
        RenJun = response.html.find('.review-shop-wrap .price')[0].text
    except Exception as e:
        print(e)
        RenJun = np.nan

    try:
        KouWei = response.html.find('.review-shop-wrap .score span')[0].text
    except Exception as e:
        print(e)
        KouWei = np.nan
    try:
        HangJing = response.html.find('.review-shop-wrap .score span')[1].text
    except Exception as e:
        print(e)
        HangJing = np.nan

    try:
        FuWu = response.html.find('.review-shop-wrap .score span')[2].text
    except Exception as e:
        print(e)
        FuWu = np.nan

    try:
        DiZhi = response.html.find('.review-shop-wrap .address-info')[0].text
    except Exception as e:
        print(e)
        DiZhi = np.nan

    try:
        DianHua = response.html.find('.review-shop-wrap .phone-info')[0].text
    except Exception as e:
        print(e)
        DianHua=np.nan
    try:
        DaJiaRenWei = response.html.find('.reviews-tags')[0].text
    except Exception as e:
        print(e)
        DaJiaRenWei = np.nan
    try:
        PingLun = response.html.find('.reviews-filter .filters')[0].text
    except Exception as e:
        print(e)
        PingLun = np.nan

    result_df = pd.DataFrame({
        'name': [name],
        'XingJi': [XingJi],
        'ZongPin': [ZongPin],
        'RenJun': [RenJun],
        'KouWei': [KouWei],
        'HangJing': [HangJing],
        'FuWu': [FuWu],
        'DiZhi': [DiZhi],
        'DianHua': [DianHua],
        'DaJiaRenWei': [DaJiaRenWei],
        'PingLun': [PingLun],
    })
    if result_df.empty:
        print(url)
        return None
    result_df.T.to_csv(base_dir / f"{shop_id}.csv", header=None)



def get_shop_remark(url, is_first_page=True):
    """获取商店评论"""
    # if is_first_page:
    shop_id = url.split('/')[-1]
    url = url + '/review_all'

    header3 = page_comment_header

    response = session.get(url, headers=header3)
    if response.status_code != 200:
        print('response Error..')
        return None
    if not response.html.find('.reviews-items ul li'):
        print('not comment..')


    li_list = list()
    remark_df_list = list()
    for li in response.html.find('.reviews-items ul li .main-review'):
        # main_review = HTML(html=response.html.find('.reviews-items ul li .main-review')[0].html)
        main_review = HTML(html=li.html)

        # people
        comment_user = np.nan
        if main_review.find('.dper-info'):
            comment_user = main_review.find('.dper-info')[0].text

        # star
        XingJi = np.nan
        if main_review.find('.review-rank span'):
            XingJi = main_review.find('.review-rank span')[0].attrs['class'][1]

        # content
        comment_content = np.nan
        if main_review.find('.review-words'):
            comment_content = main_review.find('.review-words')[0].text

        if main_review.find('.review-truncated-words .more-words'):
            comment_content = main_review.find('.review-truncated-words .more-words')[0].text

        # remark time
        remark_time = np.nan
        if main_review.find('.misc-info .time'):
            remark_time = main_review.find('.misc-info .time')[0].text

        li_list.append((comment_user, XingJi, comment_content,remark_time))

    li_df = pd.DataFrame()
    if li_list:
        # li_df = pd.DataFrame({'comment_user':comment_user, 'XingJi':XingJi, 'comment_content': comment_content, 'remark_time':remark_time})
        li_df = pd.DataFrame(li_list, columns=['comment_user', 'XingJi', 'comment_content', 'remark_time'])
    remark_df_list.append(li_df)

    # is more page remark
    if response.html.find('.reviews-pages'):
        total_page = response.html.find('.reviews-pages a')[-2].text
        start_page = 2
        for page in range(2, int(total_page)+1):
            df = loop_page_comment(url, page)

            remark_df_list.append(df)

    remark_df = pd.concat(remark_df_list, axis=0, ignore_index=False)

    # save

    

def loop_page_comment(url, page):
    """获取每页每页评论"""
    url = url + f'/p{page}'

    header3 = page_comment_header
    header3['User-Agent'] = UserAgent().random

    response = session.get(url, headers=header3)
    if response.status_code != 200:
        print('response Error..')
        return None
    if not response.html.find('.reviews-items ul li'):
        print('not comment..')

    li_list = list()
    for li in response.html.find('.reviews-items ul li'):
        main_review = HTML(html=response.html.find('.reviews-items ul li .main-review')[0].html)

        # people
        comment_user = np.nan
        if main_review.find('.dper-info a'):
            comment_user = main_review.find('.dper-info a')[0].text

        # star
        XingJi = np.nan
        if main_review.find('.review-rank span'):
            XingJi = main_review.find('.review-rank span')[0].attrs['class'][1]

        # content
        comment_content = np.nan
        if main_review.find('.review-words'):
            comment_content = comment_content.find('.review-words')[0].text

        if main_review.find('.review-truncated-words .more-words'):
            comment_content = main_review.find('.review-truncated-words .more-words').text

        # remark time
        remark_time = np.nan
        if main_review.find('.misc-info .time'):
            remark_time = main_review.find('.misc-info .time')[0].text

        li_list.append((comment_user, XingJi, comment_content, remark_time))

    li_df = pd.DataFrame()
    if li_list:
        li_df = pd.DataFrame({'comment_user': comment_user, 'XingJi': XingJi, 'comment_content': comment_content,
                              'remark_time': remark_time})
    return li_df







if __name__ == '__main__':
    # get_shop_list()
    # get_shop_list_2()
    shop_dir = Path('D:\dzdp\shop.csv')
    df = pd.read_csv(shop_dir)
    base_dir = Path(r'D:\dzdp\base_info')

    # 设置代理
    # pro_ip_result = requests.get('http://http.tiqu.qingjuhe.cn/getip?num=200&type=1&pack=33811&port=1&lb=1&pb=4&regions=').text.strip().split()
    #
    # proxy_ip_host = pro_ip_result.pop()
    # proxyHost = proxy_ip_host.split(':')[0]
    # proxyPort = proxy_ip_host.split(':')[1]
    # proxyMeta = "http://%(host)s:%(port)s" % {
    #         "host": proxyHost,
    #         "port": proxyPort
    # }
    # proxies = {
    #
    #     "http": proxyMeta,
    #     "https": proxyMeta,
    # }
    # pro_ip_list = pro_ip.values

    # -- 获取店铺基本信息 start
    # for index, u in enumerate(list(df['shop_url'])):
    #     shop_id = u.split('/')[-1]
    #     ff = Path(r'D:\dzdp\base_info') / f"{shop_id}.csv"
    #     if ff.exists():
    #         continue
    #
    #     get_shop_detail(u)
    #     print(u, 'end..')
    #     time.sleep(10)
    # -- 获取店铺基本信息 end

    # -- 获取评论内容 start
    comment_shop_url = pd.read_csv(data_dir / 'shop_2.csv')
    for index, u in enumerate(list(comment_shop_url['shop_url'])):
        u = r'http://www.dianping.com/shop/110587881'
        shop_id = u.split('/')[-1]
        get_shop_remark(u)
