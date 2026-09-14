import asyncio
import logging
from datetime import datetime

from aiogram.types import BufferedInputFile

import chart
import storage

log = logging.getLogger("profitbot")


def build_caption(totals):
	lines = [f"{datetime.strptime(d, '%Y-%m-%d').strftime('%d.%m')}: {v:+g}" for d, v in totals]
	return "📈 Профит по дням\n" + "\n".join(lines) + f"\n\nИтого: {sum(v for _, v in totals):+g}"


async def send_report(bot, settings, chat_id=None, pin=False):
	target = chat_id or settings.group_id
	totals = await asyncio.to_thread(storage.daily_totals, settings.db_path, target, settings.report_days)
	if not totals:
		await bot.send_message(target, "Пока нет данных #профит")
		return
	image = await asyncio.to_thread(chart.render_chart, totals)
	msg = await bot.send_photo(target, BufferedInputFile(image, "profit.png"), caption=build_caption(totals))
	if pin:
		try:
			await bot.pin_chat_message(target, msg.message_id, disable_notification=True)
		except Exception:
			log.exception("pin failed")
