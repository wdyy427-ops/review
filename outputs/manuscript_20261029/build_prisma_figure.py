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
        "font.size": 9,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "text.color": "#202020",
    }
)


def box(ax, x, y, w, h, text, face="#FFFFFF", edge="#555555", fontsize=9.2, weight="normal"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.018,rounding_size=0.11",
            linewidth=0.85,
            edgecolor=edge,
            facecolor=face,
        )
    )
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        weight=weight,
        linespacing=1.18,
    )


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=0.85,
            color="#404040",
            shrinkA=0,
            shrinkB=0,
        )
    )


fig, ax = plt.subplots(figsize=(12.0, 5.8))
ax.set_xlim(0, 16)
ax.set_ylim(0.7, 8.25)
ax.axis("off")

header_y = 7.60
header_h = 0.48
main_y = 5.35
main_h = 1.65
exclude_y = 1.55
exclude_h = 2.55
col_x = [0.55, 4.35, 8.15, 11.95]
col_w = 3.00

for x, title in zip(col_x, ["Identification", "Screening", "Eligibility", "Inclusion"]):
    box(ax, x, header_y, col_w, header_h, title, face="#F7F7F7", edge="#4C4C4C", fontsize=10.5, weight="bold")

# Identification
box(
    ax,
    col_x[0],
    main_y,
    col_w,
    main_h,
    "Records identified through\ndatabase searching\n(n = 5,135)",
)
box(
    ax,
    col_x[0],
    exclude_y,
    col_w,
    exclude_h,
    "Records removed before\nscreening (n = 142)\n\nDuplicate records (n = 55)\nNon-peer-reviewed records\n(n = 87)",
    face="#FBEAEA",
    edge="#9B6E6E",
    fontsize=8.6,
)

# Screening
box(
    ax,
    col_x[1],
    main_y,
    col_w,
    main_h,
    "Records screened by title,\nabstract, and keywords\n(n = 4,993)",
)
box(
    ax,
    col_x[1],
    exclude_y,
    col_w,
    exclude_h,
    "Records excluded\n(n = 4,408)\n\nEC1 (n = 228)\nEC2 (n = 3,837)\nEC3 (n = 211)\nEC4 (n = 132)",
    face="#FBEAEA",
    edge="#9B6E6E",
    fontsize=8.8,
)

# Eligibility
box(
    ax,
    col_x[2],
    main_y,
    col_w,
    main_h,
    "Full-text articles assessed\nfor eligibility\n(n = 585)\nInclude: 82  ·  Unclear: 503",
    fontsize=8.9,
)
box(
    ax,
    col_x[2],
    exclude_y,
    col_w,
    exclude_h,
    "Full-text articles excluded\n(n = 445)\n\nEC1 (n = 118)\nEC2 (n = 239)\nEC3 (n = 23)\nEC4 (n = 65)",
    face="#FBEAEA",
    edge="#9B6E6E",
    fontsize=8.8,
)

# Inclusion and post-eligibility temporal restriction
box(
    ax,
    col_x[3],
    main_y,
    col_w,
    main_h,
    "Articles retained after\nfull-text assessment\n(n = 140)",
)
box(
    ax,
    col_x[3] + 0.18,
    3.55,
    col_w - 0.36,
    0.78,
    "Articles published in 2017–2021\nremoved (n = 15)",
    face="#FBEAEA",
    edge="#9B6E6E",
    fontsize=8.3,
)
box(
    ax,
    col_x[3],
    1.62,
    col_w,
    1.20,
    "Studies included in the\nfinal corpus (n = 125)\n2022–2026",
    face="#EDF6E7",
    edge="#6D8A5E",
    fontsize=9.1,
    weight="bold",
)

# Main horizontal flow
flow_y = main_y + main_h / 2
for i in range(3):
    arrow(ax, col_x[i] + col_w, flow_y, col_x[i + 1], flow_y)

# Exclusion branches
for i in range(3):
    x_mid = col_x[i] + col_w / 2
    arrow(ax, x_mid, main_y, x_mid, exclude_y + exclude_h)

# Temporal restriction and final inclusion
x_mid = col_x[3] + col_w / 2
arrow(ax, x_mid, main_y, x_mid, 4.33)
arrow(ax, x_mid, 3.55, x_mid, 2.82)

# Round labels improve traceability without competing with the PRISMA phases.
ax.text(col_x[0] + col_w / 2, 4.83, "Round 1", ha="center", va="center", fontsize=7.7, color="#666666", style="italic")
ax.text(col_x[1] + col_w / 2, 4.83, "Round 2", ha="center", va="center", fontsize=7.7, color="#666666", style="italic")
ax.text(col_x[2] + col_w / 2, 4.83, "Round 3", ha="center", va="center", fontsize=7.7, color="#666666", style="italic")

stem = OUT / "figXX_prisma_data_collection"
for ext in ("png", "pdf", "svg"):
    fig.savefig(stem.with_suffix(f".{ext}"), dpi=400, bbox_inches="tight", pad_inches=0.05)

plt.close(fig)

