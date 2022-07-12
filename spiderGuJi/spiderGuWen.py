# encoding: utf-8
"""
url: https://so.gushiwen.cn/guwen/
"""
import json, requests, time, os, pickle
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

SAVE_DIR = "" or os.getcwd()


def get_category_first():
    """
    获取估计的大类
    返回格式：
    {
    "经部"：[{"name": "", 'url": ""}]
    }
    """
    url = "https://so.gushiwen.cn/guwen/"
    html_str = requests.get(url)
    res = {}
    if html_str.status_code == 200:
        # 请求成功
        html_val = html_str.text
        result_beautiful = BeautifulSoup(html_val, 'html.parser')

        son2_list = result_beautiful.find_all('div', class_='son2')
        son2_list.pop(0)

        for son2 in son2_list:
            # 获取大类下的每个小类： --》 经部：易类 书类 诗类 礼类...
            category = son2.text.split("：")[0].strip()
            son_list = son2.select('[class~=sright] a')

            res.update({
                category: [{'name': son.text.strip(), 'href': 'https://so.gushiwen.cn' + son.attrs['href']} for son in son_list]
            })
        return res
    else:
        raise "请求主类目失败！"



def get_category_second(url):
    """
    获取易类下面所有的类别
    经部：易类 --> 周易(先秦) 易传(先秦) 子夏易传(先秦)
    """
    html_str = requests.get(url)
    res = []
    if html_str.status_code == 200:
        # 请求成功
        html_val = html_str.text
        result_beautiful = BeautifulSoup(html_val, 'html.parser')

        son2_list = result_beautiful.select('div[class="typecont"] span')

        return [{'name': i.text, 'href': 'https://so.gushiwen.cn' + i.next.attrs['href']} for i in son2_list]
    else:
        raise "请求🎧目标失败"

def get_category_third(url):
    """获取三级目录或四级别，最终文件路径"""
    html_str = requests.get(url)
    res = []
    if html_str.status_code == 200:
        # 请求成功
        html_val = html_str.text
        result_beautiful = BeautifulSoup(html_val, 'html.parser')

        bookcont_list = result_beautiful.select('div[class="sons"] div[class="bookcont"]')
        book_detail_res = []
        for bookcont in bookcont_list:
            bookcont_parent = bookcont.find('div', class_='bookMl')
            if bookcont_parent:
                parent_name = bookcont_parent.text.strip()
                book_detail_list = bookcont.select('div span a')
                book_detail_res.extend([{'name': i.text.strip(), 'href': i.attrs.get('href'), 'parent_name': parent_name} for i in book_detail_list])
            else:
                book_detail_list = bookcont.select('div ul span a')
                book_detail_res.extend([{'name': i.text.strip(), 'href': i.attrs.get('href')} for i in book_detail_list])
        return book_detail_res
    else:
        raise "请求🎧目标失败"

number = 0
def write_file(f_name, url):
    """写文件操作"""
    if url is None:
        with open(f_name, 'w', encoding='utf-8') as f:
            f.write('')
        return 'sucess'
    try:
        html_str = requests.get(url)
    except:
        print('e')

    global number
    number += 1
    if os.path.exists(f_name):
        print('{} {} 文件已经存在'.format(number, f_name))
        return 'sucess'

    if html_str.status_code == 200:
        # 请求成功
        html_val = html_str.text
        result_beautiful = BeautifulSoup(html_val, 'html.parser')

        content_list = result_beautiful.select('div[class="contson"] p')
        content_res = []
        for bookcont in content_list:
            if bookcont.text.strip():
                content_res.append(bookcont.text.strip()+"\n")
            pass
        print('**** {} {} 写入成功'.format(number, f_name))
        with open(f_name, 'w', encoding='utf-8') as f:
            f.writelines(content_res)
        return 'sucess'
    else:
        print("{} {}: 写文件失败失败".format(number, url))
        return 'fail'


def loop_write_file(dir_name, cur_val_list, file_list):

    for cur_val in cur_val_list:
        if cur_val.get('children'):
            loop_write_file(os.path.join(dir_name, cur_val['name']), cur_val.get('children'), file_list)
        else:
            if os.path.exists(dir_name) == False:
                os.makedirs(dir_name)
            file_name = os.path.join(dir_name, "{}.txt".format(cur_val['name'].replace('/','_')))
            if cur_val.get('parent_name'):
                tmp_name = os.path.join(dir_name, cur_val.get('parent_name'))
                if os.path.exists(tmp_name) == False: os.makedirs(tmp_name)
                file_name = os.path.join(tmp_name, "{}.txt".format(cur_val['name'].replace('/','_')))
            # write_file(file_name, cur_val['href'])
            file_list.append([file_name, cur_val['href']])


def spider_cate():
    """"""
    ff = "spiderShiCi.pkl"
    if os.path.exists(ff):
        with open(ff, 'rb') as f:
            data = pickle.load(f)
    else:
        # 获取第一级类目
        res = get_category_first()
        # 获取第二级类目
        t1 = time.time()
        for _, first_cates in res.items():
            for first_cate in first_cates:
                res2 = get_category_second(first_cate['href'])
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
                    res3 = get_category_third(son['href'])
                    print('{}-{}-{} 存在 {} 条'.format(_, name, son['name'], len(res3)))
                    son.update({'children': res3})
                    print('res')
                print('\n' * 3)
        print('获取文本详情文件耗时： {}'.format(time.time() - t2))

        # 开始写操作
        file_list = []
        for k, v in res.items():
            loop_write_file(os.path.join(SAVE_DIR, k), v, file_list)
        with open(ff, 'wb') as f:
            pickle.dump(file_list, f)
        data = file_list
    return data


def main():

    file_list = spider_cate()
    print('一共需要下载{}个'.format(len(file_list)))

    # 多线程下载文件
    with ThreadPoolExecutor(max_workers=5) as t:
        tt_list = [t.submit(write_file, i[0], i[1]) for i in file_list]
        for tt in as_completed(tt_list):
            data = tt.result()
            print("thread==", data)

main()



