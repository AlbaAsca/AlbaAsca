"""Avatar neón: crestas (ridgeline) con 60 días de temperatura real de aws-data-pipeline.

    python make_avatar.py "../aws-data-pipeline/data/raw/weather/**/*.parquet"
"""

import sys
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

OUT = Path(__file__).parent / "assets"
BG = "#16161E"
CMAP = LinearSegmentedColormap.from_list("neon", ["#7DCFFF", "#7AA2F7", "#BB9AF7", "#F7768E", "#E0AF68"])


def series(raw_glob: str) -> list[np.ndarray]:
    rows = duckdb.connect().execute(
        "select city, observed_at, temperature_c from read_parquet(?) order by city, observed_at", [raw_glob]
    ).fetchall()
    by_city: dict[str, list[float]] = {}
    for city, _, t in rows:
        by_city.setdefault(city, []).append(t)
    # cada cresta = 6 días de una ciudad, suavizada: 10 crestas de 144 horas
    out = []
    for temps in by_city.values():
        arr = np.convolve(np.array(temps), np.ones(6) / 6, mode="same")
        for start in range(0, len(arr) - 144, 144 * 4):
            out.append(arr[start : start + 144])
    return out[:12]


def draw(curves: list[np.ndarray], path: Path, initials: bool) -> None:
    fig = plt.figure(figsize=(8, 8), dpi=100, facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1], facecolor=BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n = len(curves)
    x = np.linspace(0.16, 0.84, len(curves[0]))
    window = np.sin(np.linspace(0, np.pi, len(x))) ** 2  # picos en el centro, como una montaña
    for i, c in enumerate(curves):
        base = 0.3 + i * (0.42 / n)
        y = base + (c - c.min()) / (np.ptp(c) + 1e-9) * 0.15 * window
        color = CMAP(i / (n - 1))
        ax.fill_between(x, base - 0.01, y, color=BG, zorder=2 * (n - i))
        for lw, alpha in ((5, 0.08),):
            ax.plot(x, y, color=color, linewidth=lw, alpha=alpha, zorder=2 * (n - i) + 1, solid_capstyle="round")
        ax.plot(x, y, color=color, linewidth=1.8, zorder=2 * (n - i) + 1, solid_capstyle="round")

    # anillo neón que encaja con el recorte circular de GitHub
    t = np.linspace(0, 2 * np.pi, 400)
    for lw, alpha in ((10, 0.05), (3, 0.9)):
        ax.plot(0.5 + 0.465 * np.cos(t), 0.5 + 0.465 * np.sin(t), color="#7AA2F7", lw=lw, alpha=alpha, zorder=200)
    if initials:
        for size, alpha in ((92, 0.2), (80, 1)):
            ax.text(0.5, 0.17, "AA", ha="center", va="center", fontsize=size * 0.6, fontweight="bold",
                    color="#C0CAF5", alpha=alpha, zorder=100)
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def main() -> None:
    curves = series(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    draw(curves, OUT / "avatar.png", initials=False)
    draw(curves, OUT / "avatar-initials.png", initials=True)
    print("assets/avatar.png, assets/avatar-initials.png")


if __name__ == "__main__":
    main()
