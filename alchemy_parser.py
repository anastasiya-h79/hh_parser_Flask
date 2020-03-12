import time
import requests
import statistics
import json
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def parser_alchemy(name, area):
    engine = create_engine('sqlite:///alchemyparser.sqlite', echo=False)

    Base = declarative_base()

    # vacancyskill = Table('vacancyskill', Base.metadata,
    #                      Column('id', Integer, primary_key=True),
    #                      Column('vacancy_id', Integer, ForeignKey('vacancy.id')),
    #                      Column('skill_id', Integer, ForeignKey('skill.id'))
    #                      )

    class Skills(Base):
        __tablename__ = 'skill'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

        def __init__(self, name):
            self.name = name

        # def __str__(self):
        #     return self.name

    class Region(Base):
        __tablename__ = 'region'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        #number = Column(Integer, nullable=True)

        def __init__(self, name):
            self.name = name
            #self.number = number

        # def __str__(self):
        #     return f'{self.id}) {self.name}: {self.number}'


    class Vacancy(Base):
        __tablename__ = 'vacancy'
        id = Column(Integer, primary_key=True)
        area = Column(Integer, ForeignKey('region.id'))

        #list_salary_mean = Column(Integer, ForeignKey('list_salary_mean.id'))
        name = Column(String)
        found = Column(Integer)

    class Skill_req(Base):
        __tablename__ = 'skill_req'
        id = Column(Integer, primary_key=True)
        skills = Column(String, ForeignKey('skill.id'))
        vacancy = Column(String, ForeignKey('vacancy.id'))
        skill_num = Column(Integer)
        #skill_percent = Column(NUMERIC)

    # Создание таблицы
    Base.metadata.create_all(engine)

    # Заполняем таблицы
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()



    key_skills = {}
    url = 'https://api.hh.ru/vacancies'
    key_skills_list = []
    list_salary = []


    params = {'text': f'NAME:({name}) AND {area}'}

    result = requests.get(url, params=params).json()
    found = result['found']
    pages = result['pages']


    area = Region(params.values[1])
    if session.query(Region).filter(Region.name == params.values[1]).count() == 0: session.add(params.values[1])
    session.commit()


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
                skill = Skills(res['name'])
                if session.query(Skills).filter(Skills.name == res['name']).count() == 0: session.add(skill)
            session.commit()
            time.sleep(0.1)



    # Считаем количество скиллов
    for skill in key_skills_list:
        if skill in key_skills:
            key_skills[skill] += 1
        else:
            key_skills[skill] = 1
        skills_req = Skill_req()
        skills_req.skills = session.query(Skills).filter(Skills.name == skill).first().id
        session.add(skills_req)
        session.commit()

    result_vac = sorted(key_skills.items(), key=lambda x: x[1], reverse=True)

    list_salary_to = []
    for i in list_salary:
        if i != None:
            list_salary_to.append(i)

    # Вычисляем среднюю зарплату
    list_salary_mean = int(statistics.mean(list_salary_to))

    vacancy = Vacancy()
    vacancy.area = session.query(Region).filter(Region.name == params['area']).first().id
    #vacancy.list_salary_mean = session.query(Salary).filter(Salary.name == params['employment']).first().id
    vacancy.name = params['name']
    vacancy.found = found
    session.add(vacancy)
    session.commit()

    # Записвываем результаты в словарь
    request_result = {}

    request_result['name'] = name
    request_result['area'] = area
    request_result['found'] = found
    request_result['list_salary_mean'] = list_salary_mean
    request_result['key_skills'] = result_vac

    last_ses_id = session.query(Vacancy).order_by(Vacancy.id.desc()).first().id

    all_vac = session.query(Vacancy).order_by(Vacancy.id.desc()).first().found

    all_skills_from_orm = []
    for i in session.query(Skill_req, Skills).filter(Skill_req.skills == Skills.id,
                                                     Skill_req.request == last_ses_id).order_by(Skill_req.skill_num.asc()).all():
        all_skills_from_orm.append([i[1].name, i[0].skill_num])

    session.close()

    return all_vac, all_skills_from_orm, request_result
