"""Step 2: convert point-level 16-day series to country-level features.

Input contract
--------------
``reference_csv`` is one crop-specific point table. Its positional schema is
critical: the first 11 columns must be the legacy point metadata, with
``class`` in column 1, the crop-area field (``WHEA_A``, ``RICE_A``,
``SOYB_A``, or ``MAIZ_A``), ``Num`` (the stable point identifier),
``adm0_name``, and ``shape_area`` in column 11. The country-level time-series
columns are appended after column 11. The supplied workflow used a table with
the following order: ``class, SOYB_A, WHEA_A, Num, X, CNTRY_NAME, Y, RICE_A,
MAIZ_A, adm0_name, shape_area``. Before this stage, merge the ``class`` field
from Step 1 into that reference table while preserving this order.

Each variable folder contains one GEE-exported CSV per 16-day composite. Every
CSV must contain ``Num`` plus its exact value column: ``NDVI``, ``EVI``,
``LST_Day_1km_mean``, ``LST_Night_1km_mean``, ``temperature_2m_mean``,
``total_precipitation_sum_mean``, or ``total_evaporation_sum_mean``. Extra GEE
columns such as ``system:index`` and ``.geo`` are ignored. ``Num`` must match
the reference table exactly. The archived data span 2001-02-02 to 2022-12-19
(504 composites); because the legacy merge skips the first directory entry,
the resulting country feature tables start at the next composite.

For each variable and composite, the script produces country mean, standard
deviation, and proportions in five robustly normalized bins: <0.2, 0.2-0.4,
0.4-0.6, 0.6-0.8, and >0.8. It writes seven tables per variable. The
normalization bounds are class-specific global 0.5th/99.5th percentiles across
the specified number of annual blocks.With the active Num=19 settings, these
bounds adopt the time window prior to 2020 to construct samples for the test year 2020.
Analogously, Num=20 corresponds to test year 2021, and Num=21 corresponds to test year 2022.;
this stage itself doesnot receive a held-out test-year argument. Step 3 applies a separate
pre-test-year feature scaling.

When substituting another period, provide complete 16-day sequences in
chronological directory order, update ``Num`` to the number of annual blocks,
and revise both the reference path and output ``testYYYY`` label. Do not add
unrelated CSV files to a variable folder: the source code reads every ``.csv``
file and uses their directory order as temporal order.
"""

import pandas as pd
import os
import numpy as np

def group_and_merge_csv(folder_path, output_csv):
    """Legacy utility: average one CSV variable by ``CNTRY_NAME`` and merge dates."""

    df_list = []

    # 遍历文件夹下的所有文件
    for filename in os.listdir(folder_path):

        if filename.endswith('.csv'):

            file_path = os.path.join(folder_path, filename)

            df = pd.read_csv(file_path)

            df = df[['CNTRY_NAME', 'NDVI']]

            group_df = df.groupby('CNTRY_NAME')['NDVI'].mean().reset_index()

            group_df.rename(columns={'NDVI': filename[:-4]}, inplace=True)

            df_list.append(group_df)


    combined_df = df_list[0]
    for df in df_list[1:]:
        combined_df = pd.merge(combined_df, df, on='CNTRY_NAME', how='outer')


    combined_df.to_csv(output_csv, index=False)
    print(f"Merged CSV saved to {output_csv}")


def output_common_csv(df1, df2):

    """Keep country rows in ``df2`` whose ``adm0_name`` occurs in ``df1``."""


    common_ctry = df1.merge(df2, on='adm0_name', how='inner')['adm0_name']


    filtered_df2 = df2[df2['adm0_name'].isin(common_ctry)]


    return filtered_df2




bins = [-np.inf, 0.2, 0.4, 0.6, 0.8, np.inf]


def calculate_histogram_proportions(data, bins):
    """Return the five within-country proportions after excluding missing values."""

    hist, bin_edges = np.histogram(data[~np.isnan(data)], bins=bins)  # 忽略 NaN 值

    if hist.sum() > 0:
        proportions = hist / hist.sum()
    else:
        proportions = np.zeros_like(hist)
    return proportions

