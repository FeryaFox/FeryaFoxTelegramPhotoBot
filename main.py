from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import logging
from sqlighter import SQLighter
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InputMediaPhoto

logging.basicConfig(level=logging.INFO)

memory_storage = MemoryStorage()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=memory_storage)
db = SQLighter('bot.db')


class Keyboard:
    add_category = KeyboardButton('Добавить категорию')
    del_category = KeyboardButton('Удалить категорию')
    exit_admin_all = KeyboardButton('Выйти из админки')
    exit_admin = KeyboardButton('Выйти в окно')
    category_list = KeyboardButton('Список категорий')
    update = KeyboardButton('Отправить')
    try_again = KeyboardButton('Начать заново')
    add_something = KeyboardButton('Добавить')
    preview = KeyboardButton('Превью')


markup_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(Keyboard.add_category, Keyboard.del_category).row(
    Keyboard.exit_admin_all)


def check_photo(m):
    dd = ''
    if '@' in m.text:


        for i in m.text:
            if i != '@':
                dd += i
            else:
                break
    else:
        dd = m.text

    if len(dd) > 3:
        if dd[0:2] == '/r':
            s = dd.split()[0][3:]
            if s[0] != 'p':
                return True, False, s
            elif s[0] == 'p':
                return True, True, s[2:]
            else:
                return False, False
        else:
            return False, False
    else:
        return False, False


def check_photo_for_add(m):
    if m.text[0:4] == '/add':
        return True
    else:
        return False


class add_photo_state(StatesGroup):
    waiting_for_photo = State()
    waiting_for_photo_type = State()
    waiting_for_photo_id = State()
    waiting_for_photo_name = State()
    waiting_for_photo_username = State()
    waiting_for_photo_time = State()


class admin_menu(StatesGroup):
    waiting_for_command = State()
    waiting_for_add_category = State()
    waiting_for_add_category_2 = State()
    waiting_for_add_category_3 = State()


class photo_state(StatesGroup):
    waiting_for_count = State()
    waiting_for_photo_type = State()
    waiting_for_add_photo_type = State()
    waiting_for_add_photo = State()


