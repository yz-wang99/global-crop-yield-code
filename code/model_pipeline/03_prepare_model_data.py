"""Step 3: build class-specific country-year model tables for each lead time.

This script consumes the 49 country-feature CSVs exported by Step 2 and an
annual FAOSTAT yield table. The yield input has one row per country, an
``adm0_name`` first column, and chronological annual yield columns (the
archived layout is 2000--2022). The Step-1 cluster CSV provides ``adm0_name``
and ``class``; its original ``MEAN`` phenology field is retained there because
Step 4 uses it to exclude unrealistically early predictions.

The feature directory must contain exactly these 49 files in the legacy order
returned by ``os.listdir``: ET, EVI, LSTD, LSTN, NDVI, PRE, TEM; for each
variable, ``_mean``, ``_proportions0`` through ``_proportions4``, then ``_std``.
Each file has ``adm0_name`` followed by a shared chronological sequence of
16-day country summaries. The source code does *not* sort filenames; a
different directory order changes feature positions and invalidates Step 4's
positional selections. Check this order before use and keep unrelated CSVs
out of the directory.

For every class and lead time, output rows have this exact layout:
``adm0_name, yield, [49 contiguous feature blocks], year``. Each block contains
the class-specific number of retained 16-day composites. The final appended
year is the held-out test set and all preceding rows are training data. Scaled
versions use extrema calculated from historical (pre-test-year) rows only.

To prepare a new target year, set both ``year`` and ``end``. With the archived
2000-first yield layout, use ``end = target_year - 1998`` (22 for 2020, 23 for
2021, and 24 for 2022), retain ``start = 3`` (2002), and point the input/output
paths to matching feature directories. The crop-specific offsets and intervals
reproduce the paper's P25-planting to P75-harvest windows; do not reuse them
after changing the calendar, time-series origin, or composite frequency.
"""

import pandas as pd
import os

# Select the crop and final held-out yield year (see the module documentation).
crop_type = 'maize'   # maize,rice,soybean,wheat,wheats
year = 2020

df_grace = pd.read_csv('E:\\E盘WYZ\\crop_data\\产量\\processed\\' + crop_type + '.csv')

df_class = pd.read_csv('E:\\D盘WYZ\\SPAM2020\\cluster\\' + crop_type + '_cluster_final.csv')
df_class = df_class[['adm0_name', 'class']]

df_grace = pd.merge(df_grace, df_class, on='adm0_name', how='outer')


folder_path = f'E:\\D盘WYZ\\Process_country(Non_scale)\\test{year}\\' + crop_type


dfs = {}


for filename in os.listdir(folder_path):

    if filename.endswith('.csv'):

        file_path = os.path.join(folder_path, filename)

        df = pd.read_csv(file_path)
        df.iloc[:, 1:].interpolate(method='linear', axis=1, limit=3, inplace=True)
        df.fillna(0, inplace=True)
        df = pd.merge(df, df_class, on='adm0_name', how='outer')
        df['class'] = df['class'].fillna(99)
        dfs[filename] = df


df_01 = dfs['ET_std.csv']
print(df_01)


def data_creat(start, end, m, interval, class_value):
    """Stack one class's country-year samples for one prediction window.

    ``start`` and ``end`` index annual yield columns; ``m`` is the calibrated
    positional offset aligning the legacy summary-series origin to the class
    season; ``interval`` is the number of retained 16-day composites.
    """

    result_df = pd.DataFrame()


    for n in range(start, end):  # (10,262)  t1= n-8  t2= n-9   interval = 36;  3, 24

        t1 = (n-2) * 23 + m
        interval = interval

        df_grace_e = df_grace[df_grace['class'] == class_value].iloc[:, n]


        dfs_list = [df[df['class'] == class_value].iloc[:, t1:t1 + interval] for df in dfs.values()]  # df_03被删除了，需要的话再加上


        dfs_list.insert(0, df_grace_e)
        dfs_list.insert(0, df_grace[df_grace['class'] == class_value].iloc[:, 0])


        temp_df = pd.concat(dfs_list, axis=1, ignore_index=True)
        temp_df = temp_df.rename(columns={temp_df.columns[0]: 'adm0_name'})


        temp_df['year'] = n + 1999

        # temp_df = pd.merge(temp_df, df_class, on='adm0_name', how='outer')
        # temp_df['class'] = temp_df['class'].fillna(99)

        result_df = pd.concat([result_df, temp_df], ignore_index=True)

    result_df = result_df.dropna()
    return result_df


