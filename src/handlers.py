import ast
import asyncio
import logging
import operator

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji

import reporting
import storage
from config import Settings

log = logging.getLogger("profitbot")
CHECK = "✅"
OPS = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
	ast.USub: operator.neg,
	ast.UAdd: operator.pos,
}


def _eval(node):
	if isinstance(node, ast.Constant):
		if type(node.value) in (int, float):
			return node.value
		raise ValueError("bad expression")
	if isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
		return OPS[type(node.op)](_eval(node.left), _eval(node.right))
	if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
		return OPS[type(node.op)](_eval(node.operand))
	raise ValueError("bad expression")


def parse_arg(text):
	parts = (text or "").split(None, 1)
	if len(parts) < 2 or not parts[1].strip():
		return None
	try:
		return float(_eval(ast.parse(parts[1].strip(), mode="eval").body))
	except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, RecursionError):
		return None


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

	@dp.message(Command("profit"))
	async def profit(m: Message):
		if m.chat.id != settings.group_id:
			return
		value = parse_arg(m.text)
		if value is None:
			await m.reply("Использование: /profit 20+5*2")
			return
		await store(bot, m, settings, value)