@dp.message_handler(commands='r')
async def r(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Отправь имя категории \n Или /category_list для списка категорий')
    await photo_state.waiting_for_photo_type.set()
    await state.update_data(t=True)


@dp.message_handler(lambda message: check_photo_for_add(message))
async def add_photo(message: types.Message, state: FSMContext):
    dd = ''
    if '@' in message.text:

        for i in message.text:
            if i != '@':
                dd += i
            else:
                break
    else:
        dd = message.text

    if len(dd) == 4:
        await bot.send_message(message.chat.id,
                               'Отправь категорию для добавления\n/category_list для полученния списка '
                               'категорий\n/exit для выхода')
        await photo_state.waiting_for_add_photo_type.set()
    else:
        await photo_state.waiting_for_add_photo.set()
        d = dd[5:]
        await state.update_data(photo_type=d.lower())
        await bot.send_message(message.chat.id, 'Отправь картинку для добавления')


@dp.message_handler(state=photo_state.waiting_for_add_photo_type, content_types=types.ContentTypes.TEXT)
async def add_photo_waiting_type(message: types.Message, state: FSMContext):
    if '/exit' in message.text:
        await bot.send_message(message.chat.id, 'Вышел')
        await state.finish()
    elif '/category_list' in message.text:
        list_cat = db.get_category()
        to_send = 'Список категорий\n'
        for i in list_cat:
            to_send += f'{i[0]} - {i[1]}\n'
        await bot.send_message(message.from_user.id, to_send)
    else:
        if db.check_category(message.text):
            await state.update_data(photo_type=message.text.lower())
            await bot.send_message(message.chat.id, 'Пришли фото')
            await photo_state.waiting_for_add_photo.set()

        else:
            await bot.send_message(message.chat.id, 'Данной категории нет')


@dp.message_handler(lambda message: check_photo(message)[0])
async def rand_photo(message: types.Message, state: FSMContext):
    r = check_photo(message)
    if db.check_category(r[2]):
        if not check_photo(message)[1]:
            await bot.send_photo(message.chat.id, db.get_random_picture(r[2], 1)[0][2])
        elif check_photo(message)[1]:
            count = message.text.split()
            if len(count) > 1 and count[1].isdigit():
                if int(count[1]) <= 10 and count[1] != 0:
                    photo = db.get_random_picture(r[2], count[1])
                    media = []
                    for photo_id in photo:
                        media.append(InputMediaPhoto(photo_id[2]))
                    await bot.send_media_group(message.chat.id, media)
                else:
                    await bot.send_message(message.chat.id,
                                           f'Ты отправил не верное количество фото для вывода надо отправить от 1 до '
                                           f'10, а ты отправил {count[1]}')
            else:
                await photo_state.waiting_for_count.set()
                await bot.send_message(message.chat.id, 'Отправь количество для вывода')
                await state.update_data(photo_type=r[2].lower())
    elif message.text[:4] == '/r_p' and (len(message.text) == 4 or message.text[4] == '@'):
        await photo_state.waiting_for_photo_type.set()
        await state.update_data(t=False)
        await bot.send_message(message.chat.id, 'Пришли навание категории')
    else:
        await bot.send_message(message.chat.id,
                               f'Категория {r[2]} не найдена. Введите /category_list для полученния списка категорий')


@dp.message_handler(state=photo_state.waiting_for_count, content_types=types.ContentTypes.TEXT)
async def rand_photo_2(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) <= 10 and int(message.text) != 0:
            photo_type = await state.get_data()
            photo = db.get_random_picture(photo_type['photo_type'], int(message.text))
            media = []
            for photo_id in photo:
                media.append(InputMediaPhoto(photo_id[2]))
            await bot.send_media_group(message.chat.id, media)
            await state.finish()
        else:
            await bot.send_message(message.chat.id,
                                   f'Ты отправил не верное количество фото для вывода надо отправить от 1 до 10, '
                                   f'а ты отправил {message.text}')
            await state.finish()
    else:
        await bot.send_message(message.chat.id, 'Что ты отправил? А надо писать число от 1 до 10. Давай по новой.')
        await state.finish()


@dp.message_handler(state=add_photo_state.waiting_for_photo_type, content_types=types.ContentTypes.TEXT)
async def add_photo_type(message: types.Message, state: FSMContext):

    if message.text == '/category_list':
        s = 'Список категорий:\n'
        for i in db.get_category():
            s += f'{i[0]} - {i[1]}\n'

        await bot.send_message(message.chat.id, s)
    elif '/exit' in message.text:
        await bot.send_message(message.chat.id, 'Вышел')
        await state.finish()
    else:

        await state.update_data(photo_type=message.text.lower())
        await photo_state.waiting_for_count.set()
        await bot.send_message(message.chat.id, 'Пришли количесво для вывода')


@dp.message_handler(state=photo_state.waiting_for_photo_type, content_types=types.ContentTypes.TEXT)
async def photo_type_2(message: types.Message, state: FSMContext):
    if message.text == '/category_list':
        s = 'Список категорий:\n'
        for i in db.get_category():
            s += f'{i[0]} - {i[1]}\n'

        await bot.send_message(message.chat.id, s)
    elif '/exit' in message.text:
        await bot.send_message(message.chat.id, 'Вышел')
        await state.finish()
    else:
        f = await state.get_data()
        if not f['t']:
            await state.update_data(photo_type=message.text.lower())
            await photo_state.waiting_for_count.set()
            await bot.send_message(message.chat.id, 'Пришли количесво для вывода')
        else:
            await bot.send_photo(message.chat.id, db.get_random_picture(message.text.lower(), 1)[0][2])
            await state.finish()


@dp.message_handler(state=add_photo_state.waiting_for_photo, content_types=types.ContentTypes.TEXT)
async def add_photo_text(message: types.Message, state: FSMContext):
    if '/exit' in message.text:
        await bot.send_message(message.chat.id, 'Вышел')
        await state.finish()


@dp.message_handler(state=photo_state.waiting_for_add_photo, content_types=types.ContentTypes.PHOTO)
async def add_photo_2(message: types.Message, state: FSMContext):
    d = await state.get_data()

    #db.add_picture(message, d['photo_type'])
    #await message.reply('Добавил отправь ещё или /exit для выхода')
    await add_photo_state.waiting_for_photo_id.set()
    await state.update_data(file_id=message['photo'][-1]['file_id'])


@dp.message_handler(state=add_photo_state.waiting_for_photo_id, content_types=types.ContentTypes.TEXT)
async def add_photo_3(message: types.Message, state: FSMContext):
    print('d')
    await state.update_data(id=message.text)
    await add_photo_state.waiting_for_photo_time.set()


@dp.message_handler(state=add_photo_state.waiting_for_photo_time, content_types=types.ContentTypes.TEXT)
async def add_photo_4(message: types.Message, state: FSMContext):
    print('dfd')
    date = await state.get_data()
    db.add_picture_typo(date['id'], message.text, date['file_id'], 'a_art')
    await photo_state.waiting_for_add_photo.set()


@dp.message_handler(state=photo_state.waiting_for_add_photo, content_types=types.ContentTypes.TEXT)
async def add_photo_text(message: types.Message, state: FSMContext):
    if 'exit' in message.text:
        await state.finish()
        await message.reply('Вышел')


@dp.message_handler(lambda message: 'admin' in message.text)
async def admin(message: types.Message):
    if db.check_admin(message):
        await message.reply(f'Привет, {message.from_user.first_name}', reply=False, reply_markup=markup_admin)
        await admin_menu.waiting_for_command.set()


@dp.message_handler(state=admin_menu.waiting_for_command, content_types=types.ContentTypes.TEXT)
async def waiting_for_command(message: types.Message, state: FSMContext):
    if 'Добавить категорию' == message.text:
        await admin_menu.waiting_for_add_category.set()
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(Keyboard.category_list, Keyboard.exit_admin)
        await bot.send_message(message.from_user.id, 'Пришли название для новой категории //название не может содержать @', reply_markup=markup)
    elif 'Выйти из админки' == message.text:
        await state.finish()
        await bot.send_message(message.chat.id, f'Прощай {message.from_user.first_name}',
                               reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=admin_menu.waiting_for_add_category, content_types=types.ContentTypes.TEXT)
async def add_category(message: types.Message, state: FSMContext):
    if 'Выйти в окно' in message.text:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Прощай {message.from_user.first_name}',
                               reply_markup=ReplyKeyboardRemove())
    elif 'Список категорий' == message.text:
        list_cat = db.get_category()
        to_send = 'Список категорий\n'
        for i in list_cat:
            to_send += f'{i[0]} - {i[1]}\n'
        await bot.send_message(message.from_user.id, to_send)
    else:
        await state.update_data(name=message.text.lower())
        await bot.send_message(message.from_user.id, 'Пришли описание')
        await admin_menu.waiting_for_add_category_2.set()


