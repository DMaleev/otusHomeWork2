import requests
from datetime import datetime, timedelta
import pymorphy2
import collections
from terminaltables import AsciiTable

from bs4 import BeautifulSoup

morph = pymorphy2.MorphAnalyzer()

def date_checker(date):
    if "сегодня" in date:
        post_date = datetime.now().date()
    elif "вчера" in date:
        post_date = datetime.now().date() - timedelta(days=1)
    else:
        day = date[:2]
        mounthes = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
                    'ноября', 'декабря']
        mounth = mounthes.index(date.split()[1]) + 1
        post_date = datetime.strptime(str(day) + str(mounth) + "2018", '%d%m%Y').date()

    first_week_day = post_date - timedelta(post_date.weekday())
    last_week_day = first_week_day - timedelta(days=6)
    return str(first_week_day) + " - " + str(last_week_day)

try:
    page = int(input("С какой страницы парсить?"))
    page_end = int(input("По какую?"))
except(Exception):
    print("Неверно введены даныне")
    exit(1)
result = {}
for page_number in range(page, page_end):
    print('Парсим {0} страницу'.format(page_number))
    r = requests.get('https://habr.com/all/page{0}'.format(page_number))
    soup = BeautifulSoup(r.text, 'html.parser')
    for post in soup.find_all("li", {"class": "content-list__item_post"}):
        try:
            post_week = date_checker(post.find("span", class_="post__time").text)
            if not post_week in result:
                result.setdefault(post_week, [])
            for title_word in post.find("a", class_="post__title_link").text.split():
                word_analyzer = morph.parse(title_word)[0]
                if word_analyzer.tag.POS == 'NOUN':
                    result[post_week].append(word_analyzer.normal_form)
        except Exception:
            pass
table_data = [
    ['Дата', 'Ключевые слова'],
]
for key, value in result.items():
    table_data.append([key, str(collections.Counter(result[key]).most_common(3))])

table = AsciiTable(table_data)
print(table.table)