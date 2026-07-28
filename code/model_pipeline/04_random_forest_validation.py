"""Step 4: validate cluster-specific Random Forest yield models.

Inputs are the scaled class-specific CSVs created by Step 3:
``trainingdata(scale)_classN.csv`` and ``testdata(scale)_classN.csv``. Their
first column is ``adm0_name``, their second column is the FAOSTAT yield target,
their final column is ``year``, and all columns between them are ordered
16-day feature blocks. The block order is the 49-table legacy sequence from
Step 3: ET, EVI, LSTD, LSTN, NDVI, PRE, TEM; for each variable, mean, five
normalized-value frequencies, and standard deviation. The feature selections
below are positional and are valid only for that exact arrangement.

``feature_combination=0`` selects the seven mean blocks, ``1`` selects the
seven mean and seven standard-deviation blocks, and ``2`` selects all 49
blocks (the active configuration). A 100-tree RandomForestRegressor is fitted
for every shuffled 10-fold split. Test predictions from the ten fold models
are averaged within each seed. The active seed list (30--300 in steps of 30)
therefore fits 100 forests per crop/class/lead-time; the final summary tables
average the per-seed metric values.

The cluster table is also read with ``MEAN``. The class-specific ``harvests``
arrays are calendar-day prediction cut-offs; values larger than 365 represent
seasons crossing a calendar year. A country is excluded when that cut-off is
fewer than 30 days after its mean planting date (``MEAN``), preventing an
unrealistically early prediction. If the crop calendar or lead-time spacing is
changed, recalculate both ``intervals_*`` and ``harvest_*`` rather than editing
only one list.

This file intentionally preserves the original executable statements. In its
active call, however, ``crossvalid`` declares the argument ``feature`` whereas
the caller supplies ``feature_tag``. Python will therefore raise a keyword
argument error if that line is run unchanged. This is documented rather than
altered here to preserve the archived implementation; replace ``feature_tag``
with ``feature`` manually in a working copy before executing the legacy script.
"""

import math
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import ensemble
from sklearn.metrics import mean_squared_error, r2_score, make_scorer, mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.base import clone
import re
import os
import joblib

def seed_everything(seed=22):
    """Set Python and NumPy random generators used by the repeated validation."""
    random.seed(seed)
    np.random.seed(seed)


