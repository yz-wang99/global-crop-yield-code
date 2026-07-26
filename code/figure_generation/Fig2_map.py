"""Create Figure 2: lead-time and feature-set performance comparisons.

All values are embedded, publication-specific R2 results. ``days`` gives the
nine prediction lead times (0--128 days before harvest in 16-day increments).
For each crop, the three arrays in ``data`` must have the same length and
correspond, in order, to the three labels: means only; means plus standard
deviations; and all mean, standard-deviation, and five frequency features.
Replace the full data block and labels together when plotting a different
validation experiment. The script writes PDF, EPS, TIFF, and PNG files to
``output_dir``; it reads no external input files.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
from pathlib import Path


# ============================================================
# Nature Research Journals figure dimensions
# Two-column width: 180 mm
# ============================================================
MM_TO_INCH = 1 / 25.4

FIG_WIDTH_MM = 180
FIG_HEIGHT_MM = 145


# ============================================================
# Global plot settings
# ============================================================
plt.rcParams.update({
    # Fonts
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],

    # Nature final figure font size is typically 5–7 pt
    "font.size": 6,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 7,

    # Axes and legend
    "axes.linewidth": 0.7,
    "legend.frameon": False,

    # Embed TrueType/Type 42 fonts in PDF and EPS
    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    # White background
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white"
})


# ============================================================
# X-axis
# ============================================================
# Ordered prediction horizons used as the x axis for every crop panel.
days = np.array([0, 16, 32, 48, 64, 80, 96, 112, 128])


# ============================================================
# Crop names
# ============================================================
crops = [
    "a. Wheat",
    "b. Rice",
    "c. Soybean",
    "d. Maize"
]


# ============================================================
# Data
# ============================================================
data = {
    "a. Wheat": [
        [
            0.866081817,
            0.865263635,
            0.858506483,
            0.851662100,
            0.835406955,
            0.831191111,
            0.832289245,
            0.828245999,
            0.854436908
        ],
        [
            0.882674337,
            0.883198406,
            0.875535892,
            0.871609594,
            0.862734980,
            0.862049909,
            0.842401166,
            0.850470395,
            0.864339259
        ],
        [
            0.906074565,
            0.905403185,
            0.904188852,
            0.900157560,
            0.895163575,
            0.891241761,
            0.873892597,
            0.878910610,
            0.872999239
        ]
    ],

    "b. Rice": [
        [
            0.759302301,
            0.764014093,
            0.768900435,
            0.762407399,
            0.767351832,
            0.766752027,
            0.782270068,
            0.783399589,
            0.688329392
        ],
        [
            0.801543723,
            0.810017298,
            0.810336050,
            0.810445683,
            0.804421252,
            0.802139730,
            0.791203519,
            0.799261959,
            0.751625237
        ],
        [
            0.808070605,
            0.815106090,
            0.826111373,
            0.821178020,
            0.817984000,
            0.816084424,
            0.813922963,
            0.817544895,
            0.781801944
        ]
    ],

    "c. Soybean": [
        [
            0.626065386,
            0.617190800,
            0.647308218,
            0.633320822,
            0.629056748,
            0.653181385,
            0.633539210,
            0.635589310,
            0.681555813
        ],
        [
            0.692866828,
            0.683159733,
            0.684675270,
            0.661206511,
            0.656906121,
            0.669715708,
            0.688579232,
            0.723310863,
            0.713921549
        ],
        [
            0.711892554,
            0.702659692,
            0.706659315,
            0.708881665,
            0.703789557,
            0.711287416,
            0.713835048,
            0.720745036,
            0.724211834
        ]
    ],

    "d. Maize": [
        [
            0.815921721,
            0.819308422,
            0.819652513,
            0.814745854,
            0.814947381,
            0.813047032,
            0.728631179,
            0.754630507,
            0.862074044
        ],
        [
            0.878398453,
            0.868759292,
            0.864380284,
            0.859142060,
            0.846790621,
            0.835917801,
            0.784232678,
            0.830531053,
            0.872201163
        ],
        [
            0.888954177,
            0.883129699,
            0.878925710,
            0.874217722,
            0.877249616,
            0.862512670,
            0.872762970,
            0.884399995,
            0.870412700
        ]
    ]
}


# ============================================================
# Legend labels
# ============================================================
labels = [
    "Using the mean of variables",
    "Using the mean and standard deviation of variables",
    "Using the mean, standard deviation, and frequencies of variables"
]


# ============================================================
# Line styles, colors, and markers
# Use color, line style, and markers for grayscale distinction.
# ============================================================
colors = [
    "#0072B2",
    "#009E73",
    "#D55E00"
]

markers = [
    "o",
    "s",
    "^"
]

line_styles = [
    "-",
    "--",
    ":"
]


# ============================================================
# Create figure
# Fixed final size: 180 mm × 145 mm
# ============================================================
fig, axes = plt.subplots(
    nrows=2,
    ncols=2,
    figsize=(
        FIG_WIDTH_MM * MM_TO_INCH,
        FIG_HEIGHT_MM * MM_TO_INCH
    )
)

axes = axes.flatten()


# ============================================================
# Draw four panels
# ============================================================
for i, crop in enumerate(crops):

    ax = axes[i]

    for j in range(3):

        ax.plot(
            days,
            data[crop][j],

            color=colors[j],
            linestyle=line_styles[j],
            marker=markers[j],

            linewidth=1.65,
            markersize=4.5,

            markerfacecolor=colors[j],
            markeredgecolor="white",
            markeredgewidth=0.35,

            label=labels[j]
        )

    # All values in the current panel
    all_values = np.asarray(data[crop], dtype=float).ravel()

    # Panel title, for example, a Wheat
    panel_title = crop.replace(". ", "  ", 1)

    ax.set_title(
        panel_title,
        loc="left",
        fontweight="bold",
        pad=3
    )

    # Axis labels
    ax.set_xlabel(
        "Days before harvest",
        labelpad=2
    )

    ax.set_ylabel(
        r"R²",
        labelpad=2
    )

    # Keep the original independent y-axis range for each panel
    ax.set_ylim(
        all_values.min() - 0.015,
        all_values.max() + 0.015
    )

    # Major y-axis tick interval
    ax.yaxis.set_major_locator(
        MultipleLocator(0.03)
    )

    # X-axis ticks
    ax.set_xticks(days)
    ax.set_xticklabels([str(day) for day in days])

    # Tick marks
    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        length=2.5,
        width=0.7,
        pad=1.5
    )

    # Hide the top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Left and bottom spine widths
    ax.spines["left"].set_linewidth(0.6)
    ax.spines["bottom"].set_linewidth(0.6)


# ============================================================
# Create a shared figure legend
# ncol=2 automatically arranges items in two rows
# ============================================================
handles, legend_labels = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    legend_labels,

    loc="lower center",
    bbox_to_anchor=(0.5, 0.005),

    ncol=2,

    frameon=False,
    handlelength=2.6,
    handletextpad=0.5,
    columnspacing=1.3,
    labelspacing=0.7
)


# ============================================================
# Adjust subplot layout
# Reserve space for the bottom legend
# ============================================================
fig.subplots_adjust(
    left=0.09,
    right=0.985,
    bottom=0.14,
    top=0.955,
    wspace=0.28,
    hspace=0.325
)


# ============================================================
# Output path
# ============================================================
output_dir = Path(r"F:\重要文档\NF返修\最终文档\Fig")

# Create the output directory if needed
output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Export PDF
# Recommended vector format for line charts, bar charts, and diagrams
# Do not use bbox_inches="tight" to preserve final dimensions
# ============================================================
pdf_path = output_dir / "Fig_2.pdf"

fig.savefig(
    pdf_path,
    format="pdf",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Export EPS
# Backup vector format
# ============================================================
eps_path = output_dir / "Fig_2.eps"

fig.savefig(
    eps_path,
    format="eps",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Export high-resolution TIFF
# Backup version when a raster file is required
# Use at least 600 dpi for composite figures
# ============================================================
tiff_path = output_dir / "Fig_2.tiff"

fig.savefig(
    tiff_path,
    format="tiff",
    dpi=600,
    facecolor="white",
    edgecolor="white",
    pil_kwargs={
        "compression": "tiff_lzw"
    }
)


# ============================================================
# Export PNG preview
# PNG is for viewing or documents, not the primary submission file
# ============================================================
png_path = output_dir / "Fig_2_preview.png"

fig.savefig(
    png_path,
    format="png",
    dpi=300,
    facecolor="white",
    edgecolor="white"
)


# Output file paths
print(f"PDF saved to:  {pdf_path}")
print(f"EPS saved to:  {eps_path}")
print(f"TIFF saved to: {tiff_path}")
print(f"PNG saved to:  {png_path}")


# Display figure
plt.show()


# Close the figure to free memory during batch plotting
plt.close(fig)
