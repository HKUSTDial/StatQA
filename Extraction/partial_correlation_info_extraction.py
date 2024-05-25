# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import pingouin as pg
import utils
import warnings
import json
import path


'''
Partial Correlation Coefficient
Three quantatitive columns involved.
'''
def extract_partial_correlation_info(file_name: str, output_name: str, flag = 0):
    try:
        file_path = path.processed_dir + file_name + ".csv"
        output_path = path.info_dir + output_name + ".csv"
        df = pd.read_csv(file_path)

        test_info_list = []

        quantitative_columns = [col for col in df.columns if utils.determine_data_type(series=df[col],dataset_name=file_name) == "quant"]

        if len(quantitative_columns) < 3:
            print(f"[!] Dataset: {file_name} does not have enough continuous columns for partial correlation analysis")
            return None

        # Iterate over all combinations of two columns with one control variable
        for i in range(len(quantitative_columns)):
            for j in range(i+1, len(quantitative_columns)):
                for k in range(len(quantitative_columns)):
                    if k == i or k == j:
                        continue
                    col1 = quantitative_columns[j]
                    col2 = quantitative_columns[k]
                    control_var = quantitative_columns[i]

                    # Attempt to calculate partial correlation with exception handling for RuntimeWarnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        try:
                            # Calculate partial correlation
                            result = pg.partial_corr(data=df, x=col1, y=col2, covar=control_var)
                            p_value = result['p-val'].values[0]
                            partial_corr_value = result['r'].values[0]

                            # Partial correlation coefficient abs > 0.5: strongly correlated;
                            # otherwise not strongly correlated
                            if flag == 0:
                                cor_condition = (abs(partial_corr_value) > 0.5)
                            elif flag == 1:
                                cor_condition = (abs(partial_corr_value) <= 0.5)
                            # Use a dict to store the results: coefficent and p value
                            # partial_conclusion = 'Strongly correlated' if (abs(partial_corr_value or 0) > 0.5 and (p_value <= 0.05)) else 'Not strongly correlated'
                            # if partial_corr_value != 'null': partial_corr_value = round(partial_corr_value, 5)
                            if p_value == 'null' or partial_corr_value == 'null':
                                partial_conclusion = 'Not applicable'
                            else:
                                p_value = round(p_value, 5)
                                partial_corr_value = round(partial_corr_value, 5)
                                partial_conclusion = 'Strongly correlated' if (abs(partial_corr_value or 0) > 0.5 and (p_value <= 0.05)) else 'Not strongly correlated'
                            partial_corr_results = {'coefficient': partial_corr_value, 'p value': p_value, 'conclusion': partial_conclusion}
                            if cor_condition:
                                test_info_list.append((
                                    file_name, 
                                    col1, 
                                    col2, 
                                    control_var, 
                                    json.dumps(partial_corr_results)
                                ))
                        except RuntimeWarning:
                            print(f"[!] RuntimeWarning encountered for {file_name} with variables {col1}, {col2}, and control {control_var}. Skipping this combination.")
                        except Exception as e:
                            print(f"[!] Unexpected error for {file_name} with variables {col1}, {col2}, and control {control_var}: {e}")


        # Write results to CSV file
        new_data = pd.DataFrame(test_info_list, columns=['Dataset Name', 'Column 1', 'Column 2', 'Control Column', 'Partial Correlation Coefficient'])
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
    # Assuming utils.get_dataset_name_list() works similarly to the provided code
    dataset_names = utils.get_dataset_name_list(path.processed_dir)
    # Extract partial correlation info for all the datasets
    for dataset_name in dataset_names:
        extract_partial_correlation_info(file_name=dataset_name, output_name='Partial correlation info extraction (Strongly correlated)', flag=0)
        extract_partial_correlation_info(file_name=dataset_name, output_name='Partial correlation info extraction (Not strongly correlated)', flag=1)
    print('End.')
    # Because the partial correlation subset is overly large compared with others
    # perform csv reduce to keep balance
    utils.thinen_csv_rows(n=2, file_name='Partial correlation info extraction (Strongly correlated)')
    utils.thinen_csv_rows(n=2, file_name='Partial correlation info extraction (Not strongly correlated)')
    print('Thinened.')
