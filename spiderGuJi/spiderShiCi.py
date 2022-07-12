# encoding:utf-8
"""
诗词地址：https://gj.zdic.net/list.php?caid=47
"""

import json, requests, time, os, pickle
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED, as_completed

SAVE_DIR = "" or os.getcwd()


class SpiderShiCi:
    def __init__(self):
        self.num = 0
        pass

    def get_category_first(self):
        """
        第一级目录： 集部-》词， 楚辞...
        """
        url = "https://gj.zdic.net/"
        html_str = requests.get(url)
        if html_str.status_code == 200:
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')
            # 获取一级和🎧内容
            box_obj = result_beautiful.select('div[id=gj_dh_z] div')
            # box_obj.pop()
            res = {}
            if len(box_obj) != 8:
                raise "获取类别有错误"
            for i in range(0, 4):
                cate_name = box_obj[i].text.strip()
                children_list = box_obj[i+4].select('ul li a')
                res.update({
                    cate_name: [{'name': i.text.strip(), "href": 'https://gj.zdic.net' + i.attrs.get('href')} for i in children_list],
                })
                # break
            return res
        else:
            raise "{} 获取数据失败".format(url)

    def _get_cur_page_data(self, dl_obj):
        """
        当前传入的对象是dl 标签
        """
        cir_list = dl_obj.select('dd ul li b a')
        return [{'name': i.text.strip(), 'href': "https://gj.zdic.net/"+i.attrs.get('href')} for i in cir_list if i.attrs.get('href')]

    def _get_end_flag(self, cur_num,end_num, range=9):
        return cur_num + range == end_num

    def _write_file(self, f_name, url):
        """写文件操作"""
        if url is None:
            with open(f_name, 'w', encoding='utf-8') as f:
                f.write('')
            return 'success'
        try:
            html_str = requests.get(url)
        except:
            print('e')

        self.num += 1
        if os.path.exists(f_name):
            print('{} {} 文件已经存在'.format(self.num, f_name))
            return 'success'

        if html_str.status_code == 200:
            # 请求成功
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')

            content_res = result_beautiful.select('div[id="snr2"]')
            if content_res:
                print('**** {} {} 写入成功'.format(self.num, f_name))
                with open(f_name, 'w', encoding='utf-8') as f:
                    f.writelines(content_res[0].text.strip())
            return 'sucess'
        else:
            print("{}: 写文件失败失败".format(url))
            return 'fail'

    def loop_write_file(self, dir_name, cur_val_list,file_list):

        for cur_val in cur_val_list:
            if cur_val.get('children'):
                self.loop_write_file(os.path.join(dir_name, cur_val['name']), cur_val.get('children'), file_list)
            else:
                if os.path.exists(dir_name) == False:
                    os.makedirs(dir_name)

                jieshao_con = cur_val.get('jieShao')
                file_name = os.path.join(dir_name, "{}.txt".format(cur_val['name'].replace('/', '_')))
                if jieshao_con:
                    jieshao_ff = os.path.join(dir_name, '介绍.txt')
                    if os.path.exists(jieshao_ff) == False:
                        with open(jieshao_ff, 'w', encoding='utf-8') as f:
                            f.write(cur_val['jieShao'])

                # self._write_file(file_name, cur_val['href'])
                file_list.append([file_name, cur_val['href']])

    def get_category_second(self, url):
        """
        第二级目录： 楚辞-》文心雕龙...
        # 每页10个
        """
        html_str = requests.get(url)
        if html_str.status_code == 200:
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')
            total_cir_list = []
            # 判断有没有分页数据
            box_obj = result_beautiful.select('div[id=list_d_1] dl')
            if box_obj is None:
                return []
            box_obj = box_obj[0]
            total_cir_list.extend(self._get_cur_page_data(box_obj))
            page_nav_list = box_obj.select('div[class=pagenav] div[class=p_bar] a')
            if page_nav_list:
                cur_page_nav = box_obj.select('div[class=pagenav] div[class=p_bar] a[class=p_curpage]')[0].text.strip()

                if cur_page_nav == page_nav_list[-1].text.strip():
                    return total_cir_list

                # 找出当前页所在的索引
                # <a class="p_curpage">2</a>
                cur_page_idx = [idx for idx, i in enumerate(page_nav_list) if "p_curpage" in i.attrs.get('class', [])]
                cur_url = page_nav_list[cur_page_idx[0] + 1].attrs.get('href')
                total_cir_list.extend(self.get_category_second(cur_url))
            return total_cir_list
        else:
            raise ("{} 二级目录请求失败".format(url))

    def get_category_third(self, url):
        """
        获取文件路径：
        笏山记--》◎ 第一回　可家儿读书贻笑　玉氏子出山求名,◎ 第二回　赂本官拙行铁扇子　惩土恶痛打丁霸王....
        """
        html_str = requests.get(url)
        if html_str.status_code == 200:
            html_val = html_str.text
            result_beautiful = BeautifulSoup(html_val, 'html.parser')
            # 获取一级和🎧内容
            box_obj = result_beautiful.select('div[id=ml_2] div[class=mls] li a')

            # 获取介绍数据
            jieshao = ''
            if result_beautiful.select('div[id=jj_2]'):
                jieshao = result_beautiful.select('div[id=jj_2]')[0].text.strip()

            return [{'name': i.text.strip().replace(' ', '-'), "jieShao":jieshao, 'href': 'https://gj.zdic.net/' + i.attrs.get('href')} for i in box_obj]
        else:
            raise "{} 三级目录获取数据失败".format(url)


    def spider_category(self):
        """下载所有的目录"""
        ff = "spiderShiCi.pkl"
        if os.path.exists(ff):
            with open(ff, 'rb') as f:
                data = pickle.load(f)
        else:
            # 第一级 数据
            res = self.get_category_first()
            #
            # 获取第二级类目
            t1 = time.time()
            for _, first_cates in res.items():
                for first_cate in first_cates:
                    res2 = self.get_category_second(first_cate['href'])
                    first_cate.update({'children': res2})

            print('获取一级和二级的分类耗时：{}'.format(time.time() - t1))

            t2 = time.time()

            # 获取三级目录和四级目录
            for _, firat_cates in res.items():
                for first_cate in firat_cates:
                    if 'name' not in first_cate or 'children' not in first_cate:
                        print('{} 目录下是空'.format(_))
                        continue
                    name = first_cate['name']
                    print('{}-{}-存在 {} 条'.format(_, name, len(first_cate['children'])))
                    for son in first_cate['children']:
                        res3 = self.get_category_third(son['href'])
                        print('{}-{}-{} 存在 {} 条'.format(_, name, son['name'], len(res3)))
                        son.update({'children': res3})
                        print('res')
                    print('\n' * 3)
            print('获取文本详情文件耗时： {}'.format(time.time() - t2))
            # print(res)
            file_list = []
            # 开始写操作
            for k, v in res.items():
                self.loop_write_file(os.path.join(SAVE_DIR, k), v, file_list)
            with open(ff, 'wb') as f:
                pickle.dump(file_list, f)
            data = file_list
        return data

    def main(self):
        """
        数据生成
        """
        file_list = self.spider_category()
        print('一共需要下载{}个'.format(len(file_list)))
        # 多线程下载文件
        with ThreadPoolExecutor(max_workers=5) as t:
            tt_list = [t.submit(self._write_file, i[0], i[1]) for i in file_list]
            wait(tt_list, return_when=FIRST_COMPLETED)
            for tt in as_completed(tt_list):
                data = tt.result()
                print("thread==", data)




obj = SpiderShiCi()
obj.main()
