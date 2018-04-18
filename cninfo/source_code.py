'''
巨潮公告抓取规则，向query网址post查询信息得到公告列表
公告列表中包括公告的PDF网址、公告名称、证券代码等信息
'''

import requests
import webbrowser
from tabulate import tabulate
from math import ceil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime


def post_query(stock_code, date, pagenum):
    response = requests.post(
        'http://www.cninfo.com.cn/cninfo-new/announcement/query',
        data={'stock': stock_code, 'seDate': date, 'pageNum': pagenum})
    response.raise_for_status()
    return eval(response.text.replace('null', 'None').replace(
        'true', 'True').replace('false', 'False'))


def get_total_pagenum(stock_code, date):
    response = post_query(stock_code, date, 1)
    return ceil(response['totalAnnouncement'] / 30)


def get_announcement_list(stock_code, date):
    ann = []
    for i in range(1, get_total_pagenum(stock_code, date) + 1):
        ann += post_query(stock_code, date, i)['announcements']
    return ann


def open_pdf(ann):
    for x in ann:
        x['公告名称'] = x['announcementTitle'] + x['adjunctUrl'].split('.')[1]
    table = [[i, x['secName'], x['adjunctUrl'].split('/')[1], x['公告名称']]
             for i, x in enumerate(ann)]
    print(tabulate(table, ['编号', '证券名称', '日期', '公告']))

    while True:
        number = input('请输入公告编号查看公告（按回车键跳过）：')
        if not number:
            return
        try:
            number = int(number)
            ann[number]
        except:
            print('编号错误，请重新输入！')
            continue
        break

    webbrowser.open('http://www.cninfo.com.cn/' + ann[number]['adjunctUrl'])


def date_boundary(date):
    if len(date.split('-')) == 3:
        return [date, date]
    elif len(date.split('-')) == 2:
        date = parse(date, default=datetime(2000, 1, 1))
        return [x.strftime('%Y-%m-%d') for x in
                [date, date + relativedelta(months=1, days=-1)]]
    elif len(date.split('-')) == 1:
        date = parse(date, default=datetime(2000, 1, 1))
        return [x.strftime('%Y-%m-%d') for x in
                [date, date + relativedelta(years=1, days=-1)]]
    else:
        raise


def parse_date_string(date):
    if ',' in date:
        date = date.replace(' ', '').split(',')
    else:
        date = [date] * 2
    date = [date_boundary(x)[i] for i, x in enumerate(date)]
    date.insert(1, '~')
    return ' '.join(date)


def main_event():
    while True:
        stock_code = input(tabulate(['请输入证券代码：']) + '\n')
        date = input(tabulate(['请输入日期：']) + '\n')

        if not stock_code or not date:
            print('股票代码或日期为空，请重新输入！')
            continue

        try:
            date = parse_date_string(date)
        except:
            print('日期输入错误，请重试！')
            continue

        try:
            ann = get_announcement_list(stock_code, date)
        except:
            print('因网络、参数等出现异常，请重试')
            continue

        if not ann:
            print('当天没有公告，请重试')
            continue

        break
    open_pdf(ann)


print(tabulate([['巨潮资讯网上市公司公告'], ['http://www.cninfo.com.cn'],
                ['by 陈维杰']], tablefmt='grid', stralign='center'))
print(tabulate([
    ['提示：'],
    ['接受三种频率的日期：2017（年），2017-12（月），2017-12-31（日）'],
    ['可以输入单个日期，也可以输入日期区间（以英文逗号分隔）'],
    ['例如：'], ['2008'], ['2008-05'], ['2008-05-01'], ['2008-05-01, 2008-05-31'],
    ['2008-04, 2008-05-31'], ['2007, 2008-05-31']]))
while True:
    main_event()
