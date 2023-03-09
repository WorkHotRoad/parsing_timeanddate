from requests_html import HTMLSession
import re
import pickle
from datetime import datetime

import os

from auth import get_cookies
from utils import (
    log_text, log_error, get_times_list,
    format_time, format_date, add_data,
    save_file, MAIN_URL, format_name,
    len_files_in_dirs,
    results_dir_correct,
    results_dir_without_data,
    results_dir_time_zone_or_military_time
)


def main():
    try:
        with open("cookies", 'rb') as f:
            cookies = pickle.load(f)
            print('Launching the parser')
    except FileNotFoundError:
        print(f"отсутсвует файл cookies, запускаем selenium")
        cookies = get_cookies()
        print('Launching the parser')
    asession = HTMLSession()  # создаем сессию
    # добавляем cookies в сессию
    for cookie in cookies:
        asession.cookies.set(cookie['name'], cookie['value'])
    start_time = datetime.now()  # подключаем счетчик времени

    for number in range(1, 5960):
        print(f"парсим страницу {number}")
        result = []
        response = asession.get(MAIN_URL, params={"n": number})
        if response is None:
            log_error(number)
            continue
        url = response.html.url  # получаем url города
        # забираем имя города, страны
        pattern_for_plaсe = r"Time Zone in (.+)"
        table = response.html.xpath(
            '//h1[@class="headline-banner__title"]/text()'
        )
        try:
            place = re.search(
                pattern_for_plaсe, " ".join(table).replace(", ", "_")
            ).group(1).replace("/", "_")
        except Exception:
            log_text(number, r"Ошибка при создании имени!, фаил не сохранен")
            continue
        # сощдаем имя файла для записи
        name_file = format_name(place, number)
        if 'time_zone' not in name_file.lower():
            try:
                # получаем все временные промежутки
                times_list = get_times_list(response)
                # получаем данные с нужными годами, сортируем и форматируем их
                res = add_data(url, times_list, asession)
                sort_res = sorted(
                    [[format_date(x[0]), format_time(x[1])] for x in res],
                    key=lambda x: x[0]
                )
                # удаляем дубли и объединяем данные
                if sort_res:
                    ready_data = [sort_res[0]]
                    for i in range(1, len(sort_res)):
                        if ready_data[-1][1] != sort_res[i][1]:
                            ready_data.append(sort_res[i])
                    ready_data = ["|".join(x) for x in ready_data]
                    result += ready_data
                else:
                    log_text(number, "не нашли изменений")
                    file_path = f"{results_dir_without_data}/{name_file}.txt"
                    save_file(file_path, result, number)
                    continue
            except Exception:
                log_text(number, r"Не стандартная страница")
                continue
        else:
            log_text(number, r"страница 'Time Zone' или 'Military Time'")
            file_path = f"{results_dir_time_zone_or_military_time}/{name_file}.txt"
            save_file(file_path, result, number)
            continue
        file_path = f"{results_dir_correct}\{name_file}.txt"
        save_file(file_path, result, number)


    len_files_in_dirs()
    print("парсер закончил работу")
    print("Проверьте log_file")
    print(datetime.now() - start_time)
    os.system("pause")

if __name__ == "__main__":
    main()