def split_train_test(df0, df1):
    """Use the final appended year as the held-out test set."""

    n = df0.shape[0] - df1.shape[0]


    train_set = df0.iloc[:-n]


    test_set = df0.iloc[-n:]

    return train_set, test_set

def save_by_class(df, output, file, name):
    """Write one CSV per integer phenology class (legacy helper; not used below)."""
    # 按 'class' 字段分组
    grouped = df.groupby('class')


    for class_value, group_df in grouped:
        full_path = f"{output}{file}/{name}_{int(class_value)}.csv"
        group_df.to_csv(full_path, index=False)

def normalize_columns(df, df1, start_col, end_col):  #df1是年份少的csv
    """Scale one feature block with extrema from pre-test-year rows only."""

    min_val = df1.iloc[:, start_col:end_col].min().min()
    max_val = df1.iloc[:, start_col:end_col].max().max()

    print(str(start_col) + '-' + str(end_col) + ' Min:' + str(min_val))
    print(str(start_col) + '-' + str(end_col) + ' Max:' + str(max_val))
    print('--------------------------------------------------------------------------------------------------------')


    for col in df.columns[start_col:end_col]:
        df.loc[:, col] = (df[col] - min_val) / (max_val - min_val)

    return df


def data_process_maize(start, end, interval, output, file):   #start=1,5,11
    """Create maize train/test CSVs for one 0--128-day lead-time setting."""

    interval_class0 = interval[0]
    interval_class1 = interval[1]
    interval_class2 = interval[2]

    result0_class0 = data_creat(start, end, -8, interval_class0, 0)
    result1_class0 = data_creat(start, end-1, -8, interval_class0, 0)
    train_result0, test_result0 = split_train_test(result0_class0, result1_class0)
    train_result0.to_csv(output + '0' + file + '\\trainingdata_class0.csv', index=False)
    test_result0.to_csv(output + '0' + file + '\\testdata_class0.csv', index=False)

    result0_class1 = data_creat(start, end, 5, interval_class1, 1)
    result1_class1 = data_creat(start, end-1, 5, interval_class1, 1)
    train_result1, test_result1 = split_train_test(result0_class1, result1_class1)
    train_result1.to_csv(output + '0' + file + '\\trainingdata_class1.csv', index=False)
    test_result1.to_csv(output + '0' + file + '\\testdata_class1.csv', index=False)

    result0_class2 = data_creat(start, end, 3, interval_class2, 2)
    result1_class2 = data_creat(start, end-1, 3, interval_class2, 2)
    train_result2, test_result2 = split_train_test(result0_class2, result1_class2)
    train_result2.to_csv(output + '0' + file + '\\trainingdata_class2.csv', index=False)
    test_result2.to_csv(output + '0' + file + '\\testdata_class2.csv', index=False)


#class0**********************************************************************************

    columns_ranges0 = [(i, min(i + interval_class0, interval_class0*49+2)) for i in range(2, interval_class0*49+2, interval_class0)]
    print(columns_ranges0)

    for start_col, end_col in columns_ranges0:
        result0_class0 = normalize_columns(result0_class0, result1_class0, start_col, end_col)
    train_result0_scale, test_result0_scale = split_train_test(result0_class0, result1_class0)
    train_result0_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class0.csv', index=False)
    test_result0_scale.to_csv(output + '0' + file + '\\testdata(scale)_class0.csv', index=False)

#class1**********************************************************************************
    columns_ranges1 = [(i, min(i + interval_class1, interval_class1*49+2)) for i in range(2, interval_class1*49+2, interval_class1)]
    print(columns_ranges1)

    for start_col, end_col in columns_ranges1:
        result0_class1 = normalize_columns(result0_class1, result1_class1, start_col, end_col)
    train_result1_scale, test_result1_scale = split_train_test(result0_class1, result1_class1)
    train_result1_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class1.csv', index=False)
    test_result1_scale.to_csv(output + '0' + file + '\\testdata(scale)_class1.csv', index=False)

