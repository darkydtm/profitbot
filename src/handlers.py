import asyncio
import logging
import re

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji

import reporting
import storage
from config import Settings

log = logging.getLogger("profitbot")
CHECK = "✅"
ARG_RE = re.compile(r"([+-]?)\s*(\d+(?:[.,]\d+)?)")


def parse_arg(text):
	parts = (text or "").split(None, 1)
	if len(parts) < 2:
		return None
	found = ARG_RE.fullmatch(parts[1].strip())
	if not found:
		return None
	sign, num = found.groups()
	value = float(num.replace(",", "."))
	return -value if sign == "-" else value


async def mark(bot, chat_id, message_id):
	try:
		await bot.set_message_reaction(chat_id, message_id, reaction=[ReactionTypeEmoji(emoji=CHECK)])
	except Exception:
		log.exception("reaction failed")


async def store(bot, m, settings, amount):
	await asyncio.to_thread(
		storage.add_entries, settings.db_path, m.chat.id, m.from_user.id,
		m.from_user.username or m.from_user.full_name, [amount], settings.tz, m.message_id,
	)
	await mark(bot, m.chat.id, m.message_id)
	await m.reply(f"{amount:+g} учтено")


def register(dp: Dispatcher, bot, settings: Settings):
	@dp.message(Command("stats"))
	async def stats(m: Message):
		if m.chat.id != settings.group_id:
			return
		log.info("stats chat=%s", m.chat.id)
		await reporting.send_report(bot, settings, m.chat.id)

	@dp.message(Command("add"))
	async def add(m: Message):
		if m.chat.id != settings.group_id:
			return
		value = parse_arg(m.text)
		if value is None:
			await m.reply("Использование: /add 20")
			return
		await store(bot, m, settings, value)

	@dp.message(Command("remove"))
	async def remove(m: Message):
		if m.chat.id != settings.group_id:
			return
		value = parse_arg(m.text)
		if value is None:
			await m.reply("Использование: /remove 5")
			return
		await store(bot, m, settings, -abs(value))
