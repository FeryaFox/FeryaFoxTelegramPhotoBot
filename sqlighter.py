import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "admin" ("telegram_id"	INTEGER);')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "category"(name STRING,description STRING)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "photo"(telegram_id INTEGER,photo_time INTEGER,file_id TEXT,photo_type TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS "user"(telegram_id INTEGER,username TEXT,first_name TEXT,last_name TEXT)')

    def user_exists(self, message):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM user WHERE `telegram_id` = ?',
                                         (message['from']['id'],)).fetchall()
            return bool(len(result))

    def add_user(self, message):

        with self.connection:
            data_tuple = (message['from']['id'], message['from']['username'], message['from']['first_name'],
                          message['from']['last_name'])
            return self.cursor.execute(
                "INSERT INTO user (telegram_id, username, first_name,  last_name) VALUES (?, ?, ?, ?)",
                data_tuple)

    def update_user(self, message):
        with self.connection:
            return self.cursor.execute(
                "UPDATE user SET `username` = ?, first_name = ?, last_name = ? WHERE `telegram_id` = ?", (
                    message['from']['username'], message['from']['first_name'], message['from']['last_name'],
                    message['from']['id']))

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
            self.cursor.execute('insert into photo (telegram_id, photo_time, file_id, photo_type) values (?, ?, ?, ?)',
                                (message['from']['id'],
                                 message['date'],
                                 message['photo'][-1]['file_id'],
                                 photo_type,))

    def add_picture_typo(self, author_id, time_a, id_photo, photo_type):
        with self.connection:
            self.cursor.execute('insert into photo (telegram_id, photo_time, file_id, photo_type) values (?, ?, ?, ?)',
                                (author_id,
                                 time_a,
                                 id_photo,
                                 photo_type,))

    def get_random_picture(self, type_photo, count):
        with self.connection:
            print(type_photo,count)
            sql_fetch_blob_query = f"""SELECT * FROM photo WHERE photo_type = ? and file_id IS NOT NULL ORDER BY 
            random() LIMIT {count}; """
            r = self.cursor.execute(sql_fetch_blob_query, (type_photo,)).fetchall()
            return r

    def check_admin(self, message):
        with self.connection:

            data = self.cursor.execute("SELECT * FROM admin WHERE telegram_id = ?", (message['from']['id'],)).fetchall()

        if data:
            return True
        else:
            return False

    def get_category(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM category').fetchall()

    def add_category(self, name, des):
        with self.connection:
            self.cursor.execute('INSERT INTO category (name, description) values (?, ?)', (name, des))

    def get_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM a_art').fetchall()

    def check_category(self, name):
        with self.connection:
            return self.cursor.execute('SELECT * FROM photo WHERE photo_type = ? LIMIT 1', (name,)).fetchall() != []

    def add_admin(self, telegram_id):
        with self.connection:
            return self.cursor.execute('INSERT INTO admin (telegram_id) values (?)', (telegram_id,))
