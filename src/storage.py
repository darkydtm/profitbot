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
		created_at TEXT NOT NULL,
		message_id INTEGER DEFAULT 0
		)"""
	)
	cols = [row[1] for row in con.execute("PRAGMA table_info(profit_entries)").fetchall()]
	if "message_id" not in cols:
		con.execute("ALTER TABLE profit_entries ADD COLUMN message_id INTEGER DEFAULT 0")
	con.execute("CREATE INDEX IF NOT EXISTS idx_day ON profit_entries(chat_id, day)")
	return con


def add_entries(db_path, chat_id, user_id, username, amounts, tz, message_id, day=None):
	day = day or datetime.now(tz).strftime("%Y-%m-%d")
	now = datetime.now(tz).isoformat(timespec="seconds")
	con = connect(db_path)
	try:
		con.executemany(
			"INSERT INTO profit_entries(chat_id, user_id, username, amount, day, created_at, message_id) VALUES(?,?,?,?,?,?,?)",
			[(chat_id, user_id, username, a, day, now, message_id) for a in amounts],
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
