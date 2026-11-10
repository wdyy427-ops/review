from pathlib import Path
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Wedge


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 8.5,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#202427",
    }
)


fig, ax = plt.subplots(figsize=(6.5, 6.2))
ax.set_aspect("equal")
ax.set_xlim(-4.15, 4.15)
ax.set_ylim(-3.82, 3.82)
ax.axis("off")

cx, cy = 0.0, -0.03

# The contextual field surrounds the complete operationalization structure.
context_outer = 3.42
context_inner = 2.72
context_fills = ["#EEF3F4", "#F5F7F7"] * 4
context_edge = "#81959C"

factors = [
    ("G1", "Evaluation\npurpose"),
    ("G2", "Design\ndomain"),
    ("G3", "Design\nstage"),
    ("G4", "Evaluation\nobject"),
    ("G5", "Evaluators"),
    ("G6", "Target\nusers"),
    ("G7", "AI\nfunction"),
]

# Place G1 at the top and continue clockwise through G7.
segment = 360 / len(factors)
for i, (code, label) in enumerate(factors):
    centre_angle = 90 - i * segment
    theta1 = centre_angle - segment / 2
    theta2 = centre_angle + segment / 2
    ax.add_patch(
        Wedge(
            (cx, cy),
            context_outer,
            theta1,
            theta2,
            width=context_outer - context_inner,
            facecolor=context_fills[i],
            edgecolor="white",
            linewidth=1.8,
        )
    )
    angle = math.radians((theta1 + theta2) / 2)
    radius = (context_outer + context_inner) / 2
    x = cx + radius * math.cos(angle)
    y = cy + radius * math.sin(angle)
    ax.text(
        x,
        y + 0.075,
        code,
        ha="center",
        va="center",
        fontsize=7.7,
        weight="bold",
        color="#355965",
    )
    ax.text(
        x,
        y - 0.13,
        label,
        ha="center",
        va="center",
        fontsize=6.8,
        color="#30383B",
        linespacing=1.0,
    )

# Fine boundaries retain legibility in greyscale print.
ax.add_patch(Circle((cx, cy), context_outer, fill=False, edgecolor=context_edge, linewidth=1.0))
ax.add_patch(Circle((cx, cy), context_inner, fill=False, edgecolor=context_edge, linewidth=0.9))

# Four nested levels express increasing operational specificity.
radii = [2.62, 1.96, 1.32, 0.69]
fills = ["#EAF1F6", "#E4F0EF", "#EAF1E1", "#F2E7F0"]
edges = ["#416F8C", "#3E8079", "#66863C", "#92507F"]

for r, face, edge in zip(radii, fills, edges):
    ax.add_patch(Circle((cx, cy), r, facecolor=face, edgecolor=edge, linewidth=1.15))

# Labels are placed on the upper arc of each ring, with concise functional descriptions
# on the lower arc. This follows the compact labelling used in evaluation frameworks.
upper_labels = [
    (2.25, "EVALUATION QUESTION", edges[0], 9.2),
    (1.61, "EVALUATION DIMENSIONS", edges[1], 8.8),
    (0.99, "SUBJECTIVE INDICATORS", edges[2], 8.5),
]
for y, label, color, size in upper_labels:
    ax.text(cx, cy + y, label, ha="center", va="center", fontsize=size, weight="bold", color=color)

lower_labels = [
    (-2.22, "frames what the evaluation seeks to establish", edges[0]),
    (-1.57, "organize perceived effects into conceptual domains", edges[1]),
    (-0.94, "specify the attributes to be assessed", edges[2]),
]
for y, label, color in lower_labels:
    ax.text(cx, cy + y, label, ha="center", va="center", fontsize=7.1, color=color)

ax.text(cx, cy + 0.12, "TOOLS", ha="center", va="center", fontsize=10.0, weight="bold", color=edges[3])
ax.text(
    cx,
    cy - 0.18,
    "elicit and record\njudgments",
    ha="center",
    va="center",
    fontsize=7.0,
    color="#5B4154",
    linespacing=1.1,
)

# A restrained inward arrow clarifies the ordered relationship. It remains inside
# the operationalization structure so that it is not mistaken for a causal arrow
# from any single contextual factor.
ax.add_patch(
    FancyArrowPatch(
        (-2.34, 0.20),
        (-0.76, 0.20),
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=0.9,
        color="#5F6A6E",
    )
)
ax.text(
    -1.55,
    0.43,
    "increasing operational specificity",
    ha="center",
    va="center",
    fontsize=6.8,
    color="#4F585C",
    style="italic",
)

# The figure uses a journal-style external label rather than an infographic title.
ax.text(
    0,
    3.63,
    "CONTEXTUAL FACTORS",
    ha="center",
    va="center",
    fontsize=8.4,
    weight="bold",
    color="#355965",
    bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.5},
)
ax.text(
    0,
    -3.63,
    "Contextual factors condition the specification and alignment of all operationalization levels",
    ha="center",
    va="center",
    fontsize=7.0,
    color="#59666B",
    style="italic",
    bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.0},
)

stem = OUT / "figXX_evaluation_practice_structure_v2"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.04)

plt.close(fig)

