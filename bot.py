from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import hcode
from typing import List

import asyncio


from bot_config import TOKEN, owner
import db_config
import keyboards

from states import AddNewFilm, DeleteFilm, SendAll, AlbumMiddleware

# Налаштування боту
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    db_config.get_user(message.from_user.id)
    await message.answer("Ласкаво просимо до боту з фільмами🪄\n\nПросто відправ мені код фільму і я відправлю тобі назву :)", reply_markup=keyboards.start_kb)

@dp.message_handler(Text(equals=['🪄Випадковий фільм🪄']))
async def actual_link(message: types.message):
	await start(message)

# Вхід до админ-панелі
@dp.message_handler(commands=['panel'])
async def panel(message: types.Message):
	if message.from_user.id == owner:
		await message.answer('Ласкаво просимо в панель адміністратора🪄', reply_markup=keyboards.panel_kb)

@dp.message_handler(Text(equals=['◀️Меню◀️']))
async def back_n_stop(message: types.message):
	await dp.storage.close()
	await dp.storage.wait_closed()
	await message.answer('Ви скасували дію🪄', reply_markup=keyboards.panel_kb)

@dp.message_handler(Text(equals=['🫂Кількисть користувачів🫂']))
async def users_stat(message: types.message):
    if message.from_user.id == owner:
        msg, users = db_config.get_users()
        await message.answer(msg)

@dp.message_handler(Text(equals=['📩Зробити розсилку📩']))
async def send_all(message: types.message):
    if message.from_user.id == owner:
        await message.answer('Надішліть текст повідомлення💬', reply_markup=keyboards.back_kb)
        await SendAll.msg_text.set()

@dp.message_handler(state=SendAll.msg_text)
async def send_all_message(message: types.Message, state: FSMContext):
    if(message.text == '◀️Меню◀️'):
        await back_n_stop(message)
        return
    
    msg, users = db_config.get_users()

    #активні/неактивні юзери
    a_users = 0
    n_users = 0

    for u in users:
        try:
            await bot.send_message(u, message.text)
            a_users += 1
        except:
            n_users += 1

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await message.answer(f'Розсилка відправлена🪄\n\nВсього відправлено: {a_users + n_users}\nАктивних: {a_users}\nНеактивних: {n_users}', reply_markup=keyboards.panel_kb)


# АДМІНСЬКІ КОМАНДИ
# Додавання фільму 
@dp.message_handler(Text(equals=['🎥Додати фільм🎥']))
async def add_code(message: types.message):
	if message.from_user.id == owner:
		await message.answer('Введіть назву фільму🪄', reply_markup=keyboards.back_kb)
		await AddNewFilm.film_name.set()

# Додавання фільму
@dp.message_handler(state=AddNewFilm.film_name)
async def send_name(message: types.Message, state: FSMContext):
    if(message.text == '◀️Меню◀️'):
        await back_n_stop(message)
        return

    async with state.proxy() as data:
        data['film_name'] = message.text
    
    await message.answer('Оберіть тип контенту🪄', reply_markup=keyboards.content_type_kb)
    await AddNewFilm.next()

#######################

@dp.message_handler(state=AddNewFilm.content_type)
async def send_content_type(message: types.Message, state: FSMContext):
    if(message.text == '◀️Меню◀️'):
        await back_n_stop(message)
        return

    async with state.proxy() as data:
        data['content_type'] = message.text
    if message.text == '📷Фото📷':
        await AddNewFilm.next()
        await message.answer('Надішліть фото🪄')
    elif message.text == '🖼Альбом🖼':
        await AddNewFilm.album.set()
        await message.answer('Надішліть альбом🪄')
    elif message.text == '🎞Гіф🎞':
        await AddNewFilm.gif.set()
        await message.answer('Надішліть гіф🪄')
    elif message.text == '📹Відео📹':
        await AddNewFilm.video.set()
        await message.answer('Надішліть відео🪄')
    else:
        await message.answer('Упс... Виникла помилка :(')
        await dp.storage.close()
        await dp.storage.wait_closed()


# 


@dp.message_handler(content_types=["photo"], state=AddNewFilm.photo)
async def send_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id

    result = db_config.add_new_film(data['film_name'], data['content_type'], data['photo_id'])

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
	
    if(result == 1):
        msg = f'Фільм було додано🪄'
        await message.answer(msg, parse_mode='HTML', reply_markup=keyboards.panel_kb)
    else:
        await message.answer("Виникла помилка :(\nСпробуйте ще раз!", reply_markup=keyboards.panel_kb)

