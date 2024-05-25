# -*- coding: utf-8 -*-
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
import path


'''
Extract normality test (Anderson-Darling, Shapiro-Wilk, Kolmogorov-Smirnov, Lilliefors)
If data is not applicable to a test, the result will be set as 'null'

Prerequisites:
For Anderson-Darling, Shapiro-Wilk, Kolmogorov-Smirnov, Lilliefors Test:
    Column data should be of quantitative type.
For Chi-square goodness of fit Test:
    Column data should be categorical.
For Shapiro-Wilk Test: 
    Sample size should be less than 50.
For Lilliefors Test:
    Sample size should be more than 50.
'''

def extract_normality_test_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        # read csv
        df = pd.read_csv(file_path)
        test_info_list = []
        # all columns
        columns = df.columns

        for col in columns:
            column_data_type = utils.determine_data_type(series=df[col], dataset_name=file_name)
            # Initialize variables
            ad_results = 'null'
            sw_p = 'null'
            ks_p = 'null'
            lf_p = 'null'
            
            # select quant columns
            # if utils.is_continuous(df[col]):
            if column_data_type == 'quant':
                col_data = df[col].dropna()  # Remove NA values for test
                # Check if standard deviation is zero or very small
                if col_data.std(ddof=1) < 1e-8:
                    continue

                # col_data = utils.process_special_cont_data(col_data)

                # Anderson-Darling test
                ad_output = anderson(col_data)
                ad_stat = ad_output.statistic
                ad_crit = ad_output.critical_values[0] # Critical value for significance level of 15%
                #  significance_level=array([15., 10., 5., 2.5, 1.]
                # Build result dict for Anderson-Darling
                ad_results = {'stat': round(ad_stat, 5), 'crit': round(ad_crit, 5)}

                # Shapiro-Wilk test if sample size is less than 50
                if len(col_data) < 50:
                    _, sw_p = shapiro(col_data)
                    sw_p = 'null' if np.isnan(sw_p) else sw_p
                else:
                    sw_p = 'null'

                # Kolmogorov-Smirnov test
                # Note that standardization is needed before performing Kolmogorov-Smirnov test for normality test
                col_data_normalized = (col_data - np.mean(col_data)) / np.std(col_data)
                _, ks_p = kstest(col_data_normalized, 'norm')
                ks_p = 'null' if np.isnan(ks_p) else ks_p

                # Lilliefors test if sample size is greater than 50
                if len(col_data) > 50:
                    _, lf_p = lilliefors(col_data)
                    lf_p = 'null' if np.isnan(lf_p) else lf_p
                else:
                    lf_p = 'null'

            # Categorical column
            elif column_data_type == 'cate':
                col_data = df[col]
                observed = pd.crosstab(index=col_data, columns="count")
                # For Anderson-Darling, Shapiro-Wilk, Kolmogorov-Smirnov, Lilliefors Test, categorical data is not applicable
                ad_results = 'null'
                sw_p = 'null'
                ks_p = 'null'
                lf_p = 'null'
            # else:
            #     # continous data, applicable, continue
            #     continue

            # If stat < crit in Anderson-Darling test: Selected variables are normally distributed), vice versa
            # If any other test's p > 0.05 (Accept the null hypothesis, consider selected variables are normally distributed), vice versa
            p_tests = [(sw_p, 0.05), (ks_p, 0.05), (lf_p, 0.05)]
            norm_con = (any(t[0] != 'null' and t[0] > t[1] for t in p_tests) or (ad_results != 'null' and (ad_stat < ad_crit)))
            not_norm_con = (
                (sw_p == 'null' or sw_p <= 0.05)
                and (ks_p == 'null' or ks_p <= 0.05 )
                and (lf_p == 'null' or lf_p <= 0.05)
                and ((ad_results != 'null' and (ad_stat >= ad_crit)))
                and (sw_p != 'null' or ks_p != 'null' or lf_p != 'null')
            )
            if flag == 0:
                comp_con = norm_con
            elif flag == 1:
                comp_con = not_norm_con
            
            if ad_results == 'null':
                ad_conclusion = 'Not applicable'
            else:
                ad_conclusion = 'Normally distributed' if ((ad_results != 'null' and (ad_stat < ad_crit))) else 'Non-normally distributed'
            if sw_p == 'null':
                sw_conclusion = 'Not applicable'
            else:
                sw_conclusion = 'Normally distributed' if (sw_p != 'null' and sw_p > 0.05) else 'Non-normally distributed'
            if ks_p == 'null':
                ks_conclusion = 'Not applicable'
            else:
                ks_conclusion = 'Normally distributed' if (ks_p != 'null' and ks_p > 0.05) else 'Non-normally distributed'
            if lf_p == 'null':
                lf_conclusion = 'Not applicable'
            else:
                lf_conclusion = 'Normally distributed' if (lf_p != 'null' and lf_p > 0.05) else 'Non-normally distributed'
                
            if sw_p != 'null': sw_p = round(sw_p, 5)
            if ks_p != 'null': ks_p = round(ks_p, 5)
            if lf_p != 'null': lf_p = round(lf_p, 5)
            if comp_con:
                test_info_list.append((
                    file_name,
                    col,
                    # json.dumps(ad_results),  # convert dict to string
                    # sw_p,
                    # ks_p,
                    # lf_p
                    json.dumps({'AD results': json.dumps(ad_results), 'conclusion': ad_conclusion}),
                    json.dumps({'p value': sw_p, 'conclusion': sw_conclusion}),
                    json.dumps({'p value': ks_p, 'conclusion': ks_conclusion}),
                    json.dumps({'p value': lf_p, 'conclusion': lf_conclusion})
                ))

        # Append list of tuples to CSV file and remove duplicates
        new_data = pd.DataFrame(test_info_list, columns=[
                                'Dataset Name', 'Column', 'Anderson-Darling Test', 'Shapiro-Wilk Test of Normality', 'Kolmogorov-Smirnov Test for Normality', 'Lilliefors Test'])
        new_data = new_data.drop_duplicates()
        # Check if the file exists; if yes, append in new data without headers
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
if __name__=='__main__':
    # Get all dataset names
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    # Extract correlation info for all the datasets
    for dataset_name in dataset_names:
        test_info_list = extract_normality_test_info(file_name=dataset_name, output_name='Normality test info extraction (Normally distributed)', flag=0)
        test_info_list = extract_normality_test_info(file_name=dataset_name, output_name='Normality test info extraction (Non-normally distributed)', flag=1)
    print('End.')