#class2**********************************************************************************

    columns_ranges2 = [(i, min(i + interval_class2, interval_class2*49+2)) for i in range(2, interval_class2*49+2, interval_class2)]
    print(columns_ranges2)

    for start_col, end_col in columns_ranges2:
        result0_class2 = normalize_columns(result0_class2, result1_class2, start_col, end_col)
    train_result2_scale, test_result2_scale = split_train_test(result0_class2, result1_class2)
    train_result2_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class2.csv', index=False)
    test_result2_scale.to_csv(output + '0' + file + '\\testdata(scale)_class2.csv', index=False)

def data_process_rice(start, end, interval, output, file):   #start=1,5,11
    """Create rice train/test CSVs for one 0--128-day lead-time setting."""

    interval_class0 = interval[0]
    interval_class1 = interval[1]
    interval_class2 = interval[2]
    interval_class3 = interval[3]

    result0_class0 = data_creat(start, end, -10, interval_class0, 0)
    result1_class0 = data_creat(start, end-1, -10, interval_class0, 0)
    train_result0, test_result0 = split_train_test(result0_class0, result1_class0)
    train_result0.to_csv(output + '0' + file + '\\trainingdata_class0.csv', index=False)
    test_result0.to_csv(output + '0' + file + '\\testdata_class0.csv', index=False)

    result0_class1 = data_creat(start, end, 5, interval_class1, 1)
    result1_class1 = data_creat(start, end-1, 5, interval_class1, 1)
    train_result1, test_result1 = split_train_test(result0_class1, result1_class1)
    train_result1.to_csv(output + '0' + file + '\\trainingdata_class1.csv', index=False)
    test_result1.to_csv(output + '0' + file + '\\testdata_class1.csv', index=False)

    result0_class2 = data_creat(start, end, -2, interval_class2, 2)
    result1_class2 = data_creat(start, end-1, -2, interval_class2, 2)
    train_result2, test_result2 = split_train_test(result0_class2, result1_class2)
    train_result2.to_csv(output + '0' + file + '\\trainingdata_class2.csv', index=False)
    test_result2.to_csv(output + '0' + file + '\\testdata_class2.csv', index=False)

    result0_class3 = data_creat(start, end, 8, interval_class3, 3)
    result1_class3 = data_creat(start, end-1, 8, interval_class3, 3)
    train_result3, test_result3 = split_train_test(result0_class3, result1_class3)
    train_result3.to_csv(output + '0' + file + '\\trainingdata_class3.csv', index=False)
    test_result3.to_csv(output + '0' + file + '\\testdata_class3.csv', index=False)


#class0**********************************************************************************

    columns_ranges0 = [(i, min(i + interval_class0, interval_class0*49+2)) for i in range(2, interval_class0*49+2, interval_class0)]
    print(columns_ranges0)

    for start_col, end_col in columns_ranges0:
        result0_class0 = normalize_columns(result0_class0, result1_class0, start_col, end_col)
    train_result0_scale, test_result0_scale = split_train_test(result0_class0, result1_class0)
    train_result0_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class0.csv', index=False)
    test_result0_scale.to_csv(output + '0' + file + '\\testdata(scale)_class0.csv', index=False)

#class1**********************************************************************************
    columns_ranges1 = [(i, min(i + interval_class1, interval_class1*49+2)) for i in range(2, interval_class1*49+2, interval_class1)]
    print(columns_ranges1)

    for start_col, end_col in columns_ranges1:
        result0_class1 = normalize_columns(result0_class1, result1_class1, start_col, end_col)
    train_result1_scale, test_result1_scale = split_train_test(result0_class1, result1_class1)
    train_result1_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class1.csv', index=False)
    test_result1_scale.to_csv(output + '0' + file + '\\testdata(scale)_class1.csv', index=False)

