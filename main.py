from aiogram import Bot, Dispatcher, types, executor

from config import BOT_TOKEN, database_file, ADMIN_ID
from db import Database

import kb
import asyncio
import schedule

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
db = Database(database_file)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_users(message.from_user.id)

    print(schedule.currtime(), message.from_user.id, message.from_user.username, message.text)

    await message.answer(
        'Привет, Друже! 👋 \n\n'
        'Я неофициальный бот, который будет присылать тебе новинки и изменения в расписании стримов с сайта '
        'stopgame.ru\n\n'
        '/current - <em>узнать текущее расписание</em>\n'
        '/settings - <em>настройки уведомлений</em>',
        parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands=['current'])
async def current(message: types.Message):
    print(schedule.currtime(), message.from_user.id, message.from_user.username, message.text)

    streamlist = schedule.load()
    keys = streamlist.keys()

    if not keys:
        await message.answer('Нет запланированных стримов')

    for k in keys:
        poster = streamlist[k]['stream_poster']
        if not poster:
            poster = 'https://disk.yandex.ru/i/GsgzxAUhk0elqQ'

        await bot.send_photo(chat_id=message.chat.id, photo=poster,
                             caption=schedule.get_caption(streamlist, k),
                             parse_mode=types.ParseMode.HTML, reply_markup=kb.linkbutton_kb)
        await asyncio.sleep(0.8)


# @dp.message_handler(commands=['sendall'])
# async def send_all_message(message: types.Message):
#     if message.from_user.id == ADMIN_ID:
#         for row in db.get_users():
#             try:
#                 await bot.send_message(chat_id=row[0], text=message.text[9:])
#                 if int(row[1] != 1):
#                     db.set_active(row[0], 1)
#             except:
#                 db.set_active(row[0], 0)
#
#             await asyncio.sleep(0.5)


# @dp.message_handler(commands=['sendallkeys'])
# async def send_all_keys(message: types.Message):
#     if message.from_user.id == ADMIN_ID:
#
#         streamlist = schedule.load_from_file('streams.json')
#         keys = message.text[13:].split(',')
#
#         await send_all(streamlist, keys)


@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    print(schedule.currtime(), message.from_user.id, message.from_user.username, message.text)
    for i in db.get_live_notice(message.from_user.id):
        if i == 1:
            await message.answer('Уведомления о начале стримов: On', reply_markup=kb.settings)
        else:
            await message.answer('Уведомления о начале стримов: Off', reply_markup=kb.settings)
    await message.delete()


@dp.callback_query_handler()
async def callback_settings(callback: types.CallbackQuery):
    if callback.data == 'on':
        try:
            db.set_live_notice(callback.message.chat.id, 1)
            await callback.message.edit_text('Уведомления о начале стримов: On', reply_markup=kb.settings)
            print(schedule.currtime(), callback.message.chat.id, callback.message.chat.username, 'live_notice on')
        except:
            await callback.answer('Уведомления уже включены')
    if callback.data == 'off':
        try:
            db.set_live_notice(callback.message.chat.id, 0)
            await callback.message.edit_text('Уведомления о начале стримов: Off', reply_markup=kb.settings)
            print(schedule.currtime(), callback.message.chat.id, callback.message.chat.username, 'live_notice off')
        except:
            await callback.answer('Уведомления уже выключены')
    if callback.data == 'delete':
        await callback.message.delete()
        await callback.answer()


