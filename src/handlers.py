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


def register(dp: Dispatcher, bot, settings: Settings):
	@dp.message(Command("stats"))
	async def stats(m: Message):
		if m.chat.id != settings.group_id:
			return
		await reporting.send_report(bot, settings, m.chat.id)

	@dp.message(F.chat.id == settings.group_id, F.text.contains(TAG) | F.caption.contains(TAG))
	async def collect(m: Message):
		amounts = parse_amounts(m.text or m.caption or "")
		if not amounts:
			return
		await asyncio.to_thread(
			storage.add_entries, settings.db_path, m.chat.id, m.from_user.id,
			m.from_user.username or m.from_user.full_name, amounts, settings.tz,
		)
		try:
			await bot.set_message_reaction(m.chat.id, m.message_id, reaction=[ReactionTypeEmoji(emoji="👍")])
		except Exception:
			log.exception("reaction failed")
		await m.reply(f"✅ {sum(amounts):+g} учтено")
