from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 8.2,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#222222",
    }
)


fig, ax = plt.subplots(figsize=(7.2, 5.2))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


def box(x, y, w, h, number, title, inputs, output, accent):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            facecolor="white",
            edgecolor=accent,
            linewidth=1.1,
        )
    )
    ax.text(x + 0.035, y + h / 2, number, fontsize=17, weight="bold", color=accent, ha="center", va="center")
    ax.text(x + 0.085, y + h * 0.68, title, fontsize=8.6, weight="bold", color=accent, va="center")
    ax.text(x + 0.085, y + h * 0.32, output, fontsize=7.0, color="#56636A", va="center", linespacing=1.25)
    ax.plot([x + 0.43, x + 0.43], [y + 0.03, y + h - 0.03], color="#E0E5E7", lw=0.7)
    ax.text(x + 0.46, y + h * 0.72, "Robust contextual inputs", fontsize=6.8, color="#6A7478", va="center")
    ax.text(x + 0.46, y + h * 0.32, inputs, fontsize=7.0, color="#30383B", va="center", linespacing=1.28)


ax.text(0.02, 0.95, "Relation-informed progressive recommender", fontsize=12, weight="bold", color="#253943")
ax.text(
    0.02,
    0.905,
    "Only contextual factors supported by both group-deletion retraining and test-set permutation enter each layer.",
    fontsize=7.4,
    color="#66757B",
)

ys = [0.65, 0.38, 0.11]
x = 0.025
w = 0.95
h = 0.205

box(x, ys[0], w, h, "1", "Recommend evaluation dimensions",
    "G4  Evaluation object  ·  96.3%\nG1  Evaluation purpose  ·  2.7%",
    "Rank dimensions\n→ user confirms one dimension", "#4477AA")
box(x, ys[1], w, h, "2", "Recommend subjective indicators",
    "G4  Evaluation object  ·  55.7%     G2  Design domain  ·  17.2%\nG6  Target users  ·  10.3%",
    "Use confirmed dimension\n→ rank indicators → user confirms one", "#3E8B82")
box(x, ys[2], w, h, "3", "Recommend tools",
    "G1  Evaluation purpose  ·  38.7%     G7  AI function  ·  19.8%\nG4  Evaluation object  ·  14.6%     G3  Design stage  ·  10.1%",
    "Use confirmed dimension + indicator\n→ rank tool classes and evidence", "#A14B88")

for y1, y2 in zip(ys[:-1], ys[1:]):
    ax.add_patch(FancyArrowPatch((0.50, y1 - 0.008), (0.50, y2 + h + 0.008), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=0.9, color="#737C80"))

ax.add_patch(
    FancyBboxPatch(
        (0.025, 0.015),
        0.95,
        0.075,
        boxstyle="round,pad=0.010,rounding_size=0.015",
        facecolor="#F4F7F8",
        edgecolor="#C5D0D5",
        linewidth=0.7,
    )
)
ax.text(
    0.045,
    0.052,
    "Across all layers",
    fontsize=7.7,
    weight="bold",
    color="#3F525B",
    va="center",
)
ax.text(
    0.21,
    0.052,
    "expose supporting papers and evidence records  ·  display uncertainty  ·  permit user revision",
    fontsize=7.2,
    color="#53646B",
    va="center",
)

stem = OUT / "fig07_progressive_evidence_guidance"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.04)

plt.close(fig)