#class2**********************************************************************************

    columns_ranges2 = [(i, min(i + interval_class2, interval_class2*49+2)) for i in range(2, interval_class2*49+2, interval_class2)]
    print(columns_ranges2)

    for start_col, end_col in columns_ranges2:
        result0_class2 = normalize_columns(result0_class2, result1_class2, start_col, end_col)
    train_result2_scale, test_result2_scale = split_train_test(result0_class2, result1_class2)
    train_result2_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class2.csv', index=False)
    test_result2_scale.to_csv(output + '0' + file + '\\testdata(scale)_class2.csv', index=False)

#class2**********************************************************************************

    columns_ranges3 = [(i, min(i + interval_class3, interval_class3*49+2)) for i in range(2, interval_class3*49+2, interval_class3)]
    print(columns_ranges3)

    for start_col, end_col in columns_ranges3:
        result0_class3 = normalize_columns(result0_class3, result1_class3, start_col, end_col)
    train_result3_scale, test_result3_scale = split_train_test(result0_class3, result1_class3)
    train_result3_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class3.csv', index=False)
    test_result3_scale.to_csv(output + '0' + file + '\\testdata(scale)_class3.csv', index=False)

def data_process_soybean(start, end, interval, output, file):   #start=1,5,11
    """Create soybean train/test CSVs for one 0--128-day lead-time setting."""

    interval_class0 = interval[0]
    interval_class1 = interval[1]
    interval_class2 = interval[2]
    interval_class3 = interval[3]

    result0_class0 = data_creat(start, end, -6, interval_class0, 0)
    result1_class0 = data_creat(start, end-1, -6, interval_class0, 0)
    train_result0, test_result0 = split_train_test(result0_class0, result1_class0)
    train_result0.to_csv(output + '0' + file + '\\trainingdata_class0.csv', index=False)
    test_result0.to_csv(output + '0' + file + '\\testdata_class0.csv', index=False)

    result0_class1 = data_creat(start, end, 4, interval_class1, 1)
    result1_class1 = data_creat(start, end-1, 4, interval_class1, 1)
    train_result1, test_result1 = split_train_test(result0_class1, result1_class1)
    train_result1.to_csv(output + '0' + file + '\\trainingdata_class1.csv', index=False)
    test_result1.to_csv(output + '0' + file + '\\testdata_class1.csv', index=False)

    result0_class2 = data_creat(start, end, 6, interval_class2, 2)
    result1_class2 = data_creat(start, end-1, 6, interval_class2, 2)
    train_result2, test_result2 = split_train_test(result0_class2, result1_class2)
    train_result2.to_csv(output + '0' + file + '\\trainingdata_class2.csv', index=False)
    test_result2.to_csv(output + '0' + file + '\\testdata_class2.csv', index=False)

    result0_class3 = data_creat(start, end, -1, interval_class3, 3)
    result1_class3 = data_creat(start, end-1, -1, interval_class3, 3)
    train_result3, test_result3 = split_train_test(result0_class3, result1_class3)
    train_result3.to_csv(output + '0' + file + '\\trainingdata_class3.csv', index=False)
    test_result3.to_csv(output + '0' + file + '\\testdata_class3.csv', index=False)


#class0**********************************************************************************

    columns_ranges0 = [(i, min(i + interval_class0, interval_class0*49+2)) for i in range(2, interval_class0*49+2, interval_class0)]
    print(columns_ranges0)

    for start_col, end_col in columns_ranges0:
        result0_class0 = normalize_columns(result0_class0, result1_class0, start_col, end_col)
    train_result0_scale, test_result0_scale = split_train_test(result0_class0, result1_class0)
    train_result0_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class0.csv', index=False)
    test_result0_scale.to_csv(output + '0' + file + '\\testdata(scale)_class0.csv', index=False)

#class1**********************************************************************************
    columns_ranges1 = [(i, min(i + interval_class1, interval_class1*49+2)) for i in range(2, interval_class1*49+2, interval_class1)]
    print(columns_ranges1)
    # 对每个列区间进行归一化
    for start_col, end_col in columns_ranges1:
        result0_class1 = normalize_columns(result0_class1, result1_class1, start_col, end_col)
    train_result1_scale, test_result1_scale = split_train_test(result0_class1, result1_class1)
    train_result1_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class1.csv', index=False)
    test_result1_scale.to_csv(output + '0' + file + '\\testdata(scale)_class1.csv', index=False)

