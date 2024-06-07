# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import utils
import json
import path


'''
Extract correlation information into a csv file

For data that are continuous variables rather than categorical variables;
Kendall correlation coefficients should be used for data with sample sizes less than 50, and unlimited for sample sizes greater than 50;
For methods not applicable, the result is recorded as 'null';
Any one correlation coefficient with an absolute value greater than 0.5 will be summarized and recorded in csv.
'''
def extract_correlation_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)  # Load the dataset

        correlation_info_list = []
        columns = df.columns  # Get all column names
        
        # Measure and compare each pair of columns
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                # Check if the variables are of quant type, skip if it's not.
                data_type_i = utils.determine_data_type(df[columns[i]], dataset_name=file_name)
                data_type_j = utils.determine_data_type(df[columns[j]], dataset_name=file_name)
                # If any column is not a quant variable, skip and continue with the next loop
                if data_type_i != "quant" or data_type_j != "quant":
                    continue
                # Check if the data has enough columns for correlation analysis
                if df[[columns[i], columns[j]]].shape[1] < 2:
                    continue  # If the number of columns is less than 2, skip
                # Deal with invalid value
                df_pair = df[[columns[i], columns[j]]].dropna()
                # If the processed data is empty or any column is a constant, skip
                if df_pair.empty or (df_pair.nunique() <= 1).any():
                    continue
                # Check if the denominator is not zero
                if df_pair.std(numeric_only=True).eq(0).any():
                    continue

                pearson_corr_value = spearman_corr_value = kendall_corr_value = partial_corr_value = None
                # Based on sample size, decide which correlation methods to use
                # Compute the correlation matrix and take the corresponding results
                if len(df) >= 50:
                    # Calculate all possible correlation coefficients when sample size meets the requirement
                    # Calculate correlation coefficient: Pearsion, Spearman, Kendall, Partial
                    pearson_corr_value = df[[columns[i], columns[j]]].corr(method='pearson', numeric_only=True).iloc[0, 1]
                    spearman_corr_value = df[[columns[i], columns[j]]].corr(method='spearman', numeric_only=True).iloc[0, 1]
                    kendall_corr_value = df[[columns[i], columns[j]]].corr(method='kendall', numeric_only=True).iloc[0, 1]
                    partial_corr_value = df[[columns[i], columns[j]]].pcorr().iloc[0, 1]
                else:
                    # Only calculate Kendall when sample size is less than 50 (Small sample size)
                    kendall_corr_value = df[[columns[i], columns[j]]].corr(method='kendall').iloc[0, 1]

                # Correlation coefficient with an absolute value greater than 0.5: Strongly correlated
                # abs <= 0.5 for not strongly correlated
                strong_cor_con = (
                    abs(pearson_corr_value or 0) > 0.5 or
                    abs(spearman_corr_value or 0) > 0.5 or
                    abs(kendall_corr_value or 0) > 0.5 or
                    abs(partial_corr_value or 0) > 0.5
                )
                not_strong_cor_con = (
                    abs(pearson_corr_value or 0) <= 0.5 and
                    abs(spearman_corr_value or 0) <= 0.5 and
                    abs(kendall_corr_value or 0) <= 0.5 and
                    abs(partial_corr_value or 0) <= 0.5
                )
                if flag == 0:
                    cor_condition = strong_cor_con
                elif flag == 1:
                    cor_condition = not_strong_cor_con
                pearson_conclusion = 'Strongly correlated' if abs(pearson_corr_value or 0) > 0.5 else 'Not strongly correlated'
                spearman_conclusion = 'Strongly correlated' if abs(spearman_corr_value or 0) > 0.5 else 'Not strongly correlated'
                kendall_conclusion = 'Strongly correlated' if abs(kendall_corr_value or 0) > 0.5 else 'Not strongly correlated'
                res_not_applicable = json.dumps({'coefficient': 'null', 'conclusion': 'Not applicable'})
                if (cor_condition):
                    # Append information to the list
                    correlation_info_list.append((
                        file_name,
                        columns[i],
                        columns[j],
                        res_not_applicable if pearson_corr_value is None else json.dumps({'coefficient': round(pearson_corr_value, 5), 'conclusion': pearson_conclusion}),
                        res_not_applicable if spearman_corr_value is None else json.dumps({'coefficient': round(spearman_corr_value, 5), 'conclusion': spearman_conclusion}),
                        res_not_applicable if kendall_corr_value is None else json.dumps({'coefficient': round(kendall_corr_value, 5), 'conclusion': kendall_conclusion})
                        # 'null' if partial_corr_value is None else round(partial_corr_value, 5)
                    ))
        
        # Prepare DataFrame for storing the correlation info
        new_data = pd.DataFrame(correlation_info_list, columns=[
                                # 'Dataset Name', 'Column 1', 'Column 2', 'Pearson Correlation Coefficient', 'Spearman Correlation Coefficient', 'Kendall Correlation Coefficient', 'Partial Correlation Coefficient'])
                                'Dataset Name', 'Column 1', 'Column 2', 'Pearson Correlation Coefficient', 'Spearman Correlation Coefficient', 'Kendall Correlation Coefficient'])
        new_data = new_data.drop_duplicates()  # Remove potential duplicates

        # Check if output file exists and write the new data into it
        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            # Append new info to existing file
            new_data.to_csv(output_path, mode='a', header=False, index=False)
        else:
            # Write to a new file if it doesn't exist
            new_data.to_csv(output_path, mode='w', header=True, index=False)
        print(f"[+] Dataset: " + file_name + " Done!")
        return correlation_info_list  # Return the list of correlation info for further usage
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")
        return None  # Return None to indicate that there was an error during the execution


# main
if __name__ == '__main__':
    # Get all dataset names
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    # Process each dataset and extract the correlation info
    for dataset_name in dataset_names:
        correlation_info_list = extract_correlation_info(file_name=dataset_name, output_name='Correlation analysis info extraction (Strongly correlated)', flag=0)
        correlation_info_list = extract_correlation_info(file_name=dataset_name, output_name='Correlation analysis info extraction (Not strongly correlated)', flag=1)
    print('End.')
