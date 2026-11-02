"""Imágenes de vista previa (1280x640) para compartir los repos destacados.

    python make_social.py <imagen de cada repo, en el orden de CARDS>
"""

import sys
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

plt.rcParams["text.parse_math"] = False  # que «$» se pinte tal cual

OUT = Path(__file__).parent / "assets" / "social"
BG, FG, MUTED = "#1A1B26", "#C0CAF5", "#9AA5CE"

CARDS = [
    (
        "aws-data-pipeline",
        "Datos de punta a punta en AWS",
        "Lambda · S3 · dbt + DuckDB\nTerraform · GitHub OIDC\nLocalStack a 0 $ · AWS real < 0,01 $",
        "#7DCFFF",
    ),
    (
        "store-sales-forecasting",
        "Previsión de ventas en Kaggle",
        "1.782 series temporales\nValidación temporal honesta\nRMSLE 0,458 → 0,388 (−15 %)",
        "#BB9AF7",
    ),
    (
        "agent-board",
        "Agentes de IA en un kanban",
        "Consultor · arquitecto\nDesarrollador · tester\nTiempo estimado frente a real",
        "#E0AF68",
    ),
    (
        "WebFluxTaskManager",
        "API reactiva en tiempo real",
        "Java 21 · Spring Boot 4 · WebFlux\nMongoDB reactivo · HATEOAS\nSSE · Testcontainers",
        "#9ECE6A",
    ),
    (
        "realtime-fraud-pipeline",
        "Fraude detectado en tiempo real",
        "Kafka (KRaft) · Kafka Streams\nVentanas · exactly-once · DLQ\nJava 21 · Spring Boot 4 · SSE",
        "#F7768E",
    ),
]


def card(name: str, title: str, sub: str, accent: str, image: str) -> None:
    fig = plt.figure(figsize=(12.8, 6.4), dpi=100, facecolor=BG)
    for x in range(0, 1281, 40):
        fig.add_artist(plt.Line2D([x / 1280] * 2, [0, 1], color="#1F2335", lw=0.6))
    for y in range(0, 641, 40):
        fig.add_artist(plt.Line2D([0, 1], [y / 640] * 2, color="#1F2335", lw=0.6))
    fig.add_artist(plt.Rectangle((0, 0), 0.012, 1, color=accent, transform=fig.transFigure))
    fig.text(0.05, 0.86, "AlbaAsca /", color=MUTED, fontsize=22)
    fig.text(0.05, 0.74, name, color=accent, fontsize=46 if len(name) < 20 else 40, fontweight="bold")
    fig.text(0.05, 0.63, title, color=FG, fontsize=26)
    fig.text(0.05, 0.5, sub, color=MUTED, fontsize=18, linespacing=1.7, va="top")
    ax = fig.add_axes([0.46, 0.05, 0.51, 0.52])
    ax.imshow(mpimg.imread(image))
    ax.axis("off")
    fig.savefig(OUT / f"{name}.png", facecolor=BG)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for (name, title, sub, accent), image in zip(CARDS, sys.argv[1:], strict=True):
        card(name, title, sub, accent, image)
        print(OUT / f"{name}.png")


if __name__ == "__main__":
    main()
