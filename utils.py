import logging
import re
from urllib.parse import urljoin
from pathlib import Path
from unidecode import unidecode
import os

MAIN_URL = "http://www.timeanddate.com/worldclock/timezone.html"
URL_FOR_LOGIN = "https://www.timeanddate.com/custom/login.html"
BASE_DIR = Path(__file__).parent

results_dir_correct = BASE_DIR/'results'/'correct'
results_dir_correct.mkdir(parents=True, exist_ok=True)
results_dir_without_data = BASE_DIR/'results'/'without_data'
results_dir_without_data.mkdir(parents=True, exist_ok=True)
results_dir_time_zone_or_military_time = BASE_DIR / \
    'results'/'time_zone_or_military_time'
results_dir_time_zone_or_military_time.mkdir(parents=True, exist_ok=True)


def len_files_in_dirs():
    files_1 = len(os.listdir(path=results_dir_correct))
    loog_done(files_1, "correct")
    files_2 = len(
        os.listdir(path=results_dir_without_data)
    )
    loog_done(files_2, "without_data")
    files_3 = len(
        os.listdir(path=results_dir_time_zone_or_military_time)
    )
    loog_done(files_3, "time_zone_or_military_time")
    all_files = files_1 + files_2 + files_3
    logging.info(f"Общее кол-во файлов: {all_files}")



def format_name(place, number):
    repl_simv = (" ", '"', "__")
    place = unidecode(place)
    num_for_file = format(number, '0>4n')
    name_file = f'{num_for_file}_{place}'
    for i in repl_simv:
        name_file =  name_file.replace(i, "_")
    return name_file


logging.basicConfig(
    handlers=[
        logging.FileHandler(
            filename="./log_file.txt",
            encoding='utf-8',
            mode='a+'
        )
    ], level=logging.INFO
)


def save_file(file_path, result, number):
    try:
        with open(file_path, "w") as f:
            f.writelines(x+"\n" for x in result)
    except:
        log_text(number, " - Ошибка записи файла")

def loog_done(num, dir):
    logging.info(f"в папке {dir} - {num} файлов")

def log_text(number, text):
    n = f'?n={number}'
    url_num = urljoin(MAIN_URL, n)
    logging.warning(f"{text}: {url_num}")


def log_error(num):
    logging.error(f"Нет доступа к сайту c городом{num}")


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
    hh, * mm = time.split(":")
    if len(hh) < 2:
        hh = "0"+hh
    if mm:
        if len(mm) > 1:
            mm, ss = mm
        else:
            mm = "".join(mm)
    else:
        mm = "00"
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
        text = (" ".join(text))
        # выбираем все года, где нет изменений
        pattern = r'(\d{4}|\d{4}\s\—\s\d{4}).{,30}UTC '\
            '([\+\-]\d{,2}\:{,1}\d{,2}\:{,1}\d{,2}).{,1}h'
        result1 = re.findall(pattern, text)
        # выбираем все года, где есть изменения
        pattern = r'(\d{8}.\d{4}).{,50}'\
            '([\+\-]\d{,2}\:{,1}\d{,2}\:{,1}\d{,2}).{,1}h'
        result2 = re.findall(pattern, text)
        res += result2 + result1
    return res
