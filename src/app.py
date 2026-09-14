import asyncio
import logging

from aiogram import Bot, Dispatcher

import handlers
import scheduler
from config import load_settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("profitbot")


async def main(settings=None):
	settings = settings or load_settings()
	if not settings.token or not settings.group_id:
		raise SystemExit("Set BOT_TOKEN and GROUP_ID in deploy/.env")
	log.info("watching group %s", settings.group_id)
	bot = Bot(settings.token)
	dp = Dispatcher()
	handlers.register(dp, bot, settings)
	asyncio.create_task(scheduler.midnight_loop(bot, settings))
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())
