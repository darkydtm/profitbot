import asyncio
import logging

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji

import reporting
import storage
from config import TAG, Settings
from parser import parse_amounts

log = logging.getLogger("profitbot")
CHECK = "✅"


async def mark(bot, chat_id, message_id, emoji=CHECK):
	try:
		reactions = [ReactionTypeEmoji(emoji=emoji)] if emoji else []
		await bot.set_message_reaction(chat_id, message_id, reaction=reactions)
	except Exception:
		log.exception("reaction failed")


def register(dp: Dispatcher, bot, settings: Settings):
	@dp.message(Command("stats"))
	async def stats(m: Message):
		if m.chat.id != settings.group_id:
			return
		await reporting.send_report(bot, settings, m.chat.id)

	@dp.message(Command("add"))
	async def add(m: Message):
		if m.chat.id != settings.group_id:
			return
		target = m.reply_to_message
		if target is None:
			await m.reply("Ответь /add реплаем на сообщение с #профит")
			return
		amounts = parse_amounts(target.text or target.caption or "")
		if not amounts:
			await m.reply("В отвеченном сообщении нет сумм #профит")
			return
		exists = await asyncio.to_thread(storage.has_entries, settings.db_path, m.chat.id, target.message_id)
		if exists:
			await m.reply("Уже учтено")
			return
		await asyncio.to_thread(
			storage.add_entries, settings.db_path, target.chat.id, target.from_user.id,
			target.from_user.username or target.from_user.full_name, amounts, settings.tz, target.message_id,
		)
		await mark(bot, m.chat.id, target.message_id)
		await m.reply(f"{sum(amounts):+g} добавлено")

	@dp.message(Command("remove"))
	async def remove(m: Message):
		if m.chat.id != settings.group_id:
			return
		target = m.reply_to_message
		if target is None:
			await m.reply("Ответь /remove реплаем на сообщение с #профит")
			return
		amounts = parse_amounts(target.text or target.caption or "")
		if not amounts:
			await m.reply("В отвеченном сообщении нет сумм #профит")
			return
		count, total = await asyncio.to_thread(
			storage.remove_entries, settings.db_path, m.chat.id, target.message_id,
		)
		if not count:
			await m.reply("Сообщение не учтено в статистике")
			return
		await mark(bot, m.chat.id, target.message_id, emoji="")
		await m.reply(f"🗑 {total:+g} удалено")

	@dp.message(F.chat.id == settings.group_id, F.text.contains(TAG) | F.caption.contains(TAG))
	async def collect(m: Message):
		amounts = parse_amounts(m.text or m.caption or "")
		if not amounts:
			return
		await asyncio.to_thread(
			storage.add_entries, settings.db_path, m.chat.id, m.from_user.id,
			m.from_user.username or m.from_user.full_name, amounts, settings.tz, m.message_id,
		)
		await mark(bot, m.chat.id, m.message_id)
		await m.reply(f"{sum(amounts):+g} учтено")
