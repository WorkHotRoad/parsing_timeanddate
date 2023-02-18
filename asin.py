from requests_html import AsyncHTMLSession
from auth import BASE_DIR, get_cookies
import re, pickle, asyncio, os
from datetime import datetime
from utils import log_text, log_error, get_times_list, format_time, format_date, MAIN_URL


async def parse(asession, number):
    result = []
    response = await asession.get(MAIN_URL, params = {"n":number})
    # получаем url города
    url = response.html.url
    # забираем имя города, страны,
    pattern_for_plase = r"Time Zone in (.+)"
    place = re.search(
        pattern_for_plase,
        " ".join(
            response.html.xpath(
                '//h1[@class="headline-banner__title"]/text()'
            )
        ).replace(", ", "_")
    ).group(1)
    # создаем директорию для файлов
    results_dir = BASE_DIR/'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    # получаем все временные промежутки
    times_list = get_times_list(response)
    # получаем данные с нужными годами со и сортируем и форматируем их
    res = []
    for i in times_list:
        response = await asession.get(url+"?syear="+i)
        text = response.html.xpath(
            '//table[@id="tb-zone"]/tbody/tr/descendant-or-self::*/text()'
        )
        text =(" ".join(text))
        pattern = r'(\d{4}|\d{4}\s\—\s\d{4}).{5,30}UTC ([\+\-]\d.{0,7}).{0,1}h'
        result1 = re.findall(pattern, text)
        pattern = r'(\d{8}.\d{4}).{5,50}UTC([\+\-]\d.{0,7})h'
        result2 = re.findall(pattern, text)
        res += result1 + result2
    sort_res = sorted(
        [[format_date(x[0]), format_time(x[1])] for x in res],
        key = lambda x: x[0]
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
        result[0] = "No changes"
        print(f'No changes in {number}')
    # сохраняем в фаил
    num_for_file = format(number, '0>4n')
    file_path = f"{results_dir}/{num_for_file}_{place}.txt"
    with open(file_path, "w") as f:
        f.writelines(x+"\n" for x in result)

async def main():
    # берем cookies
    try:
        with open("cookies", 'rb') as f:
            cookies = pickle.load(f)
            print('Launching the parser')
    except FileNotFoundError:
        print(f"отсутсвует файл cookies, запускаем selenium")
        cookies = get_cookies()
        print('Launching the parser')
    # создаем сессию
    asession = AsyncHTMLSession()
    # добавляем cookies в сессию
    for cookie in cookies:
        asession.cookies.set(cookie['name'], cookie['value'])
    # 5959
    # нужно сделать проверку на корректные куки, если нет - get_cookies()
    # resalt = asession.get()
    tasks = (parse(asession, number) for number in range(166, 167))
    await asyncio.gather(*tasks)


if __name__=="__main__":
    start_time = datetime.now()
    asyncio.run(main())
    files = os.listdir(path=f"{BASE_DIR}\\results")
    print(f'the working time of the parser is {datetime.now() - start_time}')
    print(len(files))