#seed_everything(220)
all_results = []
all_grouped_results = []
def crossvalid(output_path, intervals, feature_combination, harvests, file_dates, crop, clf, feature, seed, model_save=False,
        model_save_dir=None):
    """Fit one crop/lead-time/seed ensemble and append its evaluation records.

    Outputs are per-seed country prediction tables, one serialized forest per
    fold, class-level metrics, and summary-ready records in the global lists.
    The target is temporarily min-max scaled using training rows and restored
    before all reported R2, RMSE, MAE, and percent-error calculations.
    """
    global all_results
    global all_grouped_results
    seed_everything(seed)

    mean_r2s = []
    mean_rmses = []
    mean_maes = []
    mean_predictions_all = []
    Ytest_all = []
    IDtest_all = []

    # output = output_path + crop + '_time window\\class0' + file_dates + '\\'
    output = f"{output_path}{crop}_time window\\class0{file_dates}\\"
    output_cluster = fr'E:\D盘WYZ\SPAM2020\cluster\{crop}_cluster_final.csv'
    data_cluster = pd.read_csv(output_cluster, usecols=['adm0_name', 'MEAN'])

    if crop == 'maize':
        class_num = ['0', '1', '2']
    else:
        class_num = ['0', '1', '2', '3']

    for i in class_num:
        data = pd.read_csv(output + 'trainingdata(scale)_class' + i + '.csv')


        data_test = pd.read_csv(output + 'testdata(scale)_class' + i + '.csv')

        data = data.merge(data_cluster, on=['adm0_name'], how='left')
        data_test = data_test.merge(data_cluster, on=['adm0_name'], how='left')


        harvest = harvests[int(i)]


        # ===============================
        # ===============================
        before_train = len(data)

        data = data[harvest - data['MEAN'] >= 30]
        data = data.drop(columns=['MEAN'])

        after_train = len(data)
        removed_train = before_train - after_train

        print(f"{crop}_class{i}_Training data 删除的样本个数: {removed_train}")

        # ===============================
        # ===============================
        before_test = len(data_test)

        data_test = data_test[harvest - data_test['MEAN'] >= 30]
        data_test = data_test.drop(columns=['MEAN'])

        after_test = len(data_test)
        removed_test = before_test - after_test

        print(f"{crop}_class{i}_Test data 删除的样本个数: {removed_test}")


        interval = intervals[int(i)]


        column_ranges0 = [(2, 2+interval), (2+interval*7, 2+interval*8),
                         (2+interval*14, 2+interval*15), (2+interval*21, 2+interval*22), (2+interval*28, 2+interval*29),
                         (2+interval*35, 2+interval*36), (2+interval*42, 2+interval*43)]

        column_ranges1 = [(2, 2+interval), (2+interval*6, 2+interval*7), (2+interval*7, 2+interval*8),
                         (2+interval*13, 2+interval*14), (2+interval*14, 2+interval*15), (2+interval*20, 2+interval*21),
                         (2+interval*21, 2+interval*22), (2+interval*27, 2+interval*28), (2+interval*28, 2+interval*29),
                         (2+interval*34, 2+interval*35), (2+interval*35, 2+interval*36), (2+interval*41, 2+interval*42),
                         (2+interval*42, 2+interval*43), (2+interval*48, 2+interval*49)]

        if feature_combination == 0:
            x = pd.concat([data.iloc[:, range_start:end_start] for range_start, end_start in column_ranges0], axis=1)
        elif feature_combination == 1:
            x = pd.concat([data.iloc[:, range_start:end_start] for range_start, end_start in column_ranges1], axis=1)
        elif feature_combination == 2:
            x = data.iloc[:, 2:-1]


        y0 = data.iloc[:, 1]
        y_min = y0.min()
        y_max = y0.max()
        y = (y0 - y_min) / (y_max - y_min)

        if feature_combination == 0:
            Xtest = pd.concat([data_test.iloc[:, range_start:end_start] for range_start, end_start in column_ranges0], axis=1)
        elif feature_combination == 1:
            Xtest = pd.concat([data_test.iloc[:, range_start:end_start] for range_start, end_start in column_ranges1], axis=1)
        elif feature_combination == 2:
            Xtest = data_test.iloc[:, 2:-1]

        Ytest = data_test.iloc[:, 1]



        kf = KFold(n_splits=10, shuffle=True, random_state=seed)

        r2s = []
        rmses = []
        maes = []
        predictions = []

        total_columns = x.shape[1]

        # 手动交叉验证
        for train_index, test_index in kf.split(x):
            # 分割数据
            X_train, X_test = x.iloc[train_index], x.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]

            model = ensemble.RandomForestRegressor(n_estimators=100, random_state=seed, n_jobs=-1)  #模型！！！！！！

            # 训练模型
            model.fit(X_train, y_train)


            # =========================
            # =========================
            if model_save:

                if model_save_dir is None:
                    raise ValueError(
                        "model_save=True 时必须提供 model_save_dir"
                    )

                model_dir = os.path.join(
                    model_save_dir,
                    crop,
                    f"seed_{seed}"
                )

                os.makedirs(model_dir, exist_ok=True)

                model_name = (
                    f"{clf}"
                    f"{feature}"
                    f"{file_dates}"
                    f"_class{i}"
                    f"_seed{seed}"
                    f"_fold{len(r2s) + 1}.pkl"
                )

                model_path = os.path.join(model_dir, model_name)

                joblib.dump(model, model_path)
            #-----------------------------------------------------
            # -----------------------------------------------------

            y_pred0 = model.predict(X_test)

            y_pred = y_pred0 * (y_max - y_min) + y_min
            y_test1 = y_test * (y_max - y_min) + y_min


            r2 = r2_score(y_test1, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test1, y_pred))
            mae = mean_absolute_error(y_test1, y_pred)

            r2s.append(r2)
            rmses.append(rmse)
            maes.append(mae)

            prediction0 = model.predict(Xtest)
            prediction = prediction0 * (y_max - y_min) + y_min
            predictions.append(prediction)


        mean_r2 = sum(r2s) / len(r2s)
        mean_rmse = sum(rmses) / len(rmses)
        mean_mae = sum(maes) / len(maes)
        mean_predictions = sum(predictions) / len(predictions)

        mean_r2s.append(mean_r2)
        mean_rmses.append(mean_rmse)
        mean_maes.append(mean_mae)
        mean_predictions_all.append(mean_predictions.flatten())
        Ytest_all.append(Ytest)
        IDtest_all.append(data_test['adm0_name'])

        R_2_group_test = r2_score(Ytest, mean_predictions)
        rmse_group_test = np.sqrt(mean_squared_error(Ytest, mean_predictions))
        mae_group_test = mean_absolute_error(Ytest, mean_predictions)

        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-cross R2: {mean_r2}")
        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-cross RMSE: {mean_rmse}")
        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-cross MAE: {mean_mae}")
        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-Tset R2: {R_2_group_test}")
        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-Tset RMSE: {rmse_group_test}")
        print(f"{clf}-{file_dates}-{crop}-class{i}-{feature}-Tset MAE: {mae_group_test}")

        all_results.append({
            'crop': crop,
            'file_date': file_dates,
            'class': i,
            'seed': seed,

            'cv_r2': mean_r2,
            'cv_rmse': mean_rmse,
            'cv_mae': mean_mae,

            'test_r2': R_2_group_test,
            'test_rmse': rmse_group_test,
            'test_mae': mae_group_test
        })

    mean_all_r2 = sum(mean_r2s) / len(mean_r2s)
    mean_all_rmse = sum(mean_rmses) / len(mean_rmses)
    mean_all_mae = sum(mean_maes) / len(mean_maes)
    combined_predictions = np.concatenate(mean_predictions_all)
    combined_Ytest = np.concatenate(Ytest_all)
    combined_ID = np.concatenate(IDtest_all)

    predictions_df = pd.DataFrame({
        'adm0_name': combined_ID,
        'yield': combined_Ytest,
        'predictions': combined_predictions
    })


    predictions_df['percent_error'] = (
            (predictions_df['predictions'] - predictions_df['yield'])
            / predictions_df['yield'] * 100
    )

    # predictions_df.to_csv(output + clf + f'{feature}_grouped202605_r42.csv', index=False)
    csv_name = (
            clf +
            f'{feature}_grouped'
            f'_r{seed}.csv'
    )

    predictions_df.to_csv(
        os.path.join(output, csv_name),
        index=False
    )



    R_2_test = r2_score(combined_Ytest, combined_predictions)
    rmse_test = np.sqrt(mean_squared_error(combined_Ytest, combined_predictions))
    mae_test = mean_absolute_error(combined_Ytest, combined_predictions)

    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-cross R2: {mean_all_r2}")
    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-cross RMSE: {mean_all_rmse}")
    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-cross MAE: {mean_all_mae}")
    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-Test R2: {R_2_test}")
    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-Test RMSE: {rmse_test}")
    print(f"{clf}-{file_dates}-{crop}-{feature}_grouped-Test MAE: {mae_test}")

    all_grouped_results.append({

        'crop': crop,
        'file_date': file_dates,
        'seed': seed,

        'group_cv_r2': mean_all_r2,
        'group_cv_rmse': mean_all_rmse,
        'group_cv_mae': mean_all_mae,

        'group_test_r2': R_2_test,
        'group_test_rmse': rmse_test,
        'group_test_mae': mae_test
    })




