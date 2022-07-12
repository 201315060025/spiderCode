# encoding:utf-8
"""
中国哲学书电子化计划
简体字版

https://ctext.org/zhs
"""

import json, requests, time, os, pickle
import random

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys

SAVE_DIR = "" or os.getcwd()
# 是否使用代理  https://www.kuaidaili.com/free/inha/
use_proxy = True
number = 0


class SpiderCtext:
    def __init__(self):
        pass

    def get_second_third_data(self, cur_element_list):
        """获取第二和第三级别的数据"""

        def get_cur_title(cur_element):
            # children_ele = [i for i in cur_element.children if hasattr(i, 'attrs') and 'menuitem' in i.attrs['class']]
            children_ele = cur_element.select('span[class="subcontents"] a[class="menuitem"]')
            # children_ele.pop(0)
            return [{'name': j.text.strip(), 'href': 'https://ctext.org/' + j.attrs['href']} for j in children_ele]

        res = []
        for i in cur_element_list:
            cur_name = [j for j in i.children if hasattr(j, 'attrs') and 'menuitem' in j.attrs.get('class', [])][0]
            name, href = cur_name.text.strip(), cur_name.attrs['href']
            children = get_cur_title(i)
            print('{} 总共有{}条'.format(name, len(children)))
            res.append({'name': name, 'href': 'https://ctext.org/' + href, 'children': children})
        return res

    def get_category_first(self):
        # 获取主元素的父id

        url = "https://ctext.org/zhs"
        html_str = requests.get(url)
        res = {}
        if html_str.status_code == 200:
            # 请求成功
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')
            res = {"先秦两汉": [], '汉代之后': []}
            son2_list = result_beautiful.select("div[id=menu]")
            if son2_list:
                box_obj = son2_list[0]
                # 一级标题 只需要前面两个 先秦两代和 汉代之后
                title_list = box_obj.select('div[class="menuitem listhead"]')[:2]
                # 每个标题下的二级元素
                son_list = box_obj.select('span[class="menuitem container"]')
                son_list.pop(0)
                res.update({
                    title_list[0].text.strip(): self.get_second_third_data(son_list[:-5]),
                    title_list[1].text.strip(): self.get_second_third_data(son_list[-5:])
                })
            pass
        else:
            print("请求主类目失败！")
        return res

    def get_four_category(self, url):
        # url = 'https://ctext.org/analects/zhs'
        html_str = requests.get(url)
        res = {}
        if html_str.status_code == 200:
            # 请求成功
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')

            content_list = result_beautiful.select("div[id=content2]")
            if content_list:
                box_obj = content_list[0]
                title_list = [i for i in box_obj.children if i.name == 'a']

                return [{'name': i.text.strip(), 'href': 'https://ctext.org/' + i.attrs.get('href')} for i in
                        title_list]

            pass
        else:
            print("请求主类目失败！")
        return []

    def spider_main(self):
        """"""
        ff = "spiderCtext.pkl"
        if os.path.exists(ff):
            with open(ff, 'rb') as f:
                data = pickle.load(f)
        else:
            # 获取三级目录
            res = self.get_category_first()
            # 获取第四级目录
            for k1, cate in res.items():
                for cate2 in cate:
                    for cate3 in cate2['children']:
                        four_title = self.get_four_category(cate3['href'])
                        cate3['children'] = four_title
                        print("{}-{}-{} 一共{} 条".format(k1, cate2['name'], cate3['name'], len(four_title)))
                        time.sleep(1)

            with open('spiderCtext.pkl', 'wb') as f:
                pickle.dump(res, f)
            data = res

        return data

    def loop_write_file(self, dir_name, cur_val_list, file_list):

        for cur_val in cur_val_list:
            if cur_val.get('children') or cur_val.get('children'):
                self.loop_write_file(os.path.join(dir_name, cur_val['name']), cur_val.get('children'), file_list)
            else:
                if os.path.exists(dir_name) == False:
                    os.makedirs(dir_name)
                file_name = os.path.join(dir_name, "{}.txt".format(cur_val['name'].replace('/', '_')))
                file_list.append([file_name, cur_val['href']])
                # if cur_val.get('parent_name'):
                #     tmp_name = os.path.join(dir_name, cur_val.get('parent_name'))
                #     if os.path.exists(tmp_name) == False: os.makedirs(tmp_name)
                #     file_name = os.path.join(tmp_name, "{}.txt".format(cur_val['name'].replace('/', '_')))
                # # write_file(file_name, cur_val['href'])
                # file_list.append([file_name, cur_val['href']])

    def get_proxy(self, url):
        """"""
        api_url = "http://tps.kdlapi.com/api/gettps/?orderid=******&num=1&pt=1&sep=1"
        proxy_ip = [requests.get(api_url).text]
        username = "*****"
        password = "****"

        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password,
                                                            'proxy': random.choice(proxy_ip)},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {'user': username, 'pwd': password,
                                                             'proxy': random.choice(proxy_ip)}
        }
        headers = {
            # "Accept-Encoding": "Gzip",  # 使用gzip压缩传输数据让访问更快
        }
        r = requests.get(url, proxies=proxies, headers=headers)
        return r

    def write_file(self, f_name, url):
        """写文件操作"""
        global number
        if os.path.exists(f_name):
            number += 1
            print('{} {} 文件已经存在'.format(number, f_name))
            return 'sucess'

        if url is None:
            with open(f_name, 'w', encoding='utf-8') as f:
                f.write('')
            return 'sucess'
        try:
            # html_str = requests.get(url)
            html_str = self.get_proxy(url) if use_proxy else requests.get(url)
        except:
            print('e')
            return 'error'

        if html_str.status_code == 200:
            # time.sleep(random.choice([0.1, 0.2, 0.3, 0.4, 0.5]))
            # 请求成功
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')
            context = list()
            content_list1 = result_beautiful.select('div[id="content3"] table[border="0"] tr')
            for tt in content_list1:
                td_list = tt.select('td')
                if td_list:
                    context.append(td_list[-1])
            content_res = []
            for bookcont in context:
                if bookcont.text.strip():
                    content_res.append(bookcont.text.strip() + "\n")
                pass
            number += 1
            print('**** {} {} 写入成功'.format(number, f_name))
            with open(f_name, 'w', encoding='utf-8') as f:
                f.writelines(content_res)
            return 'sucess'
        else:
            print("{} {}: 写文件失败失败".format(number, url))
            return 'fail'
        pass

    def main(self):
        data = self.spider_main()
        file_list = []
        for k, v in data.items():
            self.loop_write_file(os.path.join(SAVE_DIR, k), v, file_list)
        print('一共需要下载{}个'.format(len(file_list)))
        for i in file_list:
            # i = ['/Users/4paradigm/code/person/projectDemo/AdilCrawler/spiderGuJi/blx/blx/先秦两汉/儒家/中论/亡国.txt', 'https://ctext.org/zhong-lun/zhi-xue/zhs']
            res = self.write_file(i[0], i[1])
            if res == 'error':
                aa = 0
                if use_proxy:
                    while True:
                        aa += 1
                        print('{}代理获取失败{}开始获取'.format(i[1], aa))
                        res = self.write_file(i[0], i[1])
                        if res != 'error':
                            break



        # # 多线程下载文件
        # with ThreadPoolExecutor(max_workers=5) as t:
        #     tt_list = [t.submit(self.write_file, i[0], i[1]) for i in file_list[::-1]]
        #     for tt in as_completed(tt_list):
        #         data = tt.result()
        #         print("thread==", data)


SpiderCtext().main()
