import sqlite3
from datetime import datetime


def connect(db_path):
	con = sqlite3.connect(db_path)
	con.execute(
		"""CREATE TABLE IF NOT EXISTS profit_entries(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		chat_id INTEGER NOT NULL,
		user_id INTEGER NOT NULL,
		username TEXT DEFAULT '',
		amount REAL NOT NULL,
		day TEXT NOT NULL,
		created_at TEXT NOT NULL
		)"""
	)
	con.execute("CREATE INDEX IF NOT EXISTS idx_day ON profit_entries(chat_id, day)")
	return con


def add_entries(db_path, chat_id, user_id, username, amounts, tz, day=None):
	day = day or datetime.now(tz).strftime("%Y-%m-%d")
	now = datetime.now(tz).isoformat(timespec="seconds")
	con = connect(db_path)
	try:
		con.executemany(
			"INSERT INTO profit_entries(chat_id, user_id, username, amount, day, created_at) VALUES(?,?,?,?,?,?)",
			[(chat_id, user_id, username, a, day, now) for a in amounts],
		)
		con.commit()
	finally:
		con.close()


def daily_totals(db_path, chat_id, limit):
	con = connect(db_path)
	try:
		rows = con.execute(
			"SELECT day, SUM(amount) FROM profit_entries WHERE chat_id=? GROUP BY day ORDER BY day DESC LIMIT ?",
			(chat_id, limit),
		).fetchall()
	finally:
		con.close()
	return sorted(rows)
