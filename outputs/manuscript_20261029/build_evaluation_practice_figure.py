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
        "font.size": 8.5,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#222222",
    }
)


def rounded_box(ax, x, y, w, h, face, edge, title, subtitle, title_color="#222222"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.018",
            linewidth=0.9,
            edgecolor=edge,
            facecolor=face,
        )
    )
    ax.text(
        x + w / 2,
        y + h * 0.63,
        title,
        ha="center",
        va="center",
        fontsize=9.1,
        weight="bold",
        color=title_color,
    )
    ax.text(
        x + w / 2,
        y + h * 0.31,
        subtitle,
        ha="center",
        va="center",
        fontsize=7.0,
        color="#4D4D4D",
        linespacing=1.15,
    )


fig = plt.figure(figsize=(7.2, 3.95))
ax = fig.add_axes([0.015, 0.025, 0.97, 0.95])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Outer boundary: the two internal layers jointly constitute the practice structure.
ax.add_patch(
    FancyBboxPatch(
        (0.018, 0.035),
        0.964,
        0.925,
        boxstyle="round,pad=0.012,rounding_size=0.022",
        linewidth=1.0,
        edgecolor="#465A67",
        facecolor="#FFFFFF",
    )
)
ax.text(
    0.045,
    0.922,
    "Core structure of an evaluation practice",
    ha="left",
    va="center",
    fontsize=11.2,
    weight="bold",
    color="#263844",
)

# Context layer.
ax.add_patch(
    FancyBboxPatch(
        (0.045, 0.655),
        0.91,
        0.205,
        boxstyle="round,pad=0.010,rounding_size=0.018",
        linewidth=0.75,
        edgecolor="#9CB3BD",
        facecolor="#F1F6F7",
    )
)
ax.text(
    0.065,
    0.823,
    "Contextual factors",
    ha="left",
    va="center",
    fontsize=9.4,
    weight="bold",
    color="#355C68",
)

factors = [
    ("G1", "Evaluation\npurpose"),
    ("G2", "Design\ndomain"),
    ("G3", "Design\nstage"),
    ("G4", "Evaluation\nobject"),
    ("G5", "Evaluators"),
    ("G6", "Target\nusers"),
    ("G7", "AI\nfunction"),
]
start_x = 0.065
gap = 0.012
pill_w = (0.87 - gap * 6) / 7
for i, (code, label) in enumerate(factors):
    x = start_x + i * (pill_w + gap)
    ax.add_patch(
        FancyBboxPatch(
            (x, 0.685),
            pill_w,
            0.102,
            boxstyle="round,pad=0.006,rounding_size=0.014",
            linewidth=0.65,
            edgecolor="#7EA0AC",
            facecolor="#FFFFFF",
        )
    )
    ax.text(
        x + pill_w / 2,
        0.752,
        code,
        ha="center",
        va="center",
        fontsize=7.5,
        weight="bold",
        color="#355C68",
    )
    ax.text(
        x + pill_w / 2,
        0.715,
        label,
        ha="center",
        va="center",
        fontsize=6.7,
        color="#333333",
        linespacing=1.05,
    )

# Context-to-operationalization relation. Multiple arrows indicate distributed influence,
# while the wording avoids making an untested causal claim.
ax.text(
    0.5,
    0.615,
    "shape the selection and alignment of",
    ha="center",
    va="center",
    fontsize=7.7,
    color="#52656D",
    style="italic",
)
for x in (0.18, 0.39, 0.61, 0.82):
    ax.add_patch(
        FancyArrowPatch(
            (x, 0.655),
            (x, 0.535),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=0.75,
            color="#7A919A",
        )
    )

# Operationalization layer.
ax.add_patch(
    FancyBboxPatch(
        (0.045, 0.135),
        0.91,
        0.375,
        boxstyle="round,pad=0.010,rounding_size=0.018",
        linewidth=0.75,
        edgecolor="#B7BCC2",
        facecolor="#FAFAFA",
    )
)
ax.text(
    0.065,
    0.472,
    "Evaluation operationalization",
    ha="left",
    va="center",
    fontsize=9.4,
    weight="bold",
    color="#3A3A3A",
)
ax.text(
    0.935,
    0.472,
    "progressive specification and operationalization",
    ha="right",
    va="center",
    fontsize=7.2,
    color="#666666",
    style="italic",
)

components = [
    (
        "Evaluation question",
        "What should the\nevaluation establish?",
        "#EDF4FA",
        "#4477AA",
    ),
    (
        "Evaluation dimensions",
        "Which perceived-effect\ndomains are evaluated?",
        "#EDF7F4",
        "#3B8C7A",
    ),
    (
        "Subjective indicators",
        "Which attributes are\nassessed?",
        "#F2F7EA",
        "#6C963C",
    ),
    (
        "Tools",
        "How are judgments elicited\nand recorded?",
        "#F7EFF7",
        "#AA4499",
    ),
]

box_y = 0.21
box_h = 0.19
box_w = 0.197
box_x = [0.067, 0.29, 0.513, 0.736]
for x, (title, subtitle, face, edge) in zip(box_x, components):
    rounded_box(ax, x, box_y, box_w, box_h, face, edge, title, subtitle, edge)

for x1, x2 in zip(box_x[:-1], box_x[1:]):
    ax.add_patch(
        FancyArrowPatch(
            (x1 + box_w + 0.003, box_y + box_h / 2),
            (x2 - 0.003, box_y + box_h / 2),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=0.9,
            color="#6C7377",
        )
    )

ax.text(
    0.5,
    0.078,
    "Contextual fit and internal alignment jointly support rigorous subjective evaluation of perceived effects.",
    ha="center",
    va="center",
    fontsize=7.6,
    color="#4B555A",
)

stem = OUT / "figXX_evaluation_practice_structure"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.04)

plt.close(fig)

