# coding: utf-8
"""
爬取证卷宝的数据  http://www.baostock.com/
"""
import os
import csv
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import baostock as bs
# from crawl_spider import BaseSpider


class StSuspensionSpider(object):

    def __init__(self,
                 name='',
                 data_dir: Path = None,
                 fields=None,
                 pause=0,
                 begin_date='',
                 logger=None,
                 backup_dir: Path = None,
                 error_code_path: Path = None,
                 max_count: int = 0,
                 enable_update: bool = True,
                 **kwargs):

        self.name = name
        self.data_dir = data_dir

        self.fields = fields
        self.pause = pause
        self.begin_date = begin_date
        self.logger = logger
        self.backup_dir = backup_dir
        self.error_code_path = error_code_path

        self.max_count = max_count
        self.enable_update = enable_update

        self.index_df = pd.DataFrame()

    def get_data_from_url(self, code=''):
        """
        从yahoo获取数据

        :param code:
        :return:
        """
        data_file = self.data_dir
        f = data_file.joinpath('source') / f'{code}.csv'

        code_df = self.index_df.loc[self.index_df['code'] == code]
        start_date = list(code_df['start_date'])[0]
        end_date = list(code_df['end_date'])[0]
        source_code = list(code_df['code_format'])[0]

        # set end date
        # if end_date.strftime("%Y-%m-%d") == '2099-12-31':
        #     end_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))

        # set end date
        if f.exists():
            source_data_df = pd.read_csv(f)
            source_data_df.sort_values('date', inplace=True)
            start_date = list(source_data_df['date'])[0] if list(source_data_df['date']) else start_date

        data_rs = bs.query_history_k_data_plus(source_code, "date, tradestatus,isST", start_date=start_date, end_date=end_date,
                                               frequency="d", adjustflag="3")
        data_list = []
        while (data_rs.error_code == '0') & data_rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(data_rs.get_row_data())
        data_result = pd.DataFrame(data_list, columns=data_rs.fields)

        return data_result

    def get_stock_code_list(self):
        print(f'开始获取股票列表......')

        # set zjb login and logout
        bs.logout()
        bs.login()

        data_path = self.data_dir.parent
        all_index_file = data_path / 'all_index.csv'
        csi_all_file = data_path / 'csi_all.txt'

        # get data
        rs = bs.query_stock_basic()

        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())

        result = pd.DataFrame(data_list, columns=rs.fields)
        all_index = result.loc[result['type'] == '1']

        all_index.rename(columns={"code": 'code_format', 'ipoDate': 'start_date', 'outDate': 'end_date'}, inplace=True)
        all_index['code'] = all_index['code_format'].map(lambda x: (x.split('.')[0]).upper() + x.split('.')[1])
        all_index['end_date'] = all_index['end_date'].replace("", '2099-12-31')

        # 手动添加一致特殊股票
        all_index_cl = all_index.columns.tolist()
        add_rows = dict(zip(all_index_cl, [np.nan] * len(all_index_cl)))
        add_rows.update({"code": "SH601313", 'start_date': "2012-01-16", 'end_date': '2018-02-14'})
        all_index = all_index.append(pd.DataFrame(add_rows, index=[0]))
        all_index.to_csv(all_index_file, index=False)

        # spcially code
        # start date keep same
        teshu_code = {
            "SZ001872": "2018-12-26",
            "SH601360": "2018-02-28",
            "SH600653": '1990-12-19',
            "SH600018": "2000-07-19",
            "SZ000005": "1990-12-19"
        }
        for k, v in teshu_code.items():
            all_index.loc[all_index['code'] == k, 'start_date'] = v

        csi_index = all_index.filter(['code', 'start_date', 'end_date'])
        csi_index.to_csv(csi_all_file, columns=['code', 'start_date', 'end_date'], index=False, header=None, sep='\t')
        #
        self.index_df = all_index
        return list(csi_index['code'])



if __name__ == "__main__":
    """
    name='',
                 data_dir: Path = None,
                 fields=None,
                 pause=0,
                 begin_date='',
                 logger=None,
                 backup_dir: Path = None,
                 error_code_path: Path = None,
                 max_count: int = 0,
                 enable_update: bool = True,
    """
    st_obj = StSuspensionSpider(
        name="证卷宝",
        data_dir=Path(os.getcwd()),
        fields=None,
        pause=0,
        begin_date='',
        logger=None,
        backup_dir = None,
        error_code_path= None,
        max_count= 0,
        enable_update= True
    )
    code_list = st_obj.get_stock_code_list()
    for code in code_list:
        st_obj.get_data_from_url(code)
    pass
