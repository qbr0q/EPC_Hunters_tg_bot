import os
import base64
from datetime import datetime


def send_temp_photo(bot, user_id, image_info):
    image_data = image_info['image_data']
    image_name = image_info['image_name']

    image_data_binary = base64.b64decode(image_data)

    with open(image_name, "wb") as file:
        file.write(image_data_binary)

    with open(image_name, "rb") as photo:
        bot.send_photo(chat_id=user_id, photo=photo)

    os.remove(image_name)


def get_image_info(image_base64, user_id):
    image_name = f'ai-generated_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{user_id}.png'

    return {'image_data': image_base64, 'image_name': image_name}
