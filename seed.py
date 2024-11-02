from datetime import datetime
import faker
from random import randint, choice
import sqlite3

NUMBER_USERS = 30
NUMBER_TITLES = 10

def generate_fake_data(number_fullname, number_email, number_title, number_description) -> tuple:
    fake_data = faker.Faker()
    
    # Згенеруємо список повних імен
    fullnames = [fake_data.name() for _ in range(number_fullname)]
    
    # Згенеруємо список унікальних email
    emails = [fake_data.unique.email() for _ in range(number_email)]
    
    # Згенеруємо список назв завдань
    titles = [fake_data.sentence(nb_words=5) for _ in range(number_title)]
    
    # Згенеруємо список описів завдань
    descriptions = [fake_data.text(max_nb_chars=200) for _ in range(number_description)]
    
    return fullnames, emails, titles, descriptions

def prepare_data(fullnames, emails, titles, descriptions) -> tuple:
    # Дані для таблиці users
    for_users = []
    for i in range(len(fullnames)):
        for_users.append((fullnames[i], emails[i]))
    
    # Дані для таблиці status
    statuses = [('new',), ('in progress',), ('completed',)]
    
    # Дані для таблиці tasks
    for_tasks = []
    for j in range(len(titles)):
        title = titles[j]
        description = descriptions[j]
        status_id = randint(1, len(statuses))  # Випадковий статус
        user_id = randint(1, NUMBER_USERS)     # Випадковий користувач
        for_tasks.append((title, description, status_id, user_id))
    
    return for_users, statuses, for_tasks

def insert_data_to_db(users, statuses, tasks) -> None:
    with sqlite3.connect('test.db') as con:
        cur = con.cursor()
        
        # Вставка даних в таблицю users
        sql_to_users = """INSERT INTO users(fullname, email)
                          VALUES (?, ?)"""
        cur.executemany(sql_to_users, users)
        
        # Вставка даних в таблицю status
        sql_to_status = """INSERT INTO status(name)
                           VALUES (?)"""
        cur.executemany(sql_to_status, statuses)
        
        # Вставка даних в таблицю tasks
        sql_to_tasks = """INSERT INTO tasks(title, description, status_id, user_id)
                          VALUES (?, ?, ?, ?)"""
        cur.executemany(sql_to_tasks, tasks)
        
        con.commit()

if __name__ == "__main__":
    # Генерація фейкових даних
    fullnames, emails, titles, descriptions = generate_fake_data(NUMBER_USERS, NUMBER_USERS, NUMBER_TITLES, NUMBER_TITLES)
    
    # Підготовка даних для вставки у БД
    users, statuses, tasks = prepare_data(fullnames, emails, titles, descriptions)
    
    # Вставка даних в БД
    insert_data_to_db(users, statuses, tasks)
