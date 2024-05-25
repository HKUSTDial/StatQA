# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
import utils
import json
import path


"""
Format float value to 5 decimal places if it's a float, otherwise return the original value.
"""
def format_float(value):
    return round(value, 5) if isinstance(value, float) else value


'''
Function to calculate a given statistic, with error handling
'''
def calculate_statistic(func, col_data, default=np.nan):
    try:
        result = func(col_data)
        return format_float(result)
    except Exception:
        return default


'''
Function to extract descriptive statistics information
'''
def extract_descriptive_stats_info(file_name: str, output_name: str):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)

        stats_info_list = []

        # Iterate over each column of the dataframe
        for col in df.columns:
            is_quantitative_col = (utils.determine_data_type(series=df[col], dataset_name=file_name) == 'quant')
            # Categorical data to be calculated as mode
            is_categorical_col = (utils.determine_data_type(series=df[col], dataset_name=file_name) == 'cate')

            # Calculate statistics
            if is_quantitative_col or is_categorical_col:
                col_data = df[col].dropna() if is_quantitative_col else df[col]
                # Calculate statistics based on data type
                mean_con = str(calculate_statistic(np.mean, col_data)) if is_quantitative_col else 'Not applicable'
                median_con = str(calculate_statistic(np.median, col_data)) if is_quantitative_col else 'Not applicable'
                mode_con = str(calculate_statistic(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan, col_data)) if is_categorical_col else 'Not applicable'
                range_con = str(calculate_statistic(lambda x: x.max() - x.min(), col_data)) if is_quantitative_col else 'Not applicable'
                quartiles_con = json.dumps(calculate_statistic(lambda x: f"{{'Min': {x.quantile(0)}, 'Q1': {x.quantile(0.25)}, 'Median': {x.quantile(0.5)}, 'Q3': {x.quantile(0.75)}, 'Max': {x.quantile(1)}}}", col_data)) \
                    if is_quantitative_col else 'Not applicable'
                std_dev_con = str(calculate_statistic(np.std, col_data)) if is_quantitative_col else 'Not applicable'
                skewness_con = str(calculate_statistic(pd.Series.skew, col_data)) if is_quantitative_col else 'Not applicable'
                kurtosis_con = str(calculate_statistic(pd.Series.kurtosis, col_data)) if is_quantitative_col else 'Not applicable'

                # Append the statistics to the list
                stats_info_list.append((
                    file_name,
                    col,
                    json.dumps({'conclusion': mean_con}),
                    json.dumps({'conclusion': median_con}),
                    json.dumps({'conclusion': mode_con}),
                    json.dumps({'conclusion': range_con}),
                    json.dumps({'conclusion': quartiles_con}),
                    json.dumps({'conclusion': std_dev_con}),
                    json.dumps({'conclusion': skewness_con}),
                    json.dumps({'conclusion': kurtosis_con}),
                ))

        # Create a DataFrame from the list of statistics and save it to a CSV file
        # Only record it in the final output file if there is at least one applicable statistic method
        if stats_info_list:
            new_data = pd.DataFrame(stats_info_list, columns=[
                'Dataset Name', 'Column', 'Mean', 'Median', 'Mode', 'Range', 
                'Quartile', 'Standard Deviation', 'Skewness', 'Kurtosis'
            ])
            new_data = new_data.drop_duplicates()

            if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
                new_data.to_csv(output_path, mode='a', header=False, index=False)
            else:
                new_data.to_csv(output_path, mode='w', header=True, index=False)

            print(f"[+] Dataset: " + file_name + " Done!")
        else:
            print(f"[!] Dataset: " + file_name + " No applicable data found for descriptive statistics.")
        return stats_info_list
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")
        return None


# Main execution
if __name__=='__main__':
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    for dataset_name in dataset_names:
        stats_info_list = extract_descriptive_stats_info(file_name=dataset_name, output_name='Descriptive statistics info extraction')
    print('End.')
