from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

#Стартова панель
content_btn = KeyboardButton('🪄Випадковий фільм🪄')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(content_btn)

#Админ панель
add_film_btn = KeyboardButton('🎥Додати фільм🎥')
delete_film_btn = KeyboardButton('❌Видалити фільм❌')
films_info_btn = KeyboardButton('📽Інформація по фільмах📽')
amount_users_btn = KeyboardButton('🫂Кількисть користувачів🫂')
send_all_btn = KeyboardButton('📩Зробити розсилку📩')
panel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
panel_kb.add(send_all_btn).row(add_film_btn, delete_film_btn).row(films_info_btn, amount_users_btn)
#
back_btn = KeyboardButton('◀️Меню◀️')
back_kb = ReplyKeyboardMarkup(resize_keyboard=True)
back_kb.row(back_btn)

# Тип контента
photo_btn = KeyboardButton('📷Фото📷')
album_btn = KeyboardButton('🖼Альбом🖼')
gif_btn = KeyboardButton('🎞Гіф🎞')
video_btn = KeyboardButton('📹Відео📹')
content_type_kb = ReplyKeyboardMarkup(resize_keyboard=True)
content_type_kb.row(photo_btn, album_btn).row(gif_btn, video_btn).row(back_btn)