# 


# 
@dp.message_handler(is_media_group=True, content_types=types.ContentType.ANY, state=AddNewFilm.album)
async def send_album(message: types.Message, album: List[types.Message], state: FSMContext):
    media_group = types.MediaGroup()
    media_group_data = []

    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id

        try:
            media_group_data.append(file_id)
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")

    async with state.proxy() as data:
        data['album'] = media_group_data

        album_media_ids = ''
    for i in media_group_data:
        album_media_ids += i + ', '

    result = db_config.add_new_film(data['film_name'], data['content_type'], album_media_ids)

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
	
    if(result == 1):
        msg = f'Фільм було додано🪄'
        await message.answer(msg, parse_mode='HTML', reply_markup=keyboards.panel_kb)
    else:
        await message.answer("Виникла помилка :(\nСпробуйте ще раз!", reply_markup=keyboards.panel_kb)

# 

# 


@dp.message_handler(content_types=["animation"], state=AddNewFilm.gif)
async def send_animation(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gif_id'] = message.animation.file_id
    
    result = db_config.add_new_film(data['film_name'], data['content_type'], data['gif_id'])

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
	
    if(result == 1):
        msg = f'Фільм було додано🪄'
        await message.answer(msg, parse_mode='HTML', reply_markup=keyboards.panel_kb)
    else:
        await message.answer("Виникла помилка :(\nСпробуйте ще раз!", reply_markup=keyboards.panel_kb)

# 



# 


@dp.message_handler(content_types=["video"], state=AddNewFilm.video)
async def send_video(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['video_id'] = message.video.file_id
    
    result = db_config.add_new_film(data['film_name'], data['content_type'], data['video_id'])

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
	
    if(result == 1):
        msg = f'Фільм було додано🪄'
        await message.answer(msg, parse_mode='HTML', reply_markup=keyboards.panel_kb)
    else:
        await message.answer("Виникла помилка :(\nСпробуйте ще раз!", reply_markup=keyboards.panel_kb)
	

# 

# Видалення фільму
@dp.message_handler(Text(equals=['❌Видалити фільм❌']))
async def delete_code(message: types.message):
	await message.answer('Надішліть код фільму для видалення🪄', reply_markup=keyboards.back_kb)
	await DeleteFilm.film_code.set()

#
@dp.message_handler(state=DeleteFilm.film_code)
async def delete_code_by_name(message: types.Message, state: FSMContext):
    if(message.text == '◀️Меню◀️'):
        await back_n_stop(message)
        return
	
    result = db_config.delete_film(message.text)

    await state.finish()
    await dp.storage.close()
    await dp.storage.wait_closed()
	
    if(result == 1):
        msg = f'Фільм було додано🪄'
        await message.answer(msg, parse_mode='HTML', reply_markup=keyboards.panel_kb)
    else:
        await message.answer("Виникла помилка :(\nСпробуйте ще раз!", reply_markup=keyboards.panel_kb)
	
# Інформація по кодах
@dp.message_handler(Text(equals=['📽Інформація по фільмах📽']))
async def films_info(message: types.message):
    films = db_config.get_films()
    msg = f'Всего кодов: {len(films)}\n\n5 последих кодов:\n\n {films[-5:]}'

    await message.answer(msg)


# Видання фільму за кодом
@dp.message_handler()
async def echo(message: types.Message):

	film = db_config.get_film_by_code(message.text)
	print(film)

	if film == 0:
		await message.answer('Упс... Схоже такого коду немає.')
		return

	if film[3] == '📷Фото📷':
		await message.answer_photo(film[4], caption=film[1])
	elif film[3] == '🖼Альбом🖼':
		media_group = film[4].split(', ')
		media_group_send = types.MediaGroup()
		try:
			for i in media_group:
				if i == "":
					pass
				else:
					media_group_send.attach({"media": i, "type": "photo"})
			await message.answer_media_group(media_group_send)
			await message.answer(film[1])
		except ValueError:
			return await message.answer("This type of album is not supported by aiogram.")
	elif film[3] == '🎞Гиф🎞':
		await message.answer_animation(film[4], caption=film[1])
	elif film[3] == '📹Видео📹':
		await message.answer_video(film[4], caption=film[1])



# ---------------------------
if __name__ == '__main__':
    db_config.database_setup()
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp)