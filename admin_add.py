from sqlighter import SQLighter
db = SQLighter('bot.db')
admin_id = input('Введите telegram_id админа: ')
db.add_admin(admin_id)