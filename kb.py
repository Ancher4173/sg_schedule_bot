from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

linkbutton_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Перейти на Twitch', url='https://www.twitch.tv/stopgameru'))
settings = InlineKeyboardMarkup().add(InlineKeyboardButton('On', callback_data='on'),
                                      InlineKeyboardButton('Off', callback_data='off'))\
    .add(InlineKeyboardButton('✓', callback_data='delete'))

