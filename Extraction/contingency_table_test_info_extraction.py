# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
from scipy.stats import spearmanr, kendalltau
from pingouin import partial_corr
import glob
from scipy.stats import chi2_contingency, fisher_exact
import utils
import json
import path


'''
Extract chi-square independence test and fisher exact test p-value information into a csv file
If dataset is not applicable to a test, the p value will be set as 'null'
Any test with a p-value less than 0.05 will be summarized and recorded

Prerequisites for the chi-square independence test: 
    Column 1 and Column 2 are selected as categorical variables; 
    The number of cells with expected frequency less than 5 cannot exceed 20%;
    The existence of cells with expected frequency less than 1 can not be allowed.
Prerequisites for the fihser exact test:
    2x2 table
'''
def extract_chi_square_and_fisher_info(file_name: str, output_name: str, flag=0):
    try:
        file_path = path.processed_dir + file_name + '.csv'
        output_path = path.info_dir + output_name + ".csv"
        # read csv
        df = pd.read_csv(file_path)

        test_info_list = []

        # Only select categorical columns
        # categorical_columns = [col for col in df.columns if utils.is_categorical(df[col])]
        categorical_columns = [col for col in df.columns if utils.determine_data_type(series=df[col], dataset_name=file_name) == "cate"]


        # Make a double loop over categorical_columns
        for i in range(len(categorical_columns)):
            for j in range(i + 1, len(categorical_columns)):
                col1 = categorical_columns[i]
                col2 = categorical_columns[j]
                observed = pd.crosstab(df[col1], df[col2])

                # Record whether chi-square test requirements are met
                chi2_req_met = True
                # Check prerequisites of chi-square independence test
                row_totals = observed.sum(axis=1)
                col_totals = observed.sum(axis=0)
                total = observed.sum().sum()
                expected = np.outer(row_totals, col_totals) / total
                # Condition 1: no cell should have expected frequency < 1
                if np.any(expected < 1):
                    chi2_req_met = False
                # Condition 2: not more than 20% of cells should have expected frequency less than 5
                if np.sum(expected < 5) > 0.2 * expected.size:
                    chi2_req_met = False

                # Calculate chi-square p-value if requirements are met, else store 'null'
                chi2_p = 'null'
                if chi2_req_met:
                    chi2, chi2_p, dof, _ = chi2_contingency(observed) 

                # Fisher's exact test could be done on observed table if it is a 2x2 table
                fisher_p = 'null'
                if observed.shape == (2, 2):
                    _, fisher_p = fisher_exact(observed)

                if chi2_p != 'null': chi2_p = round(chi2_p, 5)
                if fisher_p != 'null': fisher_p = round(fisher_p, 5)

                # chi-square p < 0.05 or fisher p < 0.05: Reject the null hypothesis, and consider selected variables are NOT independent
                # p >= 0.05 for considering selected variables independent
                not_indepen = ((chi2_p != 'null' and chi2_p < 0.05) or (fisher_p != 'null' and fisher_p < 0.05))
                indepen = ((chi2_p != 'null' and chi2_p >= 0.05) and (fisher_p != 'null' and fisher_p >= 0.05))
                if flag == 0:
                    indepen_con = not_indepen
                elif flag == 1:
                    indepen_con = indepen

                if chi2_p == 'null': 
                    chi2_conclusion = 'Not applicable'
                else:
                    chi2_conclusion = 'Not independent' if (chi2_p != 'null' and chi2_p < 0.05) else 'Independent'
                if fisher_p == 'null':
                    fihser_conclusion = 'Not applicable'
                else:
                    fihser_conclusion = 'Not independent' if (fisher_p != 'null' and fisher_p < 0.05) else 'Independent'
                
                chi2_results = {'p value': chi2_p, 'conclusion': chi2_conclusion}
                fisher_results = {'p value': fisher_p, 'conclusion': fihser_conclusion}
                if indepen_con:
                    test_info_list.append((
                        file_name,
                        col1,
                        col2,
                        json.dumps(chi2_results),
                        json.dumps(fisher_results)
                    ))

        # Append list of tuples to CSV file and remove duplicates
        new_data = pd.DataFrame(test_info_list, columns=[
                                'Dataset Name', 'Column 1', 'Column 2', 'Chi-square Independence Test', 'Fisher Exact Test'])
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
        test_info_list = extract_chi_square_and_fisher_info(file_name=dataset_name, output_name='Chi-square and fisher exact test info extraction (Not independent)', flag=0)
        test_info_list = extract_chi_square_and_fisher_info(file_name=dataset_name, output_name='Chi-square and fisher exact test info extraction (Independent)', flag=1)
    print('End.')

