# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
import utils
from statsmodels.stats.contingency_tables import StratifiedTable
import json
import path


'''
Judge if a column's data type us categorical and binary
'''
def is_binary(series: pd.Series) -> bool:
    return series.nunique() == 2


'''
Mantel-Haenszel Test: a method of contingency table test
Requirement: 2 columns to be analyzed and 1 strata column, all the 3 columns need to be categorical and binary
'''
def extract_mantel_haenszel_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)

        test_info_list = []

        # Select binary columns
        binary_columns = [col for col in df.columns if utils.determine_data_type(series=df[col], dataset_name=file_name) == "cate" and is_binary(df[col])]

        if len(binary_columns) < 3:
            print(f"[!] Dataset: {file_name} does not have enough binary columns for Mantel-Haenszel test")
            return None

        # Iterate over all combinations of three columns
        for i in range(len(binary_columns)):
            for j in range(i+1, len(binary_columns)):
                for k in range(j+1, len(binary_columns)):
                    strata_col = binary_columns[i]
                    col1 = binary_columns[j]
                    col2 = binary_columns[k]

                    # Create a list of 2x2 tables for each stratum
                    stratified_tables = []
                    for stratum, group in df.groupby(strata_col):
                        table = pd.crosstab(group[col1], group[col2])
                        if table.shape == (2, 2):
                            stratified_tables.append(table)

                    if not stratified_tables:
                        continue

                    # Perform Mantel-Haenszel test
                    mh_test = StratifiedTable(stratified_tables)
                    result = mh_test.test_null_odds()
                    p_value = result.pvalue

                    # p < 0.05: Exclude strata variable, col 1 amd col 2 NOT independent (col 1 and col 2 are related) 
                    # p >= 0.05: Exclude strata variable, col 1 amd col 2 independent (col 1 and col 2 are NOT related) 
                    not_indepen = (p_value < 0.05)
                    indepen = (p_value >= 0.05)
                    if flag == 0:
                        mh_con = not_indepen
                    elif flag == 1:
                        mh_con = indepen
                    
                    if result.pvalue == 'null':
                        mh_conclusion = 'Not applicable'
                    else:
                        mh_conclusion = "Not independent" if (p_value < 0.05) else "Independent"
                    if mh_con:
                        test_info_list.append((
                            file_name, 
                            col1, 
                            col2, 
                            strata_col,
                            json.dumps({'p value': round(p_value, 5), 'conclusion': mh_conclusion})
                        ))

        # Write results to CSV file
        new_data = pd.DataFrame(test_info_list, columns=['Dataset Name', 'Column 1', 'Column 2', 'Strata Column', 'Mantel-Haenszel Test'])
        new_data = new_data.drop_duplicates()

        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            new_data.to_csv(output_path, mode='a', header=False, index=False)
        else:
            new_data.to_csv(output_path, mode='w', header=True, index=False)
        print(f"[+] Dataset: {file_name} Done!")
        return test_info_list
    except Exception as e:
        print(f"[!] Dataset: {file_name} Error: {e}")
        return None


# main
if __name__=='__main__':
    # Get all dataset names
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    # Extract correlation info for all the datasets
    for dataset_name in dataset_names:
        extract_mantel_haenszel_info(file_name=dataset_name, output_name='Mantel Haenszel test info extraction (Not independent)', flag=0)
        extract_mantel_haenszel_info(file_name=dataset_name, output_name='Mantel Haenszel test info extraction (Independent)', flag=1)
    print('End.')