@dp.message_handler(state=admin_menu.waiting_for_add_category_2, content_types=types.ContentTypes.TEXT)
async def add_category_2(message: types.Message, state: FSMContext):
    if 'Выйти в окно' in message.text:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Прощай {message.from_user.first_name}',
                               reply_markup=ReplyKeyboardRemove())
    elif 'Список категорий' == message.text:
        list_cat = db.get_category()
        to_send = 'Список категорий\n'
        for i in list_cat:
            to_send += f'{i[0]} - {i[1]}\n'
        await bot.send_message(message.from_user.id, to_send)
    else:
        await state.update_data(des=message.text)
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(Keyboard.add_something) \
            .row(Keyboard.category_list, Keyboard.try_again).row(Keyboard.exit_admin)
        await bot.send_message(message.from_user.id, 'Добавил описание', reply_markup=markup)
        await admin_menu.waiting_for_add_category_3.set()


@dp.message_handler(state=admin_menu.waiting_for_add_category_3, content_types=types.ContentTypes.TEXT)
async def add_category_3(message: types.Message, state: FSMContext):
    if 'Выйти в окно' in message.text:
        await state.finish()
        await bot.send_message(message.from_user.id, f'Прощай {message.from_user.first_name}',
                               reply_markup=ReplyKeyboardRemove())
    elif 'Список категорий' == message.text:
        list_cat = db.get_category()
        to_send = 'Список категорий\n'
        for i in list_cat:
            to_send += f'{i[0]} - {i[1]}\n'
        await bot.send_message(message.from_user.id, to_send)
    elif 'Начать заново' == message.text:
        await admin_menu.waiting_for_add_category.set()
        markup = ReplyKeyboardMarkup(resize_keyboard=True).row(Keyboard.category_list, Keyboard.exit_admin)
        await bot.send_message(message.from_user.id, 'Отправить название ещё раз', reply_markup=markup)
    if 'Добавить' == message.text:
        date = await state.get_data()
        db.add_category(date['name'], date['des'])
        await bot.send_message(message.from_user.id, 'Добавил', reply_markup=markup_admin)
        await admin_menu.waiting_for_command.set()


@dp.message_handler(commands='exit')
async def exit_from_all(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, 'Отменил все')


@dp.message_handler(commands='category_list')
async def category_list(message: types.Message):
    list_cat = db.get_category()
    to_send = 'Список категорий\n'
    for i in list_cat:
        to_send += f'{i[0]} - {i[1]}\n'
    await bot.send_message(message.from_user.id, to_send)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
