#import os
import psycopg2
import datetime

class SQLighter:

    def __init__(self):
        #DATABASE_URL = os.environ['DATABASE_URL']
        #self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.connection = psycopg2.connect(user='postgres', host='localhost', port=7777)

        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "admin" ("telegram_id"	INTEGER);')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "category" (name TEXT, description TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "photo"(telegram_id INTEGER,photo_time INTEGER,file_id TEXT,photo_type TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "user_telegram" (telegram_id INTEGER,username TEXT,first_name TEXT,last_name TEXT)')

    def user_exists(self, message):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            self.cursor.execute('SELECT * FROM user_telegram WHERE telegram_id = %s',
                                (message['from']['id'],))
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_user(self, message):

        with self.connection:
            data_tuple = (message['from']['id'], message['from']['username'], message['from']['first_name'],
                          message['from']['last_name'])
            return self.cursor.execute(
                "INSERT INTO user_telegram (telegram_id, username, first_name,  last_name) VALUES (%s, %s, %s, %s)",
                data_tuple)

    def update_user(self, message):
        with self.connection:
            return self.cursor.execute(
                "UPDATE user_telegram SET username = %s, first_name = %s, last_name = %s WHERE telegram_id = %s", (
                    message['from']['username'], message['from']['first_name'], message['from']['last_name'],
                    message['from']['id'],))

    def check_user(self, message):
        if not self.user_exists(message):
            # если юзера нет в базе, добавляем его
            self.add_user(message)
        else:
            # если он уже есть, то просто обновляем ему статус подписки
            self.update_user(message)

    def add_picture(self, message, photo_type):
        self.check_user(message)
        with self.connection:
            time = int(datetime.datetime.strptime('2019-12-24 04:00:00', '%Y-%m-%d %H:%M:%S').timestamp())

            self.cursor.execute('insert into photo (telegram_id, photo_time, file_id, photo_type) values (%s, %s, %s, %s)',
                                (message['from']['id'],
                                 time,
                                 message['photo'][-1]['file_id'],
                                 photo_type,))

    def add_picture_typo(self, author_id, time_a, id_photo, photo_type):
        with self.connection:
            self.cursor.execute('insert into photo (telegram_id, photo_time, file_id, photo_type) values (%s, %s, %s, %s)',
                                (author_id,
                                 time_a,
                                 id_photo,
                                 photo_type,))

    def get_random_picture(self, type_photo, count):
        with self.connection:
            print(type_photo,count)
            sql_fetch_blob_query = f"""SELECT * FROM photo WHERE photo_type = %s and file_id IS NOT NULL ORDER BY 
            random() LIMIT {count}; """
            self.cursor.execute(sql_fetch_blob_query, (type_photo,))
            return self.cursor.fetchall()

    def check_admin(self, message):
        with self.connection:
            self.cursor.execute("SELECT * FROM admin WHERE telegram_id = %s", (message['from']['id'],))
            data = self.cursor.fetchall()

        if data:
            return True
        else:
            return False

    def get_category(self):
        with self.connection:
            self.cursor.execute('SELECT * FROM category')
            return self.cursor.fetchall()

    def add_category(self, name, des):
        with self.connection:
            self.cursor.execute('INSERT INTO category (name, description) values (%s, %s)', (name, des))

    def get_all(self):
        with self.connection:
            self.cursor.execute('SELECT * FROM a_art')
            return self.cursor.fetchall()

    def check_category(self, name):
        with self.connection:
            self.cursor.execute('SELECT * FROM category WHERE name = %s', (name,))
            return self.cursor.fetchall() != []

    def add_admin(self, telegram_id):
        with self.connection:
            return self.cursor.execute('INSERT INTO admin (telegram_id) values (%s)', (telegram_id,))
