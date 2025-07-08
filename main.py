from telebot import types, TeleBot
from dotenv import load_dotenv
from openai import OpenAI
import os
import requests
from datetime import datetime

from gpt_api.utils import send_text_request, send_text_and_photo_request
from db.models import Users, Templates
from db.utils import get_records, insert_or_update_record
from settings import markup_list, admin_list
from utils import send_temp_photo, get_image_info


load_dotenv("config.env")
BOT_TELEGRAM_API = os.getenv("BOT_TELEGRAM_API")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = TeleBot(BOT_TELEGRAM_API)
client = OpenAI(api_key=OPENAI_API_KEY)

# выбранные шаблоны сохраняются в локальную переменную. лютый колхоз, но для пет проекта норм я считаю
users_templates = {}


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    user = get_records(Users, {'user_id': user_id})
    if not user:
        user = Users(user_id=user_id, is_admin=user_id in admin_list)
        insert_or_update_record(user)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for markup_text in markup_list:
        markup.add(types.KeyboardButton(markup_text))

    bot.send_message(message.chat.id,
                     f'Привет! Это бот, который умеет генерировать фото по промту и фото\n\n'
                     f'Text2Image - напиши текст, и бот создаст картинку по описанию.\n'
                     f'Image2Image - загрузи фото и получи его переработанную версию.\n'
                     f'Photo + Prompt - отправь фото и подпиши его промптом, чтобы получить уникальную генерацию.',
                     reply_markup=markup)


@bot.message_handler(content_types=['photo', 'text'])
def user_prompt(message):
    user_id = message.chat.id
    user_text = message.text
    user_template = users_templates.get(user_id)

    if message.content_type == 'text' and user_text in markup_list:
        markup = types.InlineKeyboardMarkup()

        templates = get_records(Templates, all_rows=True)
        for template in templates:
            template_name = template.name
            markup.add(types.InlineKeyboardButton(
                template_name, callback_data=template_name)
            )

        bot.send_message(user_id, 'Вот доступные шаблоны', reply_markup=markup)

    elif message.content_type == 'text':
        image_base64 = send_text_request(client, message.text)
        image_info = get_image_info(image_base64, user_id)

        send_temp_photo(bot, user_id, image_info)

    elif message.content_type == 'photo' and user_template:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)

        input_image_url = f"https://api.telegram.org/file/bot{BOT_TELEGRAM_API}/{file_info.file_path}"
        output_image_base64 = send_text_and_photo_request(client, input_image_url, user_template.prompt)

        image_info = get_image_info(output_image_base64, user_id)
        send_temp_photo(bot, user_id, image_info)


@bot.callback_query_handler(func=lambda call: True)
def callback_template(call):
    user_id = call.from_user.id

    template = get_records(Templates, {'name': call.data})
    users_templates[user_id] = template

    bot.send_message(user_id, 'Шаблон выбран, теперь пришлите фотографию')


bot.polling(none_stop=True)
