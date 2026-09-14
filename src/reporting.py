import asyncio
import logging
from datetime import datetime

from aiogram.types import BufferedInputFile, InputMediaPhoto

import chart
import storage

log = logging.getLogger("profitbot")


def build_caption(totals):
	lines = [f"{datetime.strptime(d, '%Y-%m-%d').strftime('%d.%m')}: {v:+g}" for d, v in totals]
	return "📈 Профит по дням\n" + "\n".join(lines) + f"\n\nИтого: {sum(v for _, v in totals):+g}"


async def send_report(bot, settings, chat_id=None, pin=False, placeholder=None):
	target = chat_id or settings.group_id
	totals = await asyncio.to_thread(storage.daily_totals, settings.db_path, target, settings.report_days)
	if not totals:
		text = "Пока нет данных. Добавьте через /profit N"
		if placeholder is None:
			await bot.send_message(target, text)
		else:
			await bot.edit_message_text(text, target, placeholder.message_id)
		return
	image = await asyncio.to_thread(chart.render_chart, totals)
	photo = BufferedInputFile(image, "profit.png")
	caption = build_caption(totals)
	if placeholder is None:
		msg = await bot.send_photo(target, photo, caption=caption)
		if pin:
			try:
				await bot.pin_chat_message(target, msg.message_id, disable_notification=True)
			except Exception:
				log.exception("pin failed")
		return
	await bot.edit_message_media(
		chat_id=target,
		message_id=placeholder.message_id,
		media=InputMediaPhoto(media=photo, caption=caption),
	)
