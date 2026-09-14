import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

TAG = "#профит"


def load_dotenv(path=".env"):
	if not os.path.exists(path):
		return
	with open(path, encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue
			key, value = line.split("=", 1)
			os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
	token: str
	group_id: int
	tz: ZoneInfo
	db_path: str
	report_days: int


def load_settings():
	for path in ("deploy/.env", ".env"):
		load_dotenv(path)
	return Settings(
		token=os.getenv("BOT_TOKEN", ""),
		group_id=int(os.getenv("GROUP_ID", "0")),
		tz=ZoneInfo(os.getenv("TIMEZONE", "Europe/Moscow")),
		db_path=os.getenv("DB_PATH", "profit.db"),
		report_days=int(os.getenv("REPORT_DAYS", "14")),
	)
