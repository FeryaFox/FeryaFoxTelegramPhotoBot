from sqlighter import SQLighter
db = SQLighter()
admin_id = input('Введите telegram_id админа: ')
db.add_admin(admin_id)