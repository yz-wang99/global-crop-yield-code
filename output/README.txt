SELECTED MODEL OUTPUTS
======================

This directory contains selected country-level prediction tables made public
with the code release. They are compact final/derived outputs, not the raw
raster, point-level, or intermediate model inputs.

Every CSV contains:
  Countries
  Yield (kg ha^-1)
  Predictions_0 days before harvest through
  Predictions_128 days before harvest (nine 16-day lead times)
  Error_0 days before harvest (%) through
  Error_128 days before harvest (%)

Errors are signed percentage errors:
  (prediction - observed yield) / observed yield * 100

An empty/NaN prediction or error is not a zero value. It denotes a lead-time
combination for which no valid output was retained, for example because the
legacy workflow excluded an unrealistically early prediction date.

File groups
-----------

Global_{crop}2020.csv
  Global results for the 2020 target-year prediction experiment. Each table
  covers the available country rows for one crop and reports outputs at all
  nine prediction lead times.

A_{crop}2019.csv and A_{crop}2020.csv
  Outputs used for the Australian wildfire case-study workflow for 2019- and
  2020-sown crops, respectively. The year denotes the crop planting year.
  The tables retain countries handled by the relevant phenology-class model;
  they are not restricted to Australia alone, although Australia is the focal
  case-study country.

RU_{crop}2022.csv
  Outputs used for the 2022 Russia--Ukraine conflict case-study workflow.
  These tables likewise retain country rows used by the relevant
  phenology-class model, rather than only the two focal countries.

The public files provide prediction results for interpretation and figure
reproduction. They do not replace the full input data described in the main
README.txt.