def join_and_scale(reference_csv, folder_path, crop, value, output_csv, s0, i0, s1, i1, s2, i2, s3=None, i3=None, Num=None,
        crop_c=None):
    """Merge one variable's point series and export seven country feature tables.

    ``s0``--``s3`` are zero-based positional starts of the crop-season window
    in the merged reference table, and ``i0``--``i3`` are its numbers of
    16-day composites for phenology classes 0--3. ``Num`` repeats the window
    at 23-composite annual intervals. Maize has classes 0--2 only, so its
    calls intentionally omit ``s3`` and ``i3``.
    """
    if Num is None:
        raise ValueError("必须提供 Num")

    is_maize = str(crop_c).strip().lower() == 'maize'

    # 非 maize 作物仍然必须提供 s3 和 i3
    if not is_maize and (s3 is None or i3 is None):
        raise ValueError(
            f"{crop_c} 存在 class 3，必须提供 s3 和 i3"
        )


    df_list = []

    for filename in os.listdir(folder_path):

        if filename.endswith('.csv'):

            file_path = os.path.join(folder_path, filename)

            df = pd.read_csv(file_path)

            df = df[['Num', value]]

            df.rename(columns={value: filename[:-4]}, inplace=True)


            df_list.append(df)


    combined_df = pd.read_csv(reference_csv)
    for df in df_list[1:]:
        combined_df = pd.merge(combined_df, df, on='Num', how='outer')


    combined_df.iloc[:, 10:].interpolate(method='linear', axis=1, limit=3, inplace=True)
    #combined_df = combined_df.dropna()


    combined_df = combined_df[combined_df[crop] > 0]

    # #combined_df.to_csv(output_csv + '_merged0.csv', index=False)
    # df_crop_class = pd.read_csv(crop_cluster)
    #
    # class_dict = dict(zip(df_crop_class['adm0_name'], df_crop_class['class']))
    #
    #
    # combined_df['class'] = combined_df['adm0_name'].map(class_dict)
    #
    # class_series = combined_df['class']
    # combined_df = pd.concat([class_series, combined_df.drop('class', axis=1)], axis=1)


    mean_df = pd.DataFrame()

    std_df = pd.DataFrame()

    for column in combined_df.iloc[:, 11:]:

        mean_grouped = combined_df.groupby('adm0_name')[column].mean().reset_index()
        std_grouped = combined_df.groupby('adm0_name')[column].std().reset_index()

        if mean_df.empty:
            mean_df = mean_grouped
        else:
            mean_df = pd.merge(mean_df, mean_grouped, on='adm0_name', how='outer')

        if std_df.empty:
            std_df = std_grouped
        else:
            std_df = pd.merge(std_df, std_grouped, on='adm0_name', how='outer')


    combined_df_class0 = combined_df[combined_df['class'] == 0]
    combined_df_class1 = combined_df[combined_df['class'] == 1]
    combined_df_class2 = combined_df[combined_df['class'] == 2]
    if not is_maize:
        combined_df_class3 = combined_df[combined_df['class'] == 3]

    start0 = s0
    interval0 = i0
    start1 = s1
    interval1 = i1
    start2 = s2
    interval2 = i2
    if not is_maize:
        start3 = s3
        interval3 = i3

    column_class0 = [(start0 + 23 * i, start0 + 23 * i + interval0) for i in range(Num)]
    column_class1 = [(start1 + 23 * i, start1 + 23 * i + interval1) for i in range(Num)]
    column_class2 = [(start2 + 23 * i, start2 + 23 * i + interval2) for i in range(Num)]
    if not is_maize:
        column_class3 = [(start3 + 23 * i, start3 + 23 * i + interval3) for i in range(Num)]

    min_values_class0 = pd.concat([combined_df_class0.iloc[:, range_start:end_start] for range_start, end_start in column_class0], axis=1).quantile(0.005).min()
    max_values_class0 = pd.concat([combined_df_class0.iloc[:, range_start:end_start] for range_start, end_start in column_class0], axis=1).quantile(0.995).max()
    min_values_class1 = pd.concat([combined_df_class1.iloc[:, range_start:end_start] for range_start, end_start in column_class1], axis=1).quantile(0.005).min()
    max_values_class1 = pd.concat([combined_df_class1.iloc[:, range_start:end_start] for range_start, end_start in column_class1], axis=1).quantile(0.995).max()
    min_values_class2 = pd.concat([combined_df_class2.iloc[:, range_start:end_start] for range_start, end_start in column_class2], axis=1).quantile(0.005).min()
    max_values_class2 = pd.concat([combined_df_class2.iloc[:, range_start:end_start] for range_start, end_start in column_class2], axis=1).quantile(0.995).max()
    if not is_maize:
        min_values_class3 = pd.concat([combined_df_class3.iloc[:, range_start:end_start] for range_start, end_start in column_class3], axis=1).quantile(0.005).min()

        max_values_class3 = pd.concat([combined_df_class3.iloc[:, range_start:end_start] for range_start, end_start in column_class3], axis=1).quantile(0.995).max()


    for column in combined_df.columns[11:]:
        combined_df.loc[combined_df['class'] == 0, column] = (combined_df.loc[combined_df['class'] == 0, column] - min_values_class0) / (max_values_class0 - min_values_class0)
        combined_df.loc[combined_df['class'] == 1, column] = (combined_df.loc[combined_df['class'] == 1, column] - min_values_class1) / (max_values_class1 - min_values_class1)
        combined_df.loc[combined_df['class'] == 2, column] = (combined_df.loc[combined_df['class'] == 2, column] - min_values_class2) / (max_values_class2 - min_values_class2)
        if not is_maize:
            combined_df.loc[combined_df['class'] == 3, column] = (combined_df.loc[combined_df['class'] == 3, column] - min_values_class3) / (max_values_class3 - min_values_class3)


    proportions0_df = pd.DataFrame()
    proportions1_df = pd.DataFrame()
    proportions2_df = pd.DataFrame()
    proportions3_df = pd.DataFrame()
    proportions4_df = pd.DataFrame()


    for column in combined_df.iloc[:, 11:]:

        proportions0_grouped = combined_df.groupby('adm0_name')[column].apply(
            lambda x: calculate_histogram_proportions(x, bins)[0]).reset_index()
        proportions1_grouped = combined_df.groupby('adm0_name')[column].apply(
            lambda x: calculate_histogram_proportions(x, bins)[1]).reset_index()
        proportions2_grouped = combined_df.groupby('adm0_name')[column].apply(
            lambda x: calculate_histogram_proportions(x, bins)[2]).reset_index()
        proportions3_grouped = combined_df.groupby('adm0_name')[column].apply(
            lambda x: calculate_histogram_proportions(x, bins)[3]).reset_index()
        proportions4_grouped = combined_df.groupby('adm0_name')[column].apply(
            lambda x: calculate_histogram_proportions(x, bins)[4]).reset_index()


        if proportions0_df.empty:
            proportions0_df = proportions0_grouped
        else:
            proportions0_df = pd.merge(proportions0_df, proportions0_grouped, on='adm0_name', how='outer')

        if proportions1_df.empty:
            proportions1_df = proportions1_grouped
        else:
            proportions1_df = pd.merge(proportions1_df, proportions1_grouped, on='adm0_name', how='outer')

        if proportions2_df.empty:
            proportions2_df = proportions2_grouped
        else:
            proportions2_df = pd.merge(proportions2_df, proportions2_grouped, on='adm0_name', how='outer')

        if proportions3_df.empty:
            proportions3_df = proportions3_grouped
        else:
            proportions3_df = pd.merge(proportions3_df, proportions3_grouped, on='adm0_name', how='outer')

        if proportions4_df.empty:
            proportions4_df = proportions4_grouped
        else:
            proportions4_df = pd.merge(proportions4_df, proportions4_grouped, on='adm0_name', how='outer')


    #combined_df.to_csv(output_csv + '_merged.csv', index=False)
    print(f"Merged CSV saved to {output_csv}")

    df1 = pd.read_csv(r'E:\WYZ\crop_data\产量\maize.csv')
    filter_mean_df = output_common_csv(df1, mean_df)
    filter_std_df = output_common_csv(df1, std_df)
    filter_proportions0_df = output_common_csv(df1, proportions0_df)
    filter_proportions1_df = output_common_csv(df1, proportions1_df)
    filter_proportions2_df = output_common_csv(df1, proportions2_df)
    filter_proportions3_df = output_common_csv(df1, proportions3_df)
    filter_proportions4_df = output_common_csv(df1, proportions4_df)

    filter_mean_df.to_csv(output_csv + '_mean.csv', index=False)
    filter_std_df.to_csv(output_csv + '_std.csv', index=False)
    filter_proportions0_df.to_csv(output_csv + '_proportions0.csv', index=False)
    filter_proportions1_df.to_csv(output_csv + '_proportions1.csv', index=False)
    filter_proportions2_df.to_csv(output_csv + '_proportions2.csv', index=False)
    filter_proportions3_df.to_csv(output_csv + '_proportions3.csv', index=False)
    filter_proportions4_df.to_csv(output_csv + '_proportions4.csv', index=False)



