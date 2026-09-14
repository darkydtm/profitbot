import asyncio
import logging
from datetime import datetime, timedelta

import reporting

log = logging.getLogger("profitbot")


async def midnight_loop(bot, settings):
	while True:
		now = datetime.now(settings.tz)
		next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=5, microsecond=0)
		await asyncio.sleep((next_run - now).total_seconds())
		try:
			await reporting.send_report(bot, settings, pin=True)
		except Exception:
			log.exception("daily report failed")