#class2**********************************************************************************

    columns_ranges2 = [(i, min(i + interval_class2, interval_class2*49+2)) for i in range(2, interval_class2*49+2, interval_class2)]
    print(columns_ranges2)

    for start_col, end_col in columns_ranges2:
        result0_class2 = normalize_columns(result0_class2, result1_class2, start_col, end_col)
    train_result2_scale, test_result2_scale = split_train_test(result0_class2, result1_class2)
    train_result2_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class2.csv', index=False)
    test_result2_scale.to_csv(output + '0' + file + '\\testdata(scale)_class2.csv', index=False)

#class2**********************************************************************************

    columns_ranges3 = [(i, min(i + interval_class3, interval_class3*49+2)) for i in range(2, interval_class3*49+2, interval_class3)]
    print(columns_ranges3)

    for start_col, end_col in columns_ranges3:
        result0_class3 = normalize_columns(result0_class3, result1_class3, start_col, end_col)
    train_result3_scale, test_result3_scale = split_train_test(result0_class3, result1_class3)
    train_result3_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class3.csv', index=False)
    test_result3_scale.to_csv(output + '0' + file + '\\testdata(scale)_class3.csv', index=False)

def data_process_wheat(start, end, interval, output, file):   #start=1,5,11
    """Create wheat train/test CSVs for one 0--128-day lead-time setting."""

    interval_class0 = interval[0]
    interval_class1 = interval[1]
    interval_class2 = interval[2]
    interval_class3 = interval[3]

    result0_class0 = data_creat(start, end, -9, interval_class0, 0)
    result1_class0 = data_creat(start, end-1, -9, interval_class0, 0)
    train_result0, test_result0 = split_train_test(result0_class0, result1_class0)
    train_result0.to_csv(output + '0' + file + '\\trainingdata_class0.csv', index=False)
    test_result0.to_csv(output + '0' + file + '\\testdata_class0.csv', index=False)

    result0_class1 = data_creat(start, end, 6, interval_class1, 1)
    result1_class1 = data_creat(start, end-1, 6, interval_class1, 1)
    train_result1, test_result1 = split_train_test(result0_class1, result1_class1)
    train_result1.to_csv(output + '0' + file + '\\trainingdata_class1.csv', index=False)
    test_result1.to_csv(output + '0' + file + '\\testdata_class1.csv', index=False)

    result0_class2 = data_creat(start, end, -6, interval_class2, 2)
    result1_class2 = data_creat(start, end-1, -6, interval_class2, 2)
    train_result2, test_result2 = split_train_test(result0_class2, result1_class2)
    train_result2.to_csv(output + '0' + file + '\\trainingdata_class2.csv', index=False)
    test_result2.to_csv(output + '0' + file + '\\testdata_class2.csv', index=False)

    result0_class3 = data_creat(start, end, -6, interval_class3, 3)
    result1_class3 = data_creat(start, end-1, -6, interval_class3, 3)
    train_result3, test_result3 = split_train_test(result0_class3, result1_class3)
    train_result3.to_csv(output + '0' + file + '\\trainingdata_class3.csv', index=False)
    test_result3.to_csv(output + '0' + file + '\\testdata_class3.csv', index=False)


#class0**********************************************************************************

    columns_ranges0 = [(i, min(i + interval_class0, interval_class0*49+2)) for i in range(2, interval_class0*49+2, interval_class0)]
    print(columns_ranges0)

    for start_col, end_col in columns_ranges0:
        result0_class0 = normalize_columns(result0_class0, result1_class0, start_col, end_col)
    train_result0_scale, test_result0_scale = split_train_test(result0_class0, result1_class0)
    train_result0_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class0.csv', index=False)
    test_result0_scale.to_csv(output + '0' + file + '\\testdata(scale)_class0.csv', index=False)

