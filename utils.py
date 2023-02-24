import logging
import re
from urllib.parse import urljoin

MAIN_URL = "http://www.timeanddate.com/worldclock/timezone.html"
URL_FOR_LOGIN = "https://www.timeanddate.com/custom/login.html"


logging.basicConfig(
        handlers=[
            logging.FileHandler(
                filename="./log_file.txt",
                encoding='utf-8',
                mode='a+'
            )
        ], level=logging.WARNING
    )

def log_text(number, text):
    n = f'?n={number}'
    url_num = urljoin(MAIN_URL, n)
    logging.warning(f"{text}: {url_num}")

def log_error():
    logging.error("Нет доступа к сайту")

def get_times_list(response):
    """функция возвращает начало временных промежутков"""
    times = response.html.xpath(
        '//select[@id="tb-zone-select"]/option/@value'
    )[1:]
    return [str(x).split("-")[0] for x in times]

def format_time(time):
    """функция фолрматирования даты"""
    hh = mm = ss = '00'
    sign = time[0]
    time = time[1:]
    hh,* mm = time.split(":")
    if len(hh)<2:
        hh = "0"+hh
    if mm:
        if len(mm)>1:
            mm, ss = mm
        else:
            mm = "".join(mm)
    else: mm = "00"
    return sign+hh+mm+ss

def format_date(date):
    if "T" in date:
        return date.replace("T", "")+"00"
    date = date.split(' — ')
    return date[0]+"0000000000"

def add_data(url, times_list, session):
    res = []
    for i in times_list:
        response = session.get(url+"?syear="+i)
        text = response.html.xpath(
            '//table[@id="tb-zone"]/tbody/tr/descendant-or-self::*/text()'
        )
        text =(" ".join(text))
        #выбираем все года, где нет изменений
        pattern = r'(\d{4}|\d{4}\s\—\s\d{4}).{,30}UTC '\
                    '([\+\-]\d{,2}\:{,1}\d{,2}\:{,1}\d{,2}).{,1}h'
        result1 = re.findall(pattern, text)
        #выбираем все года, где есть изменения
        pattern = r'(\d{8}.\d{4}).{,50}'\
                    '([\+\-]\d{,2}\:{,1}\d{,2}\:{,1}\d{,2}).{,1}h'
        result2 = re.findall(pattern, text)
        res += result2 + result1
    return res
