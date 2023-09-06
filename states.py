from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from typing import Union
import asyncio

# States

# Додання нового фільму
class AddNewFilm(StatesGroup):
	film_name = State()
	content_type = State()
	photo = State()
	album = State()
	gif = State()
	video = State()

# видалення фільму
class DeleteFilm(StatesGroup):
	film_code = State()

# відправка розсилки
class SendAll(StatesGroup):
	msg_text = State()

# клас для альбомів
class AlbumMiddleware(BaseMiddleware):
	album_data: dict = {}

	def __init__(self, latency: Union[int, float] = 0.01):
		self.latency = latency
		super().__init__()

	async def on_process_message(self, message: types.Message, data: dict):
		if not message.media_group_id:
			return

		try:
			self.album_data[message.media_group_id].append(message)
			raise CancelHandler()
		except KeyError:
			self.album_data[message.media_group_id] = [message]
			await asyncio.sleep(self.latency)

			message.conf["is_last"] = True
			data["album"] = self.album_data[message.media_group_id]

	async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
		if message.media_group_id and message.conf.get("is_last"):
			del self.album_data[message.media_group_id]