def run_join_and_scale(crop, crop_c, outputcrop, s0, i0, s1, i1, s2, i2, Num, s3=None, i3=None):
    """Run the seven-variable aggregation with one crop's calibrated windows.

    The window values reproduce planting P25 to harvest P75 calendar ranges
    derived from the Global Crop Calendar and should be recalculated if the
    crop calendar, phenology clusters, temporal start date, or composite
    frequency is changed.
    """
    scale_kwargs = {
        's0': s0,
        'i0': i0,
        's1': s1,
        'i1': i1,
        's2': s2,
        'i2': i2,
        'Num': Num,
        'crop_c': crop_c
    }

    if crop_c.strip().lower() != 'maize':
        scale_kwargs['s3'] = s3
        scale_kwargs['i3'] = i3

    reference_csv = (
            r'E:\D盘WYZ\Process_country(Non_scale)\all_point_'
            + crop_c
            + '.csv'
    )

    output_folder = (
            r'E:\D盘WYZ\Process_country(Non_scale)'
            + '\\'
            + outputcrop
    )
    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\NDVI',
        crop,
        'NDVI',
        output_folder + r'\NDVI',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\EVI',
        crop,
        'EVI',
        output_folder + r'\EVI',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\LSTD',
        crop,
        'LST_Day_1km_mean',
        output_folder + r'\LSTD',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\LSTN',
        crop,
        'LST_Night_1km_mean',
        output_folder + r'\LSTN',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\TEM',
        crop,
        'temperature_2m_mean',
        output_folder + r'\TEM',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\PRE',
        crop,
        'total_precipitation_sum_mean',
        output_folder + r'\PRE',
        **scale_kwargs
    )

    join_and_scale(
        reference_csv,
        r'E:\WYZ\crop_data\ET',
        crop,
        'total_evaporation_sum_mean',
        output_folder + r'\ET',
        **scale_kwargs
    )

# The active calls reproduce the 2002-2022 (21 annual-block) feature archive.
# For another target year, update the ``test2020`` output label and ensure the
# input archive and ``Num`` cover the intended full sequence before running.
run_join_and_scale('WHEA_A', 'wheat', 'test2020\\wheat', s0=24, i0=11, s1=39, i1=12, s2=27, i2=15, s3=27, i3=10 ,Num=19)
run_join_and_scale('RICE_A', 'rice', 'test2020\\rice', s0=23, i0=17, s1=38, i1=11, s2=31, i2=12, s3=41, i3=11,Num=19)
run_join_and_scale('SOYB_A', 'soybean', 'test2020\\soybean', s0=27, i0=13, s1=37, i1=10, s2=39, i2=11, s3=32, i3=11,Num=19)
run_join_and_scale('MAIZ_A', 'maize','test2020\\maize', s0=25, i0=14, s1=38, i1=11, s2=36, i2=11, Num=19)
