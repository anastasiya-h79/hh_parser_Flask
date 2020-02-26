import time
import requests
import statistics
import json

def parser(request_text):

    key_skills = {}
    url = 'https://api.hh.ru/vacancies'
    key_skills_list = []
    list_salary = []

    params = {'text': 'NAME:'+request_text}
    result = requests.get(url, params=params).json()
    found = result['found']
    pages = result['pages']

# Пройдемся по каждой странице
    for i in range(1, pages):
        params = {
            'text': 'NAME:'+request_text,
            'page': i
        }

        result = requests.get(url, params=params).json()
        items = result['items']
        found = result['found']

        for item in items:
            result = requests.get(item['url']).json()

        # Собираем данные по зарплате
            if item['salary'] is not None:
                salary = item['salary']['from']
                list_salary.append(salary)
                salary = item['salary']['to']
                list_salary.append(salary)

        # Собираем ключевые навыки
            for res in result['key_skills']:
                key_skills_list.append(res['name'])
            time.sleep(0.1)

# Считаем количество скиллов
    for skill in key_skills_list:
        if skill in key_skills:
            key_skills[skill] += 1
        else:
            key_skills[skill] = 1

    result_vac = sorted(key_skills.items(), key=lambda x: x[1], reverse=True)

    list_salary_to = []
    for i in list_salary:
        if i != None:
            list_salary_to.append(i)

# Вычисляем среднюю зарплату
    list_salary_mean = int(statistics.mean(list_salary_to))

    request_result = {}  # записвываем результаты в словарь

    request_result['request_text'] = request_text
    request_result['found'] = found
    request_result['list_salary_mean'] = list_salary_mean
    request_result['key_skills'] = result_vac

    return request_result