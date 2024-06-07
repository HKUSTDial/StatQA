# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
from scipy.stats import ks_2samp
import utils
import json
import path


'''
Use Kolmogorov-Smirnov test to compare the differences of distribution of two quant variables
'''
def extract_ks_test_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)  # Load the dataset

        ks_test_info_list = []
        columns = df.columns  # Get all column names

        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                # If NOT quant type of data, set 'null'
                data_type_i = utils.determine_data_type(series=df[columns[i]], dataset_name=file_name)
                data_type_j = utils.determine_data_type(series=df[columns[j]], dataset_name=file_name)
                if data_type_i != "quant" or data_type_j != "quant":
                    ks_test_info_list.append((file_name,columns[i],columns[j],'null'))
                    continue

                # Running the KS test
                result = ks_2samp(df[columns[i]], df[columns[j]])

                # If p-value < 0.05, reject the null hypothesis
                # Consider there is a significant difference in the distribution of the two selected variables
                # If p-value >= 0.05: Consider there is NOT a significant difference
                sig_diff = (result.pvalue < 0.05)
                not_sig_diff = (result.pvalue >= 0.05)
                if flag == 0:
                    sig_con = sig_diff
                elif flag == 1:
                    sig_con = not_sig_diff
                if result.pvalue == 'null':
                    sig_conclusion = 'Not applicable'
                else:
                    sig_conclusion = "Distribution significantly different" if (result.pvalue < 0.05) else "Distribution not significantly different"
                if sig_con:
                    # Append information to the list
                    ks_test_info_list.append((
                        file_name,
                        columns[i],
                        columns[j],
                        json.dumps({'p value': round(result.pvalue, 5), 'conclusion': sig_conclusion})
                    ))

        # Prepare DataFrame for storing the KS test info
        new_data = pd.DataFrame(ks_test_info_list, columns=[
                                'Dataset Name', 'Column 1', 'Column 2', 'Kolmogorov-Smirnov Test'])
        new_data = new_data.drop_duplicates()  # Remove potential duplicates
        new_data = new_data[new_data['Kolmogorov-Smirnov Test'] != 'null'] # Only keep the rows where P value is not 'null'

        # Check if output file exists and write the new data into it
        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
            # Append new info to existing file
            new_data.to_csv(output_path, mode='a', header=False, index=False)
        else:
            # Write to a new file if it doesn't exist
            new_data.to_csv(output_path, mode='w', header=True, index=False)
        print(f"[+] Dataset: " + file_name + " Done!")
        return ks_test_info_list  # Return the list of ks test info for further usage
    except Exception as e:
        print("[!] Dataset: " + file_name + f" Error: {e}")
        return None  # Return None to indicate that there was an error during the execution


# main
if __name__ == '__main__':
    # Get all dataset names
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    # Process each dataset and extract the KS test info
    for dataset_name in dataset_names:
        ks_test_info_list = extract_ks_test_info(file_name=dataset_name, output_name='KS distribution comparison info extraction (Distribution significantly different)', flag=0)
        ks_test_info_list = extract_ks_test_info(file_name=dataset_name, output_name='KS distribution comparison info extraction (Distribution not significantly different)', flag=1)
    print('End.')