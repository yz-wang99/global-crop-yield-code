"""Create Figure 4: Russia and Ukraine validation yields and lead-time errors.

This figure is self-contained: its reported yields and percentage errors are
embedded arrays rather than files loaded at runtime. The four yield arrays use
the ``yield_categories`` order (Maize, Soybean, Rice, Wheat). Each error list
uses the nine lead times in ``error_labels`` (0--128 days before harvest in
16-day steps). ``np.nan`` intentionally denotes a crop/lead-time combination
without a plotted estimate; the error-panel helper removes those points.

For another country pair or assessment year, update both countries' yield
arrays, their complete error dictionaries, titles, axis limits, and legends
as one coherent dataset. The script exports PDF, EPS, TIFF, and PNG files to
``output_dir``.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from pathlib import Path


# ============================================================
# Nature two-column figure dimensions
# Match Fig. 3 exactly: 180 mm × 125 mm
# ============================================================
MM_TO_INCH = 1 / 25.4

FIG_WIDTH_MM = 180
FIG_HEIGHT_MM = 125


# ============================================================
# Global plot settings
# ============================================================
plt.rcParams.update({
    # Fonts
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Arial",
        "Helvetica",
        "DejaVu Sans"
    ],

    # Use DejaVu Sans for math to avoid missing superscript minus signs
    "mathtext.fontset": "dejavusans",

    # Final figure font size
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 7,

    # Axis styling
    "axes.linewidth": 0.7,
    "axes.unicode_minus": True,

    # Legend
    "legend.frameon": False,

    # Embed fonts in PDF/EPS
    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    # Background
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white"
})


# ============================================================
# Yield data
# Unit: kg/ha
# ============================================================
# Required order for each actual/estimated yield array below.
yield_categories = [
    "Maize",
    "Soybean",
    "Rice",
    "Wheat"
]


# Russia
actual_yield_russia = [
    5998.9,
    1788.8,
    5423.1,
    3550.8
]

estimated_yield_russia = [
    5535.05,
    1503.259,
    5843.809,
    2672.532
]


# Ukraine
actual_yield_ukraine = [
    6349.1,
    2255.0,
    4414.3,
    3924.9
]

estimated_yield_ukraine = [
    5442.475,
    1852.037,
    5053.874,
    3238.035
]


# ============================================================
# Russia estimation-error data
# Unit: %
# ============================================================
errors_russia = {
    "Wheat": [
        -24.7344,
        -22.8916,
        -25.7125,
        -27.7261,
        -28.3271,
        -29.8246,
        -30.1891,
        -30.2113,
        -30.5116
    ],

    "Rice": [
        7.757719,
        5.758584,
        14.23789,
        13.59897,
        12.87367,
        13.02471,
        10.90364,
        8.985266,
        2.435055
    ],

    "Soybean": [
        -15.9627,
        -16.8130,
        -16.7654,
        -19.4880,
        -20.9912,
        -23.3240,
        -22.7069,
        -23.8390,
        np.nan
    ],

    "Maize": [
        -7.73225,
        -6.62202,
        -6.90323,
        7.991224,
        -8.87601,
        -11.6126,
        -11.7914,
        -15.3237,
        -24.3279
    ]
}


# ============================================================
# Ukraine estimation-error data
# Unit: %
# ============================================================
errors_ukraine = {
    "Wheat": [
        -17.5002,
        -16.4582,
        -17.1799,
        -13.9936,
        -12.9795,
        -13.1288,
        -10.8712,
        -10.3107,
        -8.84492
    ],

    "Rice": [
        14.48867,
        15.08475,
        16.38472,
        16.54859,
        15.10138,
        13.47087,
        9.895039,
        1.670392,
        np.nan
    ],

    "Soybean": [
        -17.8697,
        -17.8102,
        -20.9452,
        -21.5814,
        -25.3009,
        -26.0114,
        -27.0672,
        -25.5310,
        np.nan
    ],

    "Maize": [
        -14.2796,
        -13.7862,
        -14.5246,
        -9.95869,
        -16.8910,
        -20.7141,
        -25.3815,
        -24.9026,
        -14.6183
    ]
}


# ============================================================
# Days before harvest
# ============================================================
error_labels = [
    "0",
    "16",
    "32",
    "48",
    "64",
    "80",
    "96",
    "112",
    "128"
]

x_values = np.asarray(
    error_labels,
    dtype=float
)


# ============================================================
# Style settings
# ============================================================

# Bar colors
bar_colors = {
    "estimated": "#62B197",
    "actual": "#F4A259"
}

# Crop order in scatter plots
error_categories = [
    "Wheat",
    "Rice",
    "Soybean",
    "Maize"
]

# Scatter-plot colors
point_colors = [
    "#9891A3",
    "#E4937C",
    "#E2B6AE",
    "#8BAE9A"
]

# Scatter-plot markers
point_markers = [
    "o",
    "s",
    "D",
    "^"
]

# Horizontal offsets for the same time point
x_jitter = np.array([
    -5.0,
    -2.5,
    2.5,
    5.0
])


# ============================================================
# Create figure
# ============================================================
fig = plt.figure(
    figsize=(
        FIG_WIDTH_MM * MM_TO_INCH,
        FIG_HEIGHT_MM * MM_TO_INCH
    )
)

gs = fig.add_gridspec(
    nrows=2,
    ncols=4,
    height_ratios=[1, 1]
)


# ============================================================
# Common axis formatting
# ============================================================
def format_axis(ax):
    """Apply common axis styling."""

    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        length=2.8,
        width=0.7,
        pad=1.5
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)


# ============================================================
# Horizontal yield bar-chart function
# ============================================================
def plot_yield_panel(
        ax,
        estimated_values,
        actual_values,
        title,
        x_limit
):
    """Draw a horizontal yield bar chart."""

    y_positions = np.arange(
        len(yield_categories)
    )

    bar_height = 0.34

    # Estimated yield
    ax.barh(
        y_positions + bar_height / 2,
        estimated_values,

        height=bar_height,

        label="Estimated yield",

        color=bar_colors["estimated"],
        edgecolor="black",
        linewidth=0.45
    )

    # Actual yield
    ax.barh(
        y_positions - bar_height / 2,
        actual_values,

        height=bar_height,

        label="Actual yield",

        color=bar_colors["actual"],
        edgecolor="black",
        linewidth=0.45
    )

    ax.set_yticks(
        y_positions,
        labels=yield_categories
    )

    # Use the same axis range for both yield panels
    ax.set_xlim(
        0,
        x_limit
    )

    ax.xaxis.set_major_locator(
        mtick.MultipleLocator(2000)
    )

    ax.xaxis.set_major_formatter(
        mtick.StrMethodFormatter("{x:.0f}")
    )

    # Use MathText to avoid missing Unicode superscript characters
    ax.set_xlabel(
        r"Yield (kg ha$^{-1}$)",
        labelpad=2
    )

    ax.set_title(
        title,
        loc="left",
        fontweight="bold",
        pad=3
    )

    # Place the legend at the upper right to reduce overlap with long bars
    ax.legend(
        loc="upper right",
        frameon=False,

        handlelength=1.3,
        handletextpad=0.4,
        labelspacing=0.3,
        borderaxespad=0.35
    )

    format_axis(ax)


# ============================================================
# Estimation-error scatter-plot function
# ============================================================
def plot_error_panel(
        ax,
        error_data,
        title,
        y_limits,
        y_ticks
):
    """Draw a crop estimation-error scatter plot."""

    for crop_index, crop_name in enumerate(
            error_categories
    ):

        crop_errors = np.asarray(
            error_data[crop_name],
            dtype=float
        )

        crop_x = (
            x_values
            + x_jitter[crop_index]
        )

        # Remove data points corresponding to np.nan
        valid_mask = np.isfinite(
            crop_errors
        )

        ax.scatter(
            crop_x[valid_mask],
            crop_errors[valid_mask],

            s=20,
            marker=point_markers[crop_index],

            facecolor=point_colors[crop_index],
            edgecolor="black",
            linewidth=0.4,

            label=crop_name,
            zorder=3
        )

    ax.set_title(
        title,
        loc="left",
        fontweight="bold",
        pad=3
    )

    ax.set_xlabel(
        "Days before harvest",
        labelpad=2
    )

    ax.set_ylabel(
        "Error (%)",
        labelpad=2
    )

    ax.set_xticks(
        x_values,
        labels=error_labels
    )

    # Leave room for offset points at both ends
    ax.set_xlim(
        x_values.min() - 9,
        x_values.max() + 9
    )

    ax.set_ylim(
        y_limits
    )

    ax.set_yticks(
        y_ticks
    )

    ax.yaxis.set_major_formatter(
        mtick.StrMethodFormatter("{x:.0f}")
    )

    # Horizontal gridlines
    ax.set_axisbelow(True)

    ax.grid(
        axis="y",
        linestyle=":",
        linewidth=0.5,
        color="#BFBFBF"
    )

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.01, 0.99),

        ncol=2,
        frameon=False,

        columnspacing=0.9,
        handletextpad=0.3,
        labelspacing=0.35,
        borderaxespad=0.2,

        scatterpoints=1,
        markerscale=1.0
    )

    format_axis(ax)


# ============================================================
# Calculate a shared x-axis maximum for the yield panels
# ============================================================
all_yield_values = (
    actual_yield_russia
    + estimated_yield_russia
    + actual_yield_ukraine
    + estimated_yield_ukraine
)

yield_x_limit = (
    np.ceil(
        max(all_yield_values) / 1000
    ) * 1000
)


# ============================================================
# Panel a: Russia yields
# ============================================================
ax0 = fig.add_subplot(
    gs[0, 0:2]
)

plot_yield_panel(
    ax=ax0,
    estimated_values=estimated_yield_russia,
    actual_values=actual_yield_russia,
    title="a. Yields for Russia",
    x_limit=yield_x_limit
)


# ============================================================
# Panel b: Ukraine yields
# ============================================================
ax1 = fig.add_subplot(
    gs[0, 2:4]
)

plot_yield_panel(
    ax=ax1,
    estimated_values=estimated_yield_ukraine,
    actual_values=actual_yield_ukraine,
    title="b. Yields for Ukraine",
    x_limit=yield_x_limit
)


# ============================================================
# Panel c: Russia estimation errors
# ============================================================
ax2 = fig.add_subplot(
    gs[1, 0:2]
)

plot_error_panel(
    ax=ax2,
    error_data=errors_russia,
    title="c. Estimation errors for Russia",
    y_limits=(-48, 55),
    y_ticks=np.arange(-40, 41, 20)
)


# ============================================================
# Panel d: Ukraine estimation errors
# ============================================================
ax3 = fig.add_subplot(
    gs[1, 2:4]
)

plot_error_panel(
    ax=ax3,
    error_data=errors_ukraine,
    title="d. Estimation errors for Ukraine",
    y_limits=(-48, 55),
    y_ticks=np.arange(-40, 41, 20)
)


# ============================================================
# Figure layout
#
# Use the same parameters as Fig. 3 to keep the layout consistent
# ============================================================
fig.subplots_adjust(
    left=0.085,
    right=0.985,
    bottom=0.07,
    top=0.95,

    wspace=0.70,
    hspace=0.30
)


# ============================================================
# Output directory
# ============================================================
output_dir = Path(
    r"F:\重要文档\NF返修\最终文档\Fig"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Vector PDF
# Recommended as the primary submission file
# ============================================================
pdf_path = output_dir / "Fig_4.pdf"

fig.savefig(
    pdf_path,
    format="pdf",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Vector EPS
# ============================================================
eps_path = output_dir / "Fig_4.eps"

fig.savefig(
    eps_path,
    format="eps",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# 600 dpi TIFF
# Backup raster format
# ============================================================
tiff_path = output_dir / "Fig_4.tiff"

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
# 300 dpi PNG preview
# ============================================================
png_path = output_dir / "Fig_4_preview.png"

fig.savefig(
    png_path,
    format="png",
    dpi=300,
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Output file paths
# ============================================================
print(f"PDF saved to:  {pdf_path}")
print(f"EPS saved to:  {eps_path}")
print(f"TIFF saved to: {tiff_path}")
print(f"PNG saved to:  {png_path}")


# ============================================================
# Display figure
# ============================================================
plt.show()


# Close figure
plt.close(fig)
