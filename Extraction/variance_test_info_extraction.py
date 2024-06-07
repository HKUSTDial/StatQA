# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

from scipy.stats import mood, levene, bartlett, f_oneway
import pandas as pd
import numpy as np
import json
import utils
import path


'''
Prerequisite:
- Mood's test of variance: Two independent consecutive samples
- Levene's test: Two independent consecutive samples
- Bartlett's test: Two independent samples; normal distribution
- F-test: Two independent consecutive samples; normal distribution

Independence checks on continuous variables is assumed as a default.
'''
def process_result(method_name, result):
    if result is not None:
        if result[1] < 0.05:
            conclusion = 'Variance significantly difference between them'
        else:
            conclusion = 'Variance not significantly difference between them'
        return {'stat': round(result[0], 5), 'p value': round(result[1], 5), 'conclusion': conclusion}
    else:
        # Return 'null' result for methods not applicable due to failed preconditions
        return {'stat': 'null', 'p value': 'null', 'conclusion': 'Not applicable'}


def extract_variance_test_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)

        test_info_list = []
        continuous_columns = [col for col in df.columns if utils.determine_data_type(series=df[col], dataset_name=file_name) == "quant"]

        for i in range(len(continuous_columns)):
            for j in range(i + 1, len(continuous_columns)):
                col1 = continuous_columns[i]
                col2 = continuous_columns[j]

                # Delete rows that contain missing values
                df_clean = df.dropna(subset=[col1, col2])
                sample1 = df_clean[col1]
                sample2 = df_clean[col2]

                # Variance test is meaningless if variance=0. Prevent a division error of zero.
                if (sample1 <= 0).any() or (sample2 <= 0).any() or np.isinf(sample1).any() or np.isinf(sample2).any():
                    continue
                if np.std(sample1) == 0 or np.std(sample2) == 0:
                    continue

                normality1 = utils.is_normality_ad(sample1)
                normality2 = utils.is_normality_ad(sample2)

                # Process each test with precondition checks
                mood_init_res = mood(sample1, sample2)
                levene_init_res = levene(sample1, sample2)
                bartlett_init_res = bartlett(sample1, sample2)
                f_test_init_res = f_oneway(sample1, sample2)

                # If p < 0.05, reject null hypothesis, and consider there is a significant difference between the two groups
                # For p >= 0.05: considering there is NOT a significant difference
                sig_diff= (any([mood_init_res[1], levene_init_res[1], bartlett_init_res[1], f_test_init_res[1]]) >= 0.05)
                not_sig_diff = (all([mood_init_res[1], levene_init_res[1], bartlett_init_res[1], f_test_init_res[1]]) < 0.05)
                if flag == 0:
                    var_con = sig_diff
                elif flag == 1:
                    var_con = not_sig_diff

                mood_results = process_result('Mood Variance Test', mood_init_res)
                levene_results = process_result('Levene Test', levene_init_res if len(sample1) > 2 and len(sample2) > 2 else None)
                bartlett_results = process_result('Bartlett Test', bartlett_init_res if normality1 and normality2 else None)
                f_test_results = process_result('F-Test for Variance', f_test_init_res if normality1 and normality2 else None)

                if var_con:
                    test_info_list.append((
                        file_name,
                        col1,
                        col2,
                        json.dumps(mood_results),
                        json.dumps(levene_results),
                        json.dumps(bartlett_results),
                        json.dumps(f_test_results)
                    ))

        new_data = pd.DataFrame(test_info_list, columns=[
                                'Dataset Name', 'Column 1', 'Column 2', 'Mood Variance Test', 'Levene Test', 'Bartlett Test', 'F-Test for Variance'])
        new_data = new_data.drop_duplicates()

        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            new_data.to_csv(output_path, mode='a', header=False, index=False)
        else:
            new_data.to_csv(output_path, mode='w', header=True, index=False)

        print(f"[+] Dataset: " + file_name + " Done!")
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")


# main
if __name__=='__main__':
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    for dataset_name in dataset_names:
        test_info_list = extract_variance_test_info(file_name=dataset_name, output_name='Variance test info extraction (Variance significantly different)', flag=0)
        test_info_list = extract_variance_test_info(file_name=dataset_name, output_name='Variance test info extraction (Variance not significantly different)', flag=1)
    print('End.')