#class1**********************************************************************************
    columns_ranges1 = [(i, min(i + interval_class1, interval_class1*49+2)) for i in range(2, interval_class1*49+2, interval_class1)]
    print(columns_ranges1)

    for start_col, end_col in columns_ranges1:
        result0_class1 = normalize_columns(result0_class1, result1_class1, start_col, end_col)
    train_result1_scale, test_result1_scale = split_train_test(result0_class1, result1_class1)
    train_result1_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class1.csv', index=False)
    test_result1_scale.to_csv(output + '0' + file + '\\testdata(scale)_class1.csv', index=False)

#class2**********************************************************************************

    columns_ranges2 = [(i, min(i + interval_class2, interval_class2*49+2)) for i in range(2, interval_class2*49+2, interval_class2)]
    print(columns_ranges2)

    for start_col, end_col in columns_ranges2:
        result0_class2 = normalize_columns(result0_class2, result1_class2, start_col, end_col)
    train_result2_scale, test_result2_scale = split_train_test(result0_class2, result1_class2)
    train_result2_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class2.csv', index=False)
    test_result2_scale.to_csv(output + '0' + file + '\\testdata(scale)_class2.csv', index=False)

#class3**********************************************************************************

    columns_ranges3 = [(i, min(i + interval_class3, interval_class3*49+2)) for i in range(2, interval_class3*49+2, interval_class3)]
    print(columns_ranges3)

    for start_col, end_col in columns_ranges3:
        result0_class3 = normalize_columns(result0_class3, result1_class3, start_col, end_col)
    train_result3_scale, test_result3_scale = split_train_test(result0_class3, result1_class3)
    train_result3_scale.to_csv(output + '0' + file + '\\trainingdata(scale)_class3.csv', index=False)
    test_result3_scale.to_csv(output + '0' + file + '\\testdata(scale)_class3.csv', index=False)



# Each later list removes one 16-day composite, giving the A16d--A128d
# windows while retaining the crop/class order used by the model.
intervals_maize = [[14,11,11], [13,10,10], [12,9,9], [11,8,8], [10,7,7], [9,6,6], [8,5,5], [7,4,4], [6,3,3]]
intervals_rice = [[17,11,12,11], [16,10,11,10], [15,9,10,9], [14,8,9,8], [13,7,8,7], [12,6,7,6], [11,5,6,5], [10,4,5,4], [9,3,4,3]]
intervals_soybean = [[13,10,11,11], [12,9,10,10], [11,8,9,9], [10,7,8,8], [9,6,7,7], [8,5,6,6], [7,4,5,5], [6,3,4,4], [5,2,3,3]]
intervals_wheat = [[21,12,15,10], [20,11,14,9], [19,10,13,8], [18,9,12,7], [17,8,11,6], [16,7,10,5], [15,6,9,4], [14,5,8,3], [13,4,7,2]]

file_dates = ['', '_A16d', '_A32d', '_A48d', '_A64d', '_A80d', '_A96d', '_A112d', '_A128d']


# The suffix identifies one early-prediction window; each class-specific
# subdirectory receives unscaled and historical-only-scaled train/test CSVs.
output_path = f'E:\\D盘WYZ\\Process_country(Non_scale)\\test{year}\\' + crop_type + '_time window\\class'  #test2021,2022

# ``start=3`` selects the 2002 column in a 2000-first yield table. Use
# ``end`` 22, 23, and 24 for target years 2020, 2021, and 2022, respectively.
start = 3  #2020: start=3;  2021: start=4;  2022: start=5
end = 22

if crop_type == 'maize':
    intervals = intervals_maize
    for interval, file_date in zip(intervals, file_dates):
        data_process_maize(start=start, end=end, interval=interval, output=output_path, file=file_date)

elif crop_type == 'rice':
    intervals = intervals_rice
    for interval, file_date in zip(intervals, file_dates):
        data_process_rice(start=start, end=end, interval=interval, output=output_path, file=file_date)

elif crop_type == 'soybean':
    intervals = intervals_soybean
    for interval, file_date in zip(intervals, file_dates):
        data_process_soybean(start=start, end=end, interval=interval, output=output_path, file=file_date)

elif crop_type == 'wheat':
    intervals = intervals_wheat
    for interval, file_date in zip(intervals, file_dates):
        data_process_wheat(start=start, end=end, interval=interval, output=output_path, file=file_date)

