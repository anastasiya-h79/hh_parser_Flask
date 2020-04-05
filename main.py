from sqlalchemy import Column, Integer, TEXT, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request
import requests
import statistics
import time

engine = create_engine( 'sqlite:///hh_orm.sqlite', echo=True )

Base = declarative_base()


class Skill(Base):
    __tablename__ = 'hh_key_skills'
    id = Column(Integer, primary_key=True)
    name = Column(TEXT)
    quality = Column(Integer)

    def __init__(self, name, quality):
        self.name = name
        self.quality = quality


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contacts/')
def contacts():
    developer_name = 'https://github.com/anastasiya-h79/'
    return render_template('contacts.html', name=developer_name)


@app.route('/request/', methods=['GET'])
def request_get():
    return render_template('request.html')


@app.route('/results/', methods=['POST'])
def run_post_vacancy():
    name = request.form['vacancy']
    area = request.form['area']
    key_skills = {}
    url = 'https://api.hh.ru/vacancies'
    key_skills_list = []
    list_salary = []

    params = {'text': f'NAME:({name}) AND {area}'}

    result = requests.get(url, params=params).json()
    found = result['found']
    pages = result['pages']

    # Пройдемся по каждой странице
    for i in range(1, pages):
        params = {'text': f'NAME:({name}) AND {area}', 'page': i}

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
    session = Session()
    for skill in result_vac:
        hh_key_skills = Skill(skill[0], skill[1])
        session.add(hh_key_skills)
    session.commit()

    list_salary_to = []
    for i in list_salary:
        if i != None:
            list_salary_to.append(i)

    # Вычисляем среднюю зарплату
    list_salary_mean = int(statistics.mean(list_salary_to ))

    result_database = []
    hh_key_skills_query = session.query(Skill).all()
    for key_skills in hh_key_skills_query:
        result_database.append([key_skills.name, key_skills.quality])

    request_result = {}

    request_result['name'] = name
    request_result['area'] = area
    request_result['found'] = found
    request_result['list_salary_mean'] = list_salary_mean
    request_result['key_skills'] = result_vac

    return render_template('results.html', data=result_database, request_result=request_result)


app.run(debug=True)