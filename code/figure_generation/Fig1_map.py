"""Create Figure 1: global country-level yield-estimation errors and examples.

External input: a polygon shapefile (all component files with the same stem
must be present) in geographic coordinates or with a valid CRS. It must have
one feature per country and these four numeric error fields:
``wheat_erro``, ``rice_error``, ``soybean_er``, and ``maize_erro``. The short
field names reflect the 10-character limit of a Shapefile DBF table. Values
are percentage errors; zero is rendered as the grey ``Not production
countries`` category, whereas non-zero values are classified with the fixed
boundaries in ``boundaries``. Replace the shapefile path, error fields,
performance metrics, and embedded country-yield arrays together when plotting
another test year.

The script saves PDF, EPS, TIFF, and PNG versions to ``output_dir``. Map
polygons may be rasterized inside the vector exports to reduce file size;
labels, axes, bars, and legends remain vector objects.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from pathlib import Path


# ============================================================
# Nature figure dimensions
#
# Original figsize=(9, 13) with a 9:13 aspect ratio.
# Preserve the original aspect ratio without exceeding the maximum height.
#
# Caption length and recommended maximum height:
# < 50 words：225 mm
# < 150 words：210 mm
# < 300 words：185 mm
# ============================================================
MM_TO_INCH = 1 / 25.4

ORIGINAL_WIDTH_UNITS = 9
ORIGINAL_HEIGHT_UNITS = 13

MAX_WIDTH_MM = 180
MAX_HEIGHT_MM = 210

scale_factor = min(
    MAX_WIDTH_MM / ORIGINAL_WIDTH_UNITS,
    MAX_HEIGHT_MM / ORIGINAL_HEIGHT_UNITS
)

# FIG_WIDTH_MM = ORIGINAL_WIDTH_UNITS * scale_factor
# FIG_HEIGHT_MM = ORIGINAL_HEIGHT_UNITS * scale_factor

FIG_WIDTH_MM = 180
FIG_HEIGHT_MM = 210


print(
    f"Final figure size: "
    f"{FIG_WIDTH_MM:.1f} mm × {FIG_HEIGHT_MM:.1f} mm"
)


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

    # Math font
    "mathtext.fontset": "dejavusans",

    # Nature final figure font size: 5–7 pt
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

    # Embed TrueType/Type 42 fonts in PDF/EPS
    "pdf.fonttype": 42,
    "ps.fonttype": 42,

    # White background
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white"
})


# ============================================================
# File paths
# ============================================================
# This path must point to the ``.shp`` member of a complete Shapefile set.
shapefile_path = Path(
    r"F:\数据集-临时存放\县级估产\特征数据集"
    r"\SHP\global202605_error.shp"
)

output_dir = Path(
    r"F:\重要文档\NF返修\最终文档\Fig"
)

output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Load spatial data
# ============================================================
if not shapefile_path.exists():
    raise FileNotFoundError(
        f"Shapefile does not exist:\n{shapefile_path}"
    )

gdf = gpd.read_file(
    shapefile_path
)

if gdf.empty:
    raise ValueError(
        "The shapefile contains no features."
    )

if gdf.crs is None:
    raise ValueError(
        "The shapefile has no coordinate reference system."
    )

# Convert to geographic coordinates for PlateCarree
if gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(
        epsg=4326
    )

# Draw country outlines once from the merged data boundary.
# This avoids inconsistent widths from duplicate boundaries.
country_boundaries = gdf.geometry.boundary.unary_union


# ============================================================
# Crop fields and panel titles
# ============================================================
crops = [
    "wheat_erro",
    "rice_error",
    "soybean_er",
    "maize_erro"
]

titles = [
    "a. Wheat",
    "b. Rice",
    "c. Soybean",
    "d. Maize"
]


# Check required fields
missing_columns = [
    column
    for column in crops
    if column not in gdf.columns
]

if missing_columns:
    raise KeyError(
        "The following fields are missing from the shapefile: "
        + ", ".join(missing_columns)
    )


# ============================================================
# Performance metrics
# ============================================================
r2 = [
    0.91,
    0.81,
    0.71,
    0.89
]

rmse = [
    640.7,
    963.3,
    472.7,
    1202.4
]

mae = [
    483.4,
    665.2,
    322.3,
    888.4
]


# ============================================================
# Color classes
# ============================================================
colors = [
    "#67001f",
    "#b2182b",
    "#d6604d",
    "#f4a582",
    "#fddbc7",
    "#d1e5f0",
    "#92c5de",
    "#4393c3",
    "#2166ac",
    "#053061"
]

cmap = mcolors.ListedColormap(
    colors
)

boundaries = [
    -700,
    -40,
    -30,
    -20,
    -10,
    0,
    10,
    20,
    30,
    40,
    700
]

norm = mcolors.BoundaryNorm(
    boundaries,
    cmap.N
)


# ============================================================
# Crop yield data
# ============================================================
yield_data = {
    "wheat": [
        ("Germany", 7819.5, 7464.1809),
        ("Morocco", 900.4, 1668.9366),
        ("France", 6677.6, 6623.1239),
        ("Ukraine", 3795, 3314.4744),
        ("Iran", 1559.1, 2086.6762),
        ("Argentina", 2938.7, 2697.74352),
        ("Türkiye", 2964.7, 2612.91651),
        ("Pakistan", 2867.5, 2926.36077),
        ("Australia", 1468.1, 1881.3252),
        ("Canada", 3537.4, 2930.46427),
        ("Kazakhstan", 1182.5, 1599.07141),
        ("USA", 3341.7, 3274.02013),
        ("China", 5741.6, 4831.79644),
        ("Russian", 2975.9, 2540.63301),
        ("India", 3439.8, 2535.17144)
    ],

    "rice": [
        ("Nepal", 3815.3, 3441.124),
        ("Guinea", 1470, 1426.7299),
        ("Madagascar", 2524.8, 3230.0223),
        ("Brazil", 6610.8, 4728.4219),
        ("Cambodia", 3345.4, 2744.9712),
        ("Pakistan", 3786.3, 3563.39184),
        ("Nigeria", 1947.9, 1807.01265),
        ("Philippines", 4088.8, 3790.05168),
        ("Myanmar", 3865.2, 3980.84406),
        ("Viet Nam", 5921.2, 5041.66125),
        ("Indonesia", 5127.9, 4796.03475),
        ("Thailand", 2899.7, 3813.17996),
        ("Bangladesh", 4808.8, 4324.51846),
        ("China", 7040.2, 6740.93619),
        ("India", 4074.8, 3633.56944)
    ],

    "soybean": [
        ("Serbia", 3174.5, 2712.5669),
        ("Italy", 3926.2, 3166.8435),
        ("South Africa", 1766.7, 1904.161),
        ("Uruguay", 2170.6, 2159.6034),
        ("Nigeria", 1045.2, 945.3797),
        ("Bolivia", 2083.5, 1992.82935),
        ("Ukraine", 2050.6, 1817.60008),
        ("Canada", 3115.1, 2703.66283),
        ("Russian", 1593, 1504.55048),
        ("Paraguay", 3036.2, 2522.37922),
        ("China", 1983.1, 1805.52237),
        ("India", 920.7, 1140.96884),
        ("Argentina", 2919.1, 2724.79286),
        ("USA", 3432.7, 2869.32309),
        ("Brazil", 3275.5, 2811.67296)
    ],

    "maize": [
        ("Philippines", 3179, 2530.6921),
        ("Angola", 1099.3, 1416.7718),
        ("Russian", 5080.5, 4949.175),
        ("Congo", 770.6, 858.3628),
        ("South Africa", 5447.8, 4301.8881),
        ("Indonesia", 5680.4, 4441.53768),
        ("Tanzania", 1597.9, 1906.95462),
        ("Ukraine", 5617.5, 5545.13155),
        ("Nigeria", 2050.6, 2170.39534),
        ("Mexico", 3832.2, 3413.5596),
        ("Argentina", 7553.9, 5382.15181),
        ("India", 3006.1, 2525.11831),
        ("Brazil", 5695.3, 4202.86761),
        ("USA", 10760.5, 9761.1908),
        ("China", 6317.8, 5398.60318)
    ]
}


# ============================================================
# Rasterize map layers
#
# True：
# Rasterize map polygons at 600 dpi in PDF output; text and bars,
# legends, and axes remain vector objects to reduce file size.
#
# False：
# Keep all map polygons as vectors, although the PDF may be very large.
# ============================================================
RASTERIZE_MAP_POLYGONS = True


# ============================================================
# Helper function for GeoDataFrame layers
# ============================================================
def plot_geodataframe_layer(
        layer,
        ax,
        **plot_kwargs
):
    """
    Draw a GeoDataFrame and optionally rasterize newly added polygon collections.
    """

    collection_count_before = len(
        ax.collections
    )

    layer.plot(
        ax=ax,
        **plot_kwargs
    )

    if RASTERIZE_MAP_POLYGONS:
        new_collections = ax.collections[
            collection_count_before:
        ]

        for collection in new_collections:
            collection.set_rasterized(
                True
            )


# ============================================================
# Helper function for bar-chart axis formatting
# ============================================================
def format_bar_axis(ax):
    """Format the right-hand bar-chart axis."""

    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        length=2.5,
        width=0.7,
        pad=1.5
    )

    ax.spines["top"].set_visible(
        True
    )

    ax.spines["right"].set_visible(
        True
    )

    ax.spines["top"].set_linewidth(0.6)
    ax.spines["right"].set_linewidth(0.6)

    ax.spines["left"].set_linewidth(
        0.6
    )

    ax.spines["bottom"].set_linewidth(
        0.6
    )

    ax.xaxis.set_major_locator(
        mticker.MaxNLocator(
            nbins=4,
            min_n_ticks=3
        )
    )

    ax.xaxis.set_major_formatter(
        mticker.StrMethodFormatter(
            "{x:.0f}"
        )
    )


# ============================================================
# Create figure
# Preserve the original 4×2 layout and 2:1 column-width ratio
# ============================================================
fig = plt.figure(
    figsize=(
        FIG_WIDTH_MM * MM_TO_INCH,
        FIG_HEIGHT_MM * MM_TO_INCH
    )
)

gs = fig.add_gridspec(
    nrows=4,
    ncols=2,

    width_ratios=[
        2,
        1
    ],

    # Set margins manually to keep the layout fixed
    left=0.055,
    right=0.955,
    # Move panels and the bottom legend down to reduce excess bottom whitespace.
    # Keep the bottom legend near the edge while retaining top padding.
    bottom=0.105,
    top=0.965,

    wspace=0.28,
    hspace=0.24
)


# Store axes for later layout adjustments
map_axes = []
bar_axes = []


# ============================================================
# Draw four map-and-bar-chart rows
# ============================================================
for i, crop in enumerate(crops):

    # --------------------------------------------------------
    # Left map
    # --------------------------------------------------------
    ax_map = fig.add_subplot(
        gs[i, 0],
        projection=ccrs.PlateCarree()
    )

    map_axes.append(
        ax_map
    )

    # Exclude Antarctica
    ax_map.set_extent(
        [-180, 180, -60, 90],
        crs=ccrs.PlateCarree()
    )

    # Align the map bottom with the right bar-chart bottom;
    # the fixed map aspect ratio makes the map slightly shorter.
    ax_map.set_anchor("S")

    # Map background
    # ax_map.add_feature(
    #     cfeature.LAND.with_scale("110m"),
    #     facecolor="#E6E6E6",
    #     edgecolor="none",
    #     zorder=0
    # )

    land_artist = ax_map.add_feature(
        cfeature.LAND.with_scale("110m"),
        facecolor="#E6E6E6",
        edgecolor="none",
        zorder=0
    )

    if RASTERIZE_MAP_POLYGONS:
        land_artist.set_rasterized(True)



    # Place gridlines above fills and boundaries for readability.
    gridliner = ax_map.gridlines(
        crs=ccrs.PlateCarree(),

        draw_labels=True,
        x_inline=False,
        y_inline=False,

        # Use short dashed lines above the fills and boundaries.
        linestyle=(0, (6.0, 4.0)),
        linewidth=0.20,
        color="#B8B8B8",

        zorder=4
    )

    gridliner.top_labels = False
    gridliner.right_labels = False

    gridliner.xlocator = mticker.FixedLocator(
        [-120, -60, 0, 60, 120]
    )

    gridliner.ylocator = mticker.FixedLocator(
        [-30, 0, 30, 60]
    )

    gridliner.xlabel_style = {
        "size": 6,
        "color": "black"
    }

    gridliner.ylabel_style = {
        "size": 6,
        "color": "black"
    }

    ax_map.set_xlabel(
        "Longitude",
        fontsize=6,
        labelpad=2
    )

    ax_map.set_ylabel(
        "Latitude",
        fontsize=6,
        labelpad=2,
        rotation=90
    )

    ax_map.set_title(
        titles[i],
        loc="left",
        fontsize=7,
        fontweight="bold",
        pad=2
    )

    # Error values for the current crop
    plot_values = gdf[crop].replace(
        0,
        np.nan
    )

    nonzero_gdf = gdf.assign(
        plot_value=plot_values
    )

    # Draw countries with nonzero values
    plot_geodataframe_layer(
        nonzero_gdf,
        ax_map,

        column="plot_value",
        cmap=cmap,
        norm=norm,

        linewidth=0,
        edgecolor="none",

        legend=False,
        zorder=2
    )

    # Draw zero-value countries separately
    zero_value_gdf = gdf.loc[
        gdf[crop] == 0
    ]

    if not zero_value_gdf.empty:
        plot_geodataframe_layer(
            zero_value_gdf,
            ax_map,

            color="#BFBFBF",
            linewidth=0,
            edgecolor="none",

            zorder=2
        )

    # Draw unified country boundaries once from the filled polygons.
    # ax_map.add_geometries(
    #     [country_boundaries],
    #     crs=ccrs.PlateCarree(),
    #     facecolor="none",
    #     edgecolor="black",
    #     linewidth=0.20,
    #     zorder=3
    # )

    boundary_artist = ax_map.add_geometries(
        [country_boundaries],
        crs=ccrs.PlateCarree(),
        facecolor="none",
        edgecolor="black",
        linewidth=0.20,
        zorder=3
    )

    if RASTERIZE_MAP_POLYGONS:
        boundary_artist.set_rasterized(True)




    # Performance metrics
    stats_text = (
        rf"R²: {r2[i]:.2f}"
        f"\nRMSE: {rmse[i]:.1f}"
        f"\nMAE: {mae[i]:.1f}"
    )

    ax_map.text(
        0.02,
        0.05,
        stats_text,

        transform=ax_map.transAxes,

        fontsize=7,
        fontweight="bold",
        color="#17365D",

        horizontalalignment="left",
        verticalalignment="bottom",

        zorder=5
    )

    # Map frame
    ax_map.spines["geo"].set_linewidth(
        0.5
    )

    ax_map.spines["geo"].set_edgecolor(
        "#555555"
    )

    # --------------------------------------------------------
    # Right bar chart
    # --------------------------------------------------------
    ax_bar = fig.add_subplot(
        gs[i, 1]
    )

    bar_axes.append(
        ax_bar
    )

    crop_key = crop.split("_")[0]

    # Use the last 10 entries, representing the top production countries by harvested area.
    selected_countries = yield_data[
        crop_key
    ][5:]

    countries, actual, estimated = zip(
        *selected_countries
    )

    actual = np.asarray(
        actual,
        dtype=float
    )

    estimated = np.asarray(
        estimated,
        dtype=float
    )

    y_positions = np.arange(
        len(countries)
    )

    bar_height = 0.38

    ax_bar.barh(
        y_positions + bar_height / 2,
        estimated,

        height=bar_height,

        label="Estimated yield",

        color="#62B197",
        edgecolor="black",
        linewidth=0.35
    )

    ax_bar.barh(
        y_positions - bar_height / 2,
        actual,

        height=bar_height,

        label="Actual yield",

        color="#F4A259",
        edgecolor="black",
        linewidth=0.35
    )

    ax_bar.set_yticks(
        y_positions,
        labels=countries
    )

    ax_bar.tick_params(
        axis="y",
        labelsize=6.5
    )

    # Add space on the right
    panel_maximum = max(
        np.max(actual),
        np.max(estimated)
    )

    ax_bar.set_xlim(
        0,
        panel_maximum * 1.12
    )

    format_bar_axis(
        ax_bar
    )

    # Show units only on the final bar chart; add the legend after all panels are drawn.
    # Position it in figure coordinates to align with the left legend.
    if i == 3:
        ax_bar.set_xlabel(
            r"Yield (kg ha$^{-1}$)",
            fontsize=7,
            labelpad=2
        )


# ============================================================
# Bottom legend layout
#
# Cartopy resizes map axes within GridSpec cells according to projection aspect ratio,
# so GridSpec widths or hard-coded coordinates do not represent visible map width.
# Draw first and use actual map-axis bounds for the colorbar and left legend.
# ============================================================
fig.canvas.draw()

map_bbox = map_axes[-1].get_position()
bar_bbox = bar_axes[-1].get_position()

map_center_x = map_bbox.x0 + map_bbox.width / 2
bar_center_x = bar_bbox.x0 + bar_bbox.width / 2

# Reserve bottom space for colorbar ticks, title, and legends.
colorbar_bottom = map_bbox.y0 - 0.045
colorbar_height = 0.011
legend_row_y = colorbar_bottom - 0.045
right_legend_y = legend_row_y + 0.025

# ============================================================
# Horizontal colorbar matching the visible map width
# ============================================================
colorbar_ax = fig.add_axes([
    map_bbox.x0,
    colorbar_bottom,
    map_bbox.width,
    colorbar_height
])

scalar_mappable = plt.cm.ScalarMappable(
    cmap=cmap,
    norm=norm
)

scalar_mappable.set_array(
    []
)

colorbar = fig.colorbar(
    scalar_mappable,

    cax=colorbar_ax,
    orientation="horizontal",

    ticks=boundaries[1:-1],
    # Equal-width discrete classes prevent crowded ticks such as -10, 0, and 10.
    spacing="uniform"
)

colorbar.ax.tick_params(
    axis="x",
    direction="out",
    length=2.2,
    width=0.6,
    labelsize=6.5,
    pad=1.5
)

colorbar.outline.set_linewidth(
    0.6
)

colorbar.set_label(
    "Errors in yield estimation (%)",
    fontsize=7,
    fontweight="bold",
    labelpad=2
)


# ============================================================
# Gray "Not production countries" legend
# Center the complete swatch-and-text group on the colorbar.
# ============================================================
not_production_patch = mpatches.Patch(
    facecolor="#BFBFBF",
    edgecolor="black",
    linewidth=0.5,
    label="Not production countries"
)

left_legend = fig.legend(
    handles=[not_production_patch],
    loc="center",
    bbox_to_anchor=(map_center_x, legend_row_y),
    bbox_transform=fig.transFigure,
    ncol=1,
    frameon=False,
    fontsize=6.5,
    handlelength=1.8,
    handleheight=0.85,
    handletextpad=0.55,
    borderaxespad=0
)

for text in left_legend.get_texts():
    text.set_fontweight("bold")


# ============================================================
# Bar-chart legend
# Align it with the left legend center line rather than the final bar-chart axis.
# This avoids a visibly high legend anchor.
# ============================================================
bar_handles, bar_labels = bar_axes[-1].get_legend_handles_labels()

right_legend = fig.legend(
    handles=bar_handles,
    labels=bar_labels,
    loc="center",
    bbox_to_anchor=(bar_center_x, right_legend_y),
    bbox_transform=fig.transFigure,
    ncol=1,
    frameon=False,
    fontsize=7,
    handlelength=1.5,
    handletextpad=0.45,
    labelspacing=0.35,
    borderaxespad=0
)


# ============================================================
# Save files
#
# Do not use bbox_inches="tight" to preserve figure dimensions and layout.
# Rasterize map polygons at 600 dpi in PDF/EPS output;
# text, bars, axes, and legends remain vector objects.
# ============================================================
pdf_path = output_dir / "Fig_1.pdf"

fig.savefig(
    pdf_path,
    format="pdf",

    # Set the resolution for rasterized map layers in the PDF
    dpi=400,

    facecolor="white",
    edgecolor="white"
)


eps_path = output_dir / "Fig_1.eps"

fig.savefig(
    eps_path,
    format="eps",
    dpi=400,
    facecolor="white",
    edgecolor="white"
)


tiff_path = output_dir / "Fig_1.tiff"

fig.savefig(
    tiff_path,
    format="tiff",
    dpi=400,
    facecolor="white",
    edgecolor="white",

    pil_kwargs={
        "compression": "tiff_lzw"
    }
)


png_path = output_dir / "Fig_1_preview.png"

fig.savefig(
    png_path,
    format="png",
    dpi=300,
    facecolor="white",
    edgecolor="white"
)


# ============================================================
# Output file information
# ============================================================
print(f"PDF saved to:  {pdf_path}")
print(f"EPS saved to:  {eps_path}")
print(f"TIFF saved to: {tiff_path}")
print(f"PNG saved to:  {png_path}")


# ============================================================
# Display and close the figure
# ============================================================
plt.show()
plt.close(fig)
