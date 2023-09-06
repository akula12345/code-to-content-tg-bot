import sqlite3
import random

db = sqlite3.connect('database.db')
sql = db.cursor()


def database_setup():
    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tgId INT
    )
    """)

    sql.execute("""CREATE TABLE IF NOT EXISTS films (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filmCode TEXT,
        filmName TEXT,
        contentType TEXT,
        content TEXT
    )
    """)

    db.commit()
    sql.close()

def get_user(user_id):
    db = sqlite3.connect('database.db')
    sql = db.cursor()
    sql.execute(f"SELECT tgId FROM users WHERE tgId = '{user_id}'")
    if sql.fetchone() is None:
        sql.execute(f'INSERT INTO users(tgId) VALUES (?)', (user_id,))
        db.commit()
        sql.close()
    else:
        sql.close()

def get_users():
    db = sqlite3.connect('database.db')
    sql = db.cursor()
    users = []
    for i in sql.execute("SELECT tgId FROM users"):
        users += i
    sql.close()
    amount_users = f'Всього користувачів🧍‍♀🧍‍♂: {len(users)}'
    return amount_users, users

def add_new_film(film_name, contentType, content):
    db = sqlite3.connect('database.db')
    sql = db.cursor()

    filmCode = ''
    for x in range(6):
        filmCode = filmCode + random.choice(list('1234567890')) 

    numbers_film = []
    for i in sql.execute(f"SELECT filmCode FROM films WHERE filmCode = '{filmCode}'"):
        numbers_film += i

    if len(numbers_film) > 0:
        sql.close()
        return 0
		   
    sql.execute(f'INSERT INTO films(filmCode, filmName, contentType, content) VALUES (?, ?, ?, ?)', (filmCode, film_name, contentType, content))
    db.commit()
    sql.close()

    return 1

def delete_film(film_code):
    db = sqlite3.connect('database.db')
    sql = db.cursor()
			
    numbers_film = []
    for i in sql.execute(f"SELECT * FROM films WHERE filmCode = '{film_code}'"):
        numbers_film += i
    sql.close()
			
    if len(numbers_film) == 0:
        return 0
			
    db = sqlite3.connect('database.db')
    sql = db.cursor()
    sql.execute(f"DELETE FROM films WHERE filmCode = '{film_code}'")
    db.commit()
    sql.close()

    return 1

def get_films():
    db = sqlite3.connect('database.db')
    sql = db.cursor()
    films = []
    for i in sql.execute("SELECT filmCode FROM films"):
        films += i
    sql.close()

    return films

def get_film_by_code(filmCode):
    db = sqlite3.connect('database.db')
    sql = db.cursor()

    film = []
    for i in sql.execute(f"SELECT * FROM films WHERE filmCode = '{filmCode}'"):
        film += i
    sql.close()

    if len(film) == 0:
        return 0
    return film