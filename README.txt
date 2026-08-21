PUBLIC CODE AND SELECTED OUTPUTS
================================

Title: An integrative framework for early estimation of global crop yields demonstrated
under large-scale disruptions 

This repository contains the archived implementation and selected prediction
outputs supporting the manuscript named above. It estimates national yields of
wheat, rice, soybean, and maize by combining FAOSTAT statistics, crop-phenology
clusters, multi-source satellite/climate data, and cluster-specific Random
Forest models.

Repository layout
-----------------

code/model_pipeline/
    01_cluster_countries.py
        Step 1. Clusters countries with comparable planting/harvest phenology.
    02_aggregate_country_features.py
        Step 2. Aggregates point-level 16-day series into country mean,
        standard-deviation, and frequency features.
    03_prepare_model_data.py
        Step 3. Builds class-specific country-year training and test tables at
        0--128 days before harvest.
    04_random_forest_validation.py
        Step 4. Fits and evaluates class-specific Random Forest models.

code/figure_generation/
    Fig1_map.py to Fig4_map.py
        Figure-generation scripts. These are intentionally separate from the
        analytical/model pipeline. Figure 1 requires its documented shapefile;
        Figures 2--4 use embedded publication-specific values.

output/
    Selected country-level prediction tables described in output/README.txt.

Raw data and intermediate data are not included
-----------------------------------------------

The original raster, point-level, and intermediate datasets are too large to
distribute in this repository. Obtain source data through the manuscript Data
Availability statement:

  FAOSTAT crop yield and harvested area
  https://www.fao.org/faostat/en/#data/QCL

  SPAM v2020 crop distribution and harvested-area data
  https://mapspam.info/data/

  Global Crop Calendar dataset
  https://sage.nelson.wisc.edu/data-and-models/datasets/crop-calendar-dataset/

  MODIS vegetation indices and land-surface temperature
  https://earthdata.nasa.gov/eosdis/daacs/lpdaac

  ERA5-Land climate data
  https://cds.climate.copernicus.eu/datasets

  Dynamic World land cover
  https://developers.google.cn/earth-engine/datasets/catalog?hl=zh-cn

Recreate GEE point-level input tables with the following scripts. The stable
point identifier Num must be identical in every exported variable table and in
the crop-specific point-reference table.

  NDVI/EVI extraction
  https://code.earthengine.google.com/4531121c47254a9aae57a45292242c5a

  LST and weather-variable extraction
  https://code.earthengine.google.com/8c5b30a44953635c14c3e8c960e819a6

  Australian active-cropland area and relative-NDVI-decline classes
  https://code.earthengine.google.com/eeddcbb92e5c74a4f1ce6a947ba2b750;
  https://code.earthengine.google.com/a051012043895e0edad720d862b99a2a

  Ukrainian active-cropland extent and relative-NDVI-decline classes
  https://code.earthengine.google.com/ff6c4c510ead8f49c9dd6a892398b1b9

The two final GEE workflows support the disaster-year crop-area assessment.
They use Dynamic World cropland (class 4), MOD13Q1 active-cropland NDVI >= 0.3
(raw scaled value >= 3000), and relative NDVI decline against the stated
reference period. They are separate from the four Python yield-model steps.

Cropland-area estimation outside the Python workflow
----------------------------------------------------

The two disaster-assessment GEE scripts export the cropland-area and dNDVI
inputs required for the area-estimation method. After those exports were
obtained, the remaining crop-area calculations described in the Methods were
performed with formulas in Microsoft Excel workbooks, rather than with
additional Python, R, or other local scripts. Consequently, no separate
area-estimation program is included in this release. To reproduce this part of
the workflow, run the linked GEE scripts to obtain the required inputs and
then apply the calculation steps described in the Methods in a spreadsheet.

Required data structures
------------------------

Phenology input for Step 1
  One country per row. Column 1 is adm0_name. Columns 2 and 3 are the
  planting and harvest phenology summaries used for clustering. The code 
  selects these features by position, so do not insert columns before them.

Point-reference input for Step 2
  The first eleven columns must keep the legacy order:
  class, SOYB_A, WHEA_A, Num, X, CNTRY_NAME, Y, RICE_A, MAIZ_A, adm0_name,
  shape_area. Merge the Step-1 integer class into the class column before
  running Step 2. The crop-area field corresponding to the active crop must
  be positive for points retained by the code.

GEE point-series input for Step 2
  Export one CSV per 16-day composite per variable. Each CSV contains Num plus
  its exact value field: NDVI, EVI, LST_Day_1km_mean, LST_Night_1km_mean,
  temperature_2m_mean, total_precipitation_sum_mean, or
  total_evaporation_sum_mean. Extra GEE fields such as system:index and .geo
  may remain. The archived source sequence spans 2001-02-02 to 2022-12-19.

Annual-yield input for Step 3
  One country per row, with adm0_name first and chronological annual FAOSTAT
  yield columns thereafter. The archived table spans 2000--2022.

Country feature ordering for Steps 3--4
  Step 3 relies on the unsorted os.listdir() order. The 49 CSVs must enumerate
  as ET, EVI, LSTD, LSTN, NDVI, PRE, TEM; for each variable, mean,
  proportions0, proportions1, proportions2, proportions3, proportions4, and
  std. Do not add unrelated CSVs. The model output rows are:
  adm0_name, yield, [49 feature blocks], year.

Run sequence
------------

1. Set local input/output paths and crop settings in Step 1, inspect the
   dendrogram, and create crop-specific phenology labels.
2. Merge the class labels into the point-reference input while preserving its
   eleven-column arrangement.
3. Run Step 2 to calculate country features for all seven variables.
4. Run Step 3 to build class-specific scaled training/test files for each
   lead time.
5. Run Step 4 to fit the Random Forest validation models and write prediction
   tables and metric summaries.
6. Update the data/path blocks in Fig1_map.py to Fig4_map.py before recreating
   the publication figures.

The scripts retain historical absolute Windows paths. Change them to valid
local paths before execution. The original executable statements were retained
when this public package was prepared.

Changing the target year
------------------------

The archived active configuration targets 2020. With the 2000-first yield
layout, use the following Step-3 values:

  Target year   year   end   Training years
  2020          2020   22    2002--2019
  2021          2021   23    2003--2020
  2022          2022   24    2004--2021

Also use a matching testYYYY feature directory in Steps 2--4 and ensure GEE
exports extend through the target year. If the crop calendar, time-series
origin, or 16-day interval changes, recalculate the cluster-specific season
starts, intervals, and calendar-day prediction cut-offs.


Environment and citation
------------------------

The reference conda environment is recorded in ENVIRONMENT.txt and the exact
package requirements are in requirements.txt. Cite the associated manuscript
and this software release. CITATION.cff is machine-readable release metadata;
after public release, add the public repository URL and assigned Zenodo DOI.

Licence and reuse
-----------------

Python source files in code/ are released under the PolyForm Noncommercial
License 1.0.0 (LICENSE.txt). This allows non-commercial use, including
research and educational use, but commercial use requires prior written
permission from the rights holders. Result CSV files in output/ are released
under CC BY-NC 4.0 (DATA_LICENSE.txt). See LICENSE_SCOPE.txt for the scope,
attribution requirements, and exclusions for external data and services.

Before release, confirm that every relevant code author and institution
approves the public release and the stated copyright notice.
