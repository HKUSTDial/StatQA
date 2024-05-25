# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
import utils
import path


'''
Create metadata table for a dataset
If the file already exists, add it at the end and must not be overwritten.
'''
def create_dataset_preliminary_metadata_table(file_list, output_csv):
    output_path = path.meta_dir + output_csv + '.csv'
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        # Read existing metadata file
        existing_df = pd.read_csv(output_path)
        existing_datasets = set(existing_df['dataset'])
        # Filter out existing dataset names
        file_list = [name for name in file_list if name not in existing_datasets]
    # If there are new data sets that need to be added
    if file_list:  
        df = pd.DataFrame(columns=["dataset", "dataset_description", "url"])
        df["dataset"] = file_list
        append_mode = os.path.exists(output_path) and os.path.getsize(output_path) > 0
        header = not append_mode
        df.to_csv(output_path, mode='a', index=False, header=header)
        print('[+] Dataset preliminary metadata table updated with new data!')
    else:
        print('[!] No new datasets to add.')


'''
Create metadata tables for columns in a dataset
Skip if existing
'''
def create_column_preliminary_metadata_tables(file_name):
    meta_folder = path.meta_dir + path.col_meta_dir
    file_path = path.dataset_dir + file_name + '.csv'
    output_path = path.meta_dir + path.col_meta_dir + file_name + "_col_meta.csv"

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        # Read existing metadata file
        existing_df = pd.read_csv(output_path)
        if file_name in existing_df['dataset'].unique():
            print(f'[ ] Exist, skipping: Column metadata for dataset {file_name}')
            return
    try:
        df = pd.read_csv(file_path)
        column_headers = df.columns
        col_meta_df = pd.DataFrame(columns=["dataset", "column_header", "data_type", "column_description"])
        col_meta_df["column_header"] = column_headers
        col_meta_df["dataset"] = file_name
        # Determine the type of each column
        for col in column_headers:
            if utils.is_categorical(df[col]):
                col_meta_df.loc[col_meta_df["column_header"] == col, "data_type"] = "cate" # categorical
            elif utils.is_quantitative(df[col]):
                col_meta_df.loc[col_meta_df["column_header"] == col, "data_type"] = "quant" # quantitative
            else:
                col_meta_df.loc[col_meta_df["column_header"] == col, "data_type"] = "other" # other
        # save in new csv
        col_meta_df.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))
        print('[+] Column metadata table for dataset ' + file_name + ' created!')
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")



# main
if __name__ == "__main__":
    file_names = utils.get_dataset_name_list(path.dataset_dir)
    # create table for dataset metadata
    create_dataset_preliminary_metadata_table(file_names, "Dataset metadata")
    print('Dataset metadata framework table created.')
    # create tables for columns' metadata
    for item in file_names:
        create_column_preliminary_metadata_tables(item)

    # create_column_preliminary_metadata_tables('Crop Production Dataset')
    print('Column metadata framework tables created.')
    