import requests
import telebot
from telebot import types
from api import token
from PIL import Image
from pytesseract import image_to_string


bot = telebot.TeleBot(token)

leng_all = ('eng', 'rus', 'ukr')

leng_select = 'rus'

last_txt = ''


def leng_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in leng_all:
        item = types.KeyboardButton(i)
        markup.add(item)
    return markup


buttons = ('Считать текст с фото',
           'Записать текст с фото в файл', 'Изменить язык')


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in buttons:
        item = types.KeyboardButton(i)
        markup.add(item)
    return markup


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    mess = 'Привет, это бот конвентор в который может считывать текст с картинки и записыватье его в файл.'
    bot.send_message(message.chat.id, mess, reply_markup=start_markup())


@bot.message_handler(content_types=['text'])
def message_text_voice(message):
    bot.send_chat_action(message.chat.id, 'typing')

    global leng_select

    if message.text == 'Считать текст с фото':
        mess = f'Отправте фото\nВыбранный яззык распознавания: {leng_select}'
        bot.send_message(message.chat.id, mess)

    elif message.text == 'Изменить язык':
        mess = 'Выберите язык:'
        bot.send_message(message.chat.id, mess, reply_markup=leng_markup())

    elif message.text in leng_all:
        leng_select = message.text
        mess = f'Язык распознавания успешно изменен на: {leng_select}'
        bot.send_message(message.chat.id, mess, reply_markup=start_markup())

    elif message.text == 'Записать текст с фото в файл':

        if last_txt != '':
            str = f'files/{message.chat.id}.txt'

            with open(str, 'w') as txt_file:
                txt_file.write(last_txt)

            with open(str, 'r') as txt_file:
                post_data = {'chat_id': message.chat.id}
                post_file = {'document': txt_file}
                r = requests.post(
                    f'https://api.telegram.org/bot{token}/sendDocument', data=post_data, files=post_file)

        else:
            mess = 'Нечего записывать, сначала отправте фото.'
            bot.send_message(message.chat.id, mess)


@bot.message_handler(content_types=['photo'])
def message_photo(message):
    bot.send_chat_action(message.chat.id, 'typing')
    global last_txt

    mess = 'Запрос обрабатываеться'
    bot.send_message(message.chat.id, mess)
    bot.send_chat_action(message.chat.id, 'typing')

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'photo/' + message.photo[-1].file_id

    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    text = image_to_string(Image.open(src), lang=leng_select)
    last_txt = text

    mess = f'Текст с картинки: \n\n{text}'
    bot.send_message(message.chat.id, mess)


bot.infinity_polling()
