import logging
from urllib.parse import urljoin

MAIN_URL = "http://www.timeanddate.com/worldclock/timezone.html"

logging.basicConfig(
        handlers=[
            logging.FileHandler(
                filename="./log_file.txt", 
                encoding='utf-8', 
                mode='w'
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