# intervals = [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13]
# file_dates = ['10_16', '09_30', '09_14', '08_29', '08_13', '07_28', '07_12', '06_26', '06_10', '05_25', '05_09', '04_23', '04_07']

crop = ['wheat', 'rice', 'soybean', 'maize']

# Lead-time window lengths (0, 16, ..., 128 days before harvest), ordered by
# phenotype class. They must match the Step-3 CSV column-block widths.
intervals_maize = [[14,11,11], [13,10,10], [12,9,9], [11,8,8], [10,7,7], [9,6,6], [8,5,5], [7,4,4], [6,3,3]]
intervals_rice = [[17,11,12,11], [16,10,11,10], [15,9,10,9], [14,8,9,8], [13,7,8,7], [12,6,7,6], [11,5,6,5], [10,4,5,4], [9,3,4,3]]
intervals_soybean = [[13,10,11,11], [12,9,10,10], [11,8,9,9], [10,7,8,8], [9,6,7,7], [8,5,6,6], [7,4,5,5], [6,3,4,4], [5,2,3,3]]
intervals_wheat = [[21,12,15,10], [20,11,14,9], [19,10,13,8], [18,9,12,7], [17,8,11,6], [16,7,10,5], [15,6,9,4], [14,5,8,3], [13,4,7,2]]
intervals_wheats = [[21,12,15,10,8], [20,11,14,9,7], [19,10,13,8,6], [18,9,12,7,5], [17,8,11,6,4], [16,7,10,5,3], [15,6,9,4,2], [14,5,8,3,1], [13,4,7,2,1]]

