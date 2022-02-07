import sqlite3
import psycopg2
import os

#DATABASE_URL = '127.0.0.1'
#con_p = psycopg2.connect(user='postgres', host='localhost', port=5432)
DATABASE_URL = os.environ['DATABASE_URL']
con_p = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor_p = con_p.cursor()

connection = sqlite3.connect('../bot.db')
cursor_sql = connection.cursor()

'''
print(cursor_p.execute('SELECT * FROM admin'))
print(cursor_p.fetchall())
cursor_p.execute('INSERT INTO "public"."admin" (telegram_id) VALUES (5)')
con_p.commit()
'''

def port():
    cursor_p.execute('CREATE TABLE IF NOT EXISTS "admin" ("telegram_id"	INTEGER);')
    d = cursor_sql.execute('SELECT * FROM admin ').fetchall()
    for i in d:
        cursor_p.execute("""INSERT INTO admin (telegram_id) 
                                VALUES ({})""".format(i[0]))

    cursor_p.execute('CREATE TABLE IF NOT EXISTS "category" (name TEXT, description TEXT)')
    d = cursor_sql.execute('SELECT * FROM category ').fetchall()
    for i in d:
        cursor_p.execute("INSERT INTO category (name, description) " + "VALUES (%s, %s)", (i[0], i[1]))

    cursor_p.execute('CREATE TABLE IF NOT EXISTS "photo"(telegram_id INTEGER, photo_time INTEGER, file_id TEXT, photo_type TEXT)')
    d = cursor_sql.execute('SELECT * FROM photo ').fetchall()
    print(len(d[0]))
    for i in d:
        cursor_p.execute("INSERT INTO photo (telegram_id, photo_time, file_id, photo_type) " + "VALUES (%s, %s, %s, %s)", (i[0], i[1], i[2], i[3]))

    cursor_p.execute('CREATE TABLE IF NOT EXISTS "user_telegram" (telegram_id INTEGER,username TEXT,first_name TEXT,last_name TEXT)')
    d = cursor_sql.execute('SELECT * FROM user ').fetchall()
    print(len(d[0]))
    for i in d:
        cursor_p.execute(
            "INSERT INTO user_telegram (telegram_id, username, first_name, last_name) " + "VALUES (%s, %s, %s, %s)",
            (i[0], i[1], i[2], i[3]))
        #cursor_p.execute("INSERT INTO user (telegram_id, username, first_name, last_name) " + "VALUES (%s, %s, %s, %s)", (i[0], i[1], i[2], i[3]))

    con_p.commit()
port()
#print(cursor_p.execute('SELECT * FROM admin ').fetchall())
