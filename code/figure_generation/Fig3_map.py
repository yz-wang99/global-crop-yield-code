"""Create Figure 3: global validation yields and lead-time errors.

All inputs are embedded numeric arrays, so this script is self-contained.
``yield_categories`` fixes the order shared by each actual/estimated yield
array: Maize, Soybean, Rice, Wheat. In contrast, ``errors_2019`` and
``errors_2020`` are dictionaries keyed by crop name; each error list follows
the nine 0--128-day lead times in ``error_labels``. Values are percentages.
When updating a year, replace the paired actual/estimated arrays, both error
dictionaries, panel titles, and any appropriate y-axis limits together.

PDF and EPS are vector exports; TIFF (600 dpi) and PNG (300 dpi) are raster
alternatives. Output files are written to ``output_dir``.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from pathlib import Path


# ============================================================
# Nature two-column figure dimensions
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
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],

    # Final figure font size
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 7,

    # Axes
    "axes.linewidth": 0.7,
    "axes.unicode_minus": True,

    # Legend
    "legend.frameon": False,

    # Embed fonts in vector files
    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    # Background
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white"
})


# ============================================================
# Data: yields of 2019-sown crops
# Unit: kg/ha
# ============================================================
# Required order for all four horizontal-bar yield arrays below.
yield_categories = [
    "Maize",
    "Soybean",
    "Rice",
    "Wheat"
]

actual_yield_2019 = [
    7091.2,
    1772.2,
    10030.8,
    1691.7
]

estimated_yield_2019 = [
    6454.05,
    1816.042,
    9556.176,
    1902.833
]


# ============================================================
# Data: yields of 2020-sown crops
# Unit: kg/ha
# ============================================================
actual_yield_2020 = [
    6336.883,
    1718.1,
    9382,
    1468.1
]

estimated_yield_2020 = [
    5956.467,
    1883.09,
    9546.533,
    1881.325
]


# ============================================================
# Data: estimation errors for 2019-sown crops
# Unit: %
# ============================================================
errors_2019 = {
    "Wheat": [
        12.48051,
        12.17375,
        9.980872,
        7.565733,
        7.406828,
        7.641097,
        7.733202,
        4.720064,
        1.975886
    ],

    "Soybean": [
        2.473871,
        -0.73836,
        -1.43285,
        -1.24295,
        0.169736,
        -1.14391,
        -5.61952,
        -7.01081,
        -12.7987
    ],

    "Rice": [
        -4.73167,
        -6.02777,
        -5.96811,
        -6.86255,
        -8.17483,
        -8.40986,
        -8.43577,
        -8.80624,
        -8.32335
    ],

    "Maize": [
        -10.6374,
        -10.4474,
        -9.15134,
        -8.88143,
        -8.42632,
        -10.5011,
        -8.61035,
        -9.85401,
        -7.46932
    ]
}


# ============================================================
# Data: estimation errors for 2020-sown crops
# Unit: %
# ============================================================
errors_2020 = {
    "Wheat": [
        28.14694,
        26.02263,
        29.13404,
        25.99898,
        28.31527,
        40.85756,
        32.07057,
        33.10939,
        30.98506
    ],

    "Rice": [
        1.753705,
        -0.94077,
        -0.18717,
        -0.90633,
        -1.54835,
        -1.5214,
        -2.06274,
        -2.84351,
        -1.1589
    ],

    "Soybean": [
        9.603047,
        8.468794,
        9.039722,
        7.696541,
        9.636594,
        9.780577,
        7.577721,
        6.705416,
        6.00001
    ],

    "Maize": [
        -10.8607,
        -11.603,
        -11.4571,
        -11.9406,
        -11.1492,
        -11.8621,
        -10.6217,
        -8.55498,
        -7.59619
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

x_values = np.asarray(error_labels, dtype=float)


# ============================================================
# Colors and plot styles
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

# Crop colors
point_colors = [
    "#9891A3",
    "#E4937C",
    "#E2B6AE",
    "#8BAE9A"
]

# Crop markers
point_markers = [
    "o",
    "s",
    "D",
    "^"
]

# Apply small horizontal offsets to prevent same-day point overlap
x_jitter = np.array([
    -4.5,
    -2.25,
    2.25,
    4.5
])


# ============================================================
# Create a figure with fixed physical dimensions
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
# Common axis-style function
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
# Bar-chart drawing function
# ============================================================
def plot_yield_panel(
        ax,
        estimated_values,
        actual_values,
        title,
        x_limit
):
    """Draw a horizontal yield bar chart."""

    y_pos = np.arange(len(yield_categories))
    bar_height = 0.34

    # Estimated yield
    ax.barh(
        y_pos + bar_height / 2,
        estimated_values,
        height=bar_height,
        label="Estimated yield",
        color=bar_colors["estimated"],
        edgecolor="black",
        linewidth=0.45
    )

    # Actual yield
    ax.barh(
        y_pos - bar_height / 2,
        actual_values,
        height=bar_height,
        label="Actual yield",
        color=bar_colors["actual"],
        edgecolor="black",
        linewidth=0.45
    )

    ax.set_yticks(
        y_pos,
        labels=yield_categories
    )

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

    ax.legend(
        loc="lower right",
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

    for crop_index, crop_name in enumerate(error_categories):

        ax.scatter(
            x_values + x_jitter[crop_index],
            error_data[crop_name],

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

    # Leave room for jittered points at both ends
    ax.set_xlim(
        x_values.min() - 8,
        x_values.max() + 8
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

    # Horizontal reference grid
    # Avoid transparency to prevent EPS export warnings
    ax.grid(
        axis="y",
        linestyle=":",
        linewidth=0.5,
        color="#BFBFBF",
        zorder=0
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
# Use the same x-axis range for both yield panels
# This allows direct comparison of 2019 and 2020
# ============================================================
all_yield_values = (
    actual_yield_2019
    + estimated_yield_2019
    + actual_yield_2020
    + estimated_yield_2020
)

yield_x_limit = (
    np.ceil(max(all_yield_values) / 1000) * 1000
)


# ============================================================
# Panel a: yields of 2019-sown crops
# ============================================================
ax0 = fig.add_subplot(
    gs[0, 0:2]
)

plot_yield_panel(
    ax=ax0,
    estimated_values=estimated_yield_2019,
    actual_values=actual_yield_2019,
    title="a. Yields of 2019-sown crops",
    x_limit=yield_x_limit
)


# ============================================================
# Panel b: yields of 2020-sown crops
# ============================================================
ax1 = fig.add_subplot(
    gs[0, 2:4]
)

plot_yield_panel(
    ax=ax1,
    estimated_values=estimated_yield_2020,
    actual_values=actual_yield_2020,
    title="b. Yields of 2020-sown crops",
    x_limit=yield_x_limit
)


# ============================================================
# Panel c: estimation errors of 2019-sown crops
# ============================================================
ax2 = fig.add_subplot(
    gs[1, 0:2]
)

plot_error_panel(
    ax=ax2,
    error_data=errors_2019,
    title="c. Estimation errors of 2019-sown crops",
    y_limits=(-30, 45),
    y_ticks=np.arange(-20, 41, 20)
)


# ============================================================
# Panel d: estimation errors of 2020-sown crops
# ============================================================
ax3 = fig.add_subplot(
    gs[1, 2:4]
)

plot_error_panel(
    ax=ax3,
    error_data=errors_2020,
    title="d. Estimation errors of 2020-sown crops",
    y_limits=(-35, 66),
    y_ticks=np.arange(-20, 61, 20)
)


# ============================================================
# Figure layout
#
# Do not use bbox_inches="tight" to preserve the specified figure dimensions
# ============================================================
fig.subplots_adjust(
    left=0.085,
    right=0.985,
    bottom=0.07,
    top=0.96,

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
# Export vector PDF
# Recommended as the primary submission file
# ============================================================
pdf_path = output_dir / "Fig_3.pdf"

fig.savefig(
    pdf_path,
    format="pdf",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Export vector EPS
# ============================================================
eps_path = output_dir / "Fig_3.eps"

fig.savefig(
    eps_path,
    format="eps",
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Export 600 dpi TIFF
# Backup version when a journal requires a raster file
# ============================================================
tiff_path = output_dir / "Fig_3.tiff"

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
# PNG is not recommended as the final vector submission file
# ============================================================
png_path = output_dir / "Fig_3_preview.png"

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


# Close the figure to free memory during batch plotting
plt.close(fig)
