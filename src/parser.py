import re

from config import TAG

AMOUNT_RE = re.compile(r"([+-])\s*(\d+(?:[.,]\d+)?)")


def parse_amounts(text):
	if not text or TAG not in text.lower():
		return []
	tail = text.lower().split(TAG, 1)[1]
	found = AMOUNT_RE.search(tail)
	if not found:
		return []
	sign, num = found.groups()
	value = float(num.replace(",", "."))
	return [value if sign == "+" else -value]