async def send_all(streamlist, key, difference=False):
    for k in key:
        if k == '0':
            await send_live(streamlist)
        else:
            poster = streamlist[k]['stream_poster']
            if not poster:
                poster = 'https://disk.yandex.ru/i/GsgzxAUhk0elqQ'

            # caption = schedule.get_caption(streamlist, k)
            # if difference is True:
            #     caption = '[<em> Найдены изменения в анонсе </em>]\n\n' + caption

            for row in db.get_users():
                try:
                    if difference is True:
                        await bot.send_message(chat_id=row[0], text='<b>Найдены изменения в анонсе:</b>',
                                               parse_mode=types.ParseMode.HTML)
                        await asyncio.sleep(0.5)

                    await bot.send_photo(chat_id=row[0], photo=poster, caption=schedule.get_caption(streamlist, k),
                                         parse_mode=types.ParseMode.HTML, reply_markup=kb.linkbutton_kb)
                    if int(row[1] != 1):
                        db.set_active(row[0], 1)
                    print(schedule.currtime(), f'{k} sent successfully to {row[0]}')

                except:
                    db.set_active(row[0], 0)
                    print(schedule.currtime(), f'{k} not sent to {row[0]}')

                await asyncio.sleep(0.8)


async def send_live(streamlist):
    for row in db.get_users():
        if row[2] == 1:
            try:
                await bot.send_message(chat_id=row[0], text=schedule.get_live_caption(streamlist),
                                       parse_mode=types.ParseMode.HTML, reply_markup=kb.linkbutton_kb)
                if int(row[1] != 1):
                    db.set_active(row[0], 1)

                print(schedule.currtime(), f'0 sent successfully to {row[0]}')

            except:
                db.set_active(row[0], 0)
                print(schedule.currtime(), f'0 not sent to {row[0]}')

        await asyncio.sleep(0.8)


async def background_on_start() -> None:
    while True:
        json_filename = 'streams.json'
        json_streamlist = schedule.load_from_file(json_filename)
        try:
            streamlist = schedule.load()
        except:
            print(schedule.currtime(), 'Failed to load the schedule from the website')
            streamlist = schedule.load_from_file(json_filename)
            print(schedule.currtime(), 'Loaded saved schedule')
        try:
            new_keys = schedule.find_new_keys(streamlist, json_streamlist)
            if new_keys:
                await send_all(streamlist, new_keys)
                schedule.add_to_json(json_filename, new_keys, streamlist, json_streamlist)
        except:
            new_keys = None
            print(schedule.currtime(), 'Error searching for new keys')
        try:
            old_keys = schedule.find_old_keys(streamlist, json_streamlist)
            if old_keys:
                schedule.remove_from_json(old_keys, json_streamlist, json_filename)
        except:
            old_keys = None
            print(schedule.currtime(), 'Error searching for old keys')
        try:
            if not new_keys and not old_keys:
                diff_value_keys = schedule.find_diff_values(streamlist, json_streamlist)
                if diff_value_keys:
                    await send_all(streamlist, diff_value_keys, difference=True)
                    schedule.add_to_json(json_filename, diff_value_keys, streamlist, json_streamlist)
        except:
            print(schedule.currtime(), 'Error searching for difference value in keys')

        await asyncio.sleep(20)

        # jsonfile = 'streams.json'
        #
        # streamlist = schedule.load()
        # streamjson = schedule.load_from_file(jsonfile)
        #
        # new_keys = schedule.find_new_keys(streamlist, streamjson)
        # if new_keys:
        #     for k in new_keys:
        #         if k == '0':
        #             await send_all_live(streamlist, k)
        #         else:
        #             await send_all_new(streamlist, k)
        #     for k in new_keys:
        #         schedule.add_to_json(jsonfile, k, streamlist, streamjson)
        #
        # old_keys = schedule.find_old_keys(streamlist, streamjson)
        # if old_keys:
        #     for k in old_keys:
        #         schedule.remove_from_json(k, streamjson, jsonfile)
        #
        # if not new_keys and not old_keys:
        #     diff_value = schedule.find_diff_values(streamlist, streamjson)
        #     if diff_value:
        #         for k in diff_value:
        #             await send_all_new(streamlist, k, difference=True)
        #             schedule.add_to_json(jsonfile, k, streamlist, streamjson)
        #
        # await asyncio.sleep(10)


async def on_bot_start_up(dispatcher: Dispatcher) -> None:
    asyncio.create_task(background_on_start())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_bot_start_up)
