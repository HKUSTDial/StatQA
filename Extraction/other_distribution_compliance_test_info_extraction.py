# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
from scipy.stats import anderson, shapiro, kstest, chi2_contingency
from statsmodels.stats.diagnostic import lilliefors
import glob
import utils
import json
from scipy.stats import kstest, expon, uniform, gamma
import path


"""
Extract information about the fit of data columns to specific theoretical distributions using the Kolmogorov-Smirnov test.
In the output csv file, Column 1 records the title of the selected data column, and Column 2 records the test method.
"""
def extract_other_distribution_test_info(file_name: str, output_name: str, flag=0):
    try:

        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)

        test_info_list = []
        distributions = {
            'Exponential': expon.cdf,
            'Uniform': uniform.cdf,
            'Gamma': gamma(2).cdf  # Use shape=2 for gamma
        }
        
        for dist_name, dist_func in distributions.items():
            for col in df.columns:
                col_series = df[col]
                column_data_type = utils.determine_data_type(series=col_series, dataset_name=file_name)
                # Check if the data is cotinuous data
                if column_data_type != 'quant':
                    # print(f"[ ] Dataset: {file_name}. Skipping column {col} for not quantitative.")
                    continue

                # Check if the data has more than one unique value
                if len(df[col].unique()) == 1:
                    # print(f"[ ] Dataset: {file_name}. Skipping column {col} for only one unique value.")
                    continue

                col_data = df[col].dropna()  # Remove NA values for test

                # Rescale data if testing uniform distribution
                if dist_name == 'Uniform':
                    col_data = (col_data - col_data.min()) / (col_data.max() - col_data.min())

                # Kolmogorov-Smirnov test
                # Note that standardization is NOT needed before performing Kolmogorov-Smirnov test for tests except normality test
                _, ks_p_value = kstest(col_data, dist_func)

                # If any p > 0.05, accept null hypothesis, and consider the data fit the specified theoretical distribution to some extent
                # p <= 0.05 for NOT fit
                fit_dist = (ks_p_value > 0.05)
                not_fit_dist = (ks_p_value <= 0.05)
                if flag == 0:
                    fit_con = fit_dist
                elif flag == 1:
                    fit_con = not_fit_dist
                if ks_p_value == 'null':
                    ks_conclustion = 'Not applicable'
                else:
                    ks_conclustion = 'Compliance' if (ks_p_value > 0.05) else 'Non-compliance'
                if ks_p_value != 'null': ks_p_value = round(ks_p_value, 5)
                if fit_con:
                    test_info_list.append((
                        file_name,
                        col,
                        dist_name,
                        json.dumps({'p value': ks_p_value, 'conclusion': ks_conclustion})
                    ))

        new_data = pd.DataFrame(test_info_list, columns=[
            'Dataset Name', 
            'Column', 
            'Distribution', 
            'Kolmogorov-Smirnov Test'
        ])
        new_data = new_data.drop_duplicates()

        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            new_data.to_csv(output_path, mode='a', header=False, index=False)
        else:
            new_data.to_csv(output_path, mode='w', header=True, index=False)

        print(f"[+] Dataset: " + file_name + " Done!")
        return test_info_list
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")
        return None


# main
if __name__ == '__main__':
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    for dataset_name in dataset_names:
        test_info_list = extract_other_distribution_test_info(file_name=dataset_name, output_name='Other distribution info extraction (Compliance)', flag=0)
        test_info_list = extract_other_distribution_test_info(file_name=dataset_name, output_name='Other distribution info extraction (Not compliance)', flag=1)
    print('End.')