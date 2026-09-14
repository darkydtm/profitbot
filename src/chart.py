import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BG = "#282828"
GRID = "#3c3836"
GRAY = "#a89984"
LINE = "#83a598"


def render_chart(totals):
	days = [datetime.strptime(d, "%Y-%m-%d").strftime("%d.%m") for d, _ in totals]
	vals = [v for _, v in totals]
	fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
	fig.patch.set_facecolor(BG)
	ax.set_facecolor(BG)
	ax.plot(days, vals, color=LINE, linewidth=2, marker="o", markersize=5)
	ax.grid(axis="y", color=GRID, linewidth=0.8)
	ax.tick_params(colors=GRAY)
	for spine in ax.spines.values():
		spine.set_visible(False)
	fig.tight_layout()
	buf = io.BytesIO()
	fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
	plt.close(fig)
	buf.seek(0)
	return buf.getvalue()
