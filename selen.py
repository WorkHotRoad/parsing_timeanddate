from requests_html import HTMLSession
import re
import pickle
from datetime import datetime

from auth import BASE_DIR, get_cookies
from utils import (
    log_text, log_error,
    get_times_list, format_time,
    format_date, add_data,
    MAIN_URL
)


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

def main():
    try:
        with open("cookies", 'rb') as f:
            cookies = pickle.load(f)
            print('Launching the parser')
    except FileNotFoundError:
        print(f"отсутсвует файл cookies, запускаем selenium")
        cookies = get_cookies()
        print('Launching the parser')

    # создаем сессию
    asession = HTMLSession()
    # добавляем cookies в сессию
    for cookie in cookies:
        asession.cookies.set(cookie['name'], cookie['value'])

    start_time = datetime.now()
    for number in range(1, 10):
        result = []
        response = asession.get(MAIN_URL, params = {"n":number})
        # если нет ответа останавливаем
        if response is None:
            log_error()
            break
        # получаем url города
        url = response.html.url
        # забираем имя города, страны,
        pattern_for_plaсe = r"Time Zone in (.+)"
        table = response.html.xpath(
                    '//h1[@class="headline-banner__title"]/text()'
                )
        place = re.search(
            pattern_for_plaсe, " ".join(table).replace(", ", "_")
        ).group(1)
        # создаем директорию для файлов
        results_dir = BASE_DIR/'results'
        results_dir.mkdir(parents=True, exist_ok=True)

        if 'time zone' not in place.lower():
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
                if len(result) <2 :
                    log_text(
                        number, "нашли только 1но изменение, проверьте"
                    )
            else:
                log_text(number, "не нашли изменений")
                result += ["No changes"]
        else:
            log_text(number, r"страница 'Time Zone' или 'Military Time'")
            result += ["No changes"]
        # сохраняем в фаил
        num_for_file = format(number, '0>4n')
        file_path = f"{results_dir}/{num_for_file}_{place}.txt"
        with open(file_path, "w") as f:
            f.writelines(x+"\n" for x in result)

    print("парсер закончил работу")
    print("Проверьте log_file")
    print(datetime.now() - start_time )


if __name__=="__main__":
    main()
