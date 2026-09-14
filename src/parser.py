import re

from config import TAG

AMOUNT_RE = re.compile(r"([+-])\s*(\d+(?:[.,]\d+)?)")


def parse_amounts(text):
	if not text or TAG not in text.lower():
		return []
	tail = text.lower().split(TAG, 1)[1]
	out = []
	for sign, num in AMOUNT_RE.findall(tail):
		value = float(num.replace(",", "."))
		out.append(value if sign == "+" else -value)
	return out
