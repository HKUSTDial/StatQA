# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import numpy as np
import pandas as pd
import re
import utils
import path


'''
If the data in the actual column contains characters, then this column needs to be processed. The specific processing required is as follows:
1. If it contains uppercase and lowercase letters M and K, it needs to be converted into the corresponding millions and hundreds of thousands;
2. If it contains a percent sign, it needs to be converted into a decimal;
3. If units such as kg and cm are included, remove the units.
'''
def convert_value(val):
    try:
        if isinstance(val, str):
            # Check and convert values ??containing M or K, but not units (such as kg)
            m_or_k = re.search(r'(\d+(\.\d+)?)([mMkK])$', val)
            if m_or_k:
                number, unit = float(m_or_k.group(1)), m_or_k.group(3).lower()
                if unit == 'm':
                    return number * 1000000
                elif unit == 'k':
                    return number * 1000
            # Convert percentage
            if '%' in val:
                return float(val.replace('%', '')) * 0.01
            # Remove non-numeric characters
            val = re.sub(r'[^\d\.]', '', val)
        return float(val)
    except ValueError:
        return val


'''
Preprocess dataset csv file
'''
def preprocess_csv(file_name: str):
    try:
        file_path = path.dataset_dir + file_name + '.csv'
        output_path = path.processed_dir + file_name + ".csv"
        # read csv
        df = pd.read_csv(file_path)

        for col in df.columns:
            data_type = utils.determine_data_type(df[col], file_name)
            # col metadata is quant but include non-numeric characters
            if data_type == 'quant' and (not utils.is_quantitative(df[col])):
                df[col] = df[col].apply(convert_value)

        # Output the processed file
        df.to_csv(output_path, index=False)
        return output_path
    except Exception as e:
        print(f"[!] Error processing file {file_name}: {e}")
        return None


'''
Add column metadata of num_of_rows and is_normality
'''
def add_column_rows_and_normality_metadata(file_name):
    meta_folder = path.meta_dir + path.col_meta_dir
    output_path = meta_folder + file_name + "_col_meta.csv"

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        col_meta_df = pd.read_csv(output_path)
        # Check if the required column exists and add it if not
        add_flag = 0
        if 'num_of_rows' not in col_meta_df.columns:
            col_meta_df['num_of_rows'] = np.nan
            add_flag = 1
        if 'is_normality' not in col_meta_df.columns:
            col_meta_df['is_normality'] = np.nan
            add_flag = 1
        file_path = path.processed_dir + file_name + '.csv'
        df = pd.read_csv(file_path)

        for index, row in col_meta_df.iterrows():
            column_name = row['column_header']
            # Count for num of rows
            col_meta_df.at[index, 'num_of_rows'] = int(len(df[column_name]))
            # Check normality, only for quantitative data types; false for non-quant data column
            if row['data_type'] == 'quant' and not pd.isnull(df[column_name]).all():
                col_meta_df.at[index, 'is_normality'] = utils.is_normality_ad(df[column_name])
            else:
                col_meta_df.at[index, 'is_normality'] = False
        # Before saving the updated metadata table, make sure the num_of_rows column is of type integer
        col_meta_df['num_of_rows'] = col_meta_df['num_of_rows'].astype(int)
        # Save updated metadata table
        col_meta_df.to_csv(output_path, index=False)
        if add_flag == 1:
            print(f'[+] Add column metadata of num_of_rows and is_normality for dataset {file_name}')
        else:
            print(f'[ ] Exist, no need to add num_of_rows and is_normality for dataset {file_name}')
    else:
        print(f"[!] Column metadata file for {file_name} does not exist or is empty")



# main
if __name__=='__main__':
    try:
        # Get all dataset names
        dataset_names = utils.get_dataset_name_list(path.dataset_dir)
        # Extract correlation info for all the datasets
        for dataset_name in dataset_names:
            processed_file = preprocess_csv(dataset_name)
            if processed_file:
                print(f"[+] Processed file saved: {dataset_name}")
            else:
                print(f"[!] Processing failed for file: {dataset_name}")
            # Add information of rows number and normality to metadata csv files
            add_column_rows_and_normality_metadata(dataset_name)
    except Exception as e:
        print(f"[!] Error in main process: {e}")