file_dates = ['', '_A16d', '_A32d', '_A48d', '_A64d', '_A80d', '_A96d', '_A112d', '_A128d']

harvest_maize = [[128+365,288,256], [112+365,272,240], [96+365,256,224], [80+365,240,208], [64+365,224,192],
                 [48+365,208,176], [32+365,192,160], [16+365,176,144], [0+365,160,128]]
harvest_rice = [[144+365,288,192,336], [128+365,272,176,320], [112+365,256,160,304], [96+365,240,144,288],
                [80+365,224,128,272], [64+365,208,112,256], [48+365,192,96,240], [32+365,176,80,224], [16+365,160,64,208]]
harvest_soybean = [[144+365,256,304,192],[128+365,240,288,176], [112+365,224,272,160], [96+365,208,256,144],
                   [80+365,192,240,128], [64+365,176,224,112], [48+365,160,208,96], [32+365,144,192,80], [16+365,128,176,64]]
harvest_wheat = [[224+365,320,176+365,96+365],[208+365,304,160+365,80+365], [192+365,288,144+365,64+365],
                [176+365,272,128+365,48+365], [160+365,256,112+365,32+365], [144+365,240,96+365,16+365],
                 [128+365,224,80+365,0+365], [112+365,208,64+365,-16+365], [96+365,192,48+365,-32+365]]


test_year = 2020
Mode = 2  #0,1,2

output_path = f'F:\\重要文档\\data\\test{test_year}\\'
model_save_dir = fr'E:\D盘WYZ\Process_country(Non_scale)\test{test_year}\models'
seed_list = list(range(30, 301, 30))


for crop_type in crop:
    intervals0 = None
    harvest0 = None
    if crop_type == 'maize':
        intervals0 = intervals_maize
        harvest0 = harvest_maize
    elif crop_type == 'rice':
        intervals0 = intervals_rice
        harvest0 = harvest_rice
    elif crop_type == 'soybean':
        intervals0 = intervals_soybean
        harvest0 = harvest_soybean
    elif crop_type == 'wheat':
        intervals0 = intervals_wheat
        harvest0 = harvest_wheat
    # elif crop_type == 'wheats':
    #     intervals0 = intervals_wheats
    #     harvest0 = harvest_maize

    # for intervals, harvests, file_date in zip(intervals0, harvest0, file_dates):
    #     crossvalid(output_path2020, intervals, harvests, file_date, crop_type, 'RF', '02')
    #     print(f"Results saved: {file_date} _ {crop_type}________________")
    for seed in seed_list:

        print(f"\n================ Seed: {seed} ================\n")

        for intervals, harvests, file_date in zip(intervals0, harvest0, file_dates):
            # IMPORTANT: the preserved call below uses ``feature_tag`` while
            # ``crossvalid`` declares ``feature``. See the module docstring.
            crossvalid(
                output_path=output_path,
                intervals=intervals,
                feature_combination=Mode,
                harvests=harvests,
                file_dates=file_date,
                crop=crop_type,
                clf='RF',
                feature=f"0{Mode}",
                seed=seed,
                model_save= False,
                model_save_dir=None
            )

            print(
                f"Results saved: "
                f"{file_date} _ {crop_type} _ seed{seed}"
            )

print('***************************************************************************************************************')
results_df = pd.DataFrame(all_results)

summary_df = (
    results_df
    .groupby(
        ['crop', 'file_date', 'class'],
        as_index=False
    )[
        [
            'cv_r2',
            'cv_rmse',
            'cv_mae',
            'test_r2',
            'test_rmse',
            'test_mae'
        ]
    ]
    .mean()
)

summary_df.to_csv(
    fr'F:\重要文档\data\test{test_year}\RF0{Mode}_summary_mean.csv',
    index=False
)


grouped_df = pd.DataFrame(all_grouped_results)

grouped_summary_df = (
    grouped_df
    .groupby(
        ['crop', 'file_date'],
        as_index=False
    )[
        [
            'group_cv_r2',
            'group_cv_rmse',
            'group_cv_mae',
            'group_test_r2',
            'group_test_rmse',
            'group_test_mae'
        ]
    ]
    .mean()
)

grouped_summary_df.to_csv(
    fr'F:\重要文档\data\test{test_year}\RF0{Mode}_grouped_summary_mean.csv',
    index=False
)
