# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import numpy as np
import utils
import glob
import json
import path
from mappings import *


work_dir = path.info_dir + path.prequestion_dir
question_file_suffix = '_withPreliminaryQuestions'


# Integrate datasets: process a single dataset
def process_single_dataset(file_path, task):
    df = pd.read_csv(file_path)
    processed_data = []

    for _, row in df.iterrows():
        # Get dataset name from the 'Dataset Name' column
        dataset_name = row['Dataset Name']
        # Read column metadata
        col_metadata_file = f"{path.meta_dir + path.col_meta_dir}{dataset_name}_col_meta.csv"
        col_meta_df = pd.read_csv(col_metadata_file)

        '''
        Extract column information and corresponding column metadata
        '''
        # Handle different column situations
        
        # There are two columns involved: Column 1, Column 2
        if 'Column 1' in df.columns and 'Column 2' in df.columns:
            # Common case: there is no strata collumn, and no control column
            if ('Strata Column' not in df.columns) and ('Control Column' not in df.columns):
                # There are 2 columns involved in analysis
                selected_row1 = col_meta_df[col_meta_df['column_header'] == row['Column 1']]
                selected_row2 = col_meta_df[col_meta_df['column_header'] == row['Column 2']]
                # deal with possible empty value
                if not selected_row1.empty:
                    type1 = selected_row1['data_type'].iloc[0]
                    des1 = selected_row1['column_description'].iloc[0] if not pd.isna(selected_row1['column_description'].iloc[0]) else ""
                else:
                    type1 = 'Unknown'
                    des1 = ''
                if not selected_row2.empty:
                    type2 = selected_row2['data_type'].iloc[0]
                    des2 = selected_row2['column_description'].iloc[0] if not pd.isna(selected_row2['column_description'].iloc[0]) else ""
                else:
                    type2 = 'Unknown'
                    des2 = ''
                # Number of rows, and normality information
                num_of_rows_1 = selected_row1['num_of_rows'].iloc[0]
                is_normality_1 = selected_row1['is_normality'].iloc[0]
                num_of_rows_2 = selected_row2['num_of_rows'].iloc[0]
                is_normality_2 = selected_row2['is_normality'].iloc[0]
                # print(type(int(num_of_rows_1)), type(bool(is_normality_1)))
                # print('!!!!!!!'+file_path + "||" +selected_row2['dataset'].iloc[0]+'!!!!!!!')
                column_data = json.dumps([{'column_header': row['Column 1'], 
                                        # 'data_type': type1,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des1,
                                        # 'num_of_rows': int(num_of_rows_1),
                                        # 'is_normality': bool(is_normality_1)
                                        },
                                        {'column_header': row['Column 2'],
                                        # 'data_type': type2,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des2,
                                        # 'num_of_rows': int(num_of_rows_2),
                                        # 'is_normality': bool(is_normality_2)
                                        }])
            # End for common case: there is no strata collumn, and no control column
            # For Mentel-Haenszel test: include strata column
            elif ('Strata Column' in df.columns) and ('Control Column' not in df.columns):
                selected_row_s1 = col_meta_df[col_meta_df['column_header'] == row['Column 1']]
                selected_row_s2 = col_meta_df[col_meta_df['column_header'] == row['Column 2']]
                selected_row_ss = col_meta_df[col_meta_df['column_header'] == row['Strata Column']] # strata column
                # deal with possible empty value
                if not selected_row_s1.empty:
                    type_s1 = selected_row_s1['data_type'].iloc[0]
                    des_s1 = selected_row_s1['column_description'].iloc[0] if not pd.isna(selected_row_s1['column_description'].iloc[0]) else ""
                else:
                    type_s1 = 'Unknown'
                    des_s1 = ''
                if not selected_row_s2.empty:
                    type_s2 = selected_row_s2['data_type'].iloc[0]
                    des_s2 = selected_row_s2['column_description'].iloc[0] if not pd.isna(selected_row_s2['column_description'].iloc[0]) else ""
                else:
                    type_s2 = 'Unknown'
                    des_s2 = ''
                if not selected_row_ss.empty:
                    type_ss = selected_row_ss['data_type'].iloc[0]
                    des_ss = selected_row_ss['column_description'].iloc[0] if not pd.isna(selected_row_ss['column_description'].iloc[0]) else ""
                else:
                    type_ss = 'Unknown'
                    des_ss = ''
                # Number of rows, and normality information
                num_of_rows_s1 = selected_row_s1['num_of_rows'].iloc[0]
                is_normality_s1 = selected_row_s1['is_normality'].iloc[0]
                num_of_rows_s2 = selected_row_s2['num_of_rows'].iloc[0]
                is_normality_s2 = selected_row_s2['is_normality'].iloc[0]
                num_of_rows_ss = selected_row_ss['num_of_rows'].iloc[0]
                is_normality_ss = selected_row_ss['is_normality'].iloc[0]
                column_data = json.dumps([{'column_header': row['Column 1'], 
                                        # 'data_type': type_s1,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des_s1,
                                        # 'num_of_rows': int(num_of_rows_s1),
                                        # 'is_normality': bool(is_normality_s1)
                                        },
                                        {'column_header': row['Column 2'],
                                        # 'data_type': type_s2,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des_s2,
                                        # 'num_of_rows': int(num_of_rows_s2),
                                        # 'is_normality': bool(is_normality_s2)
                                        },
                                        {'column_header': row['Strata Column'],
                                        # 'data_type': type_ss,
                                        'is_strata': True,
                                        'is_control': False,
                                        # 'description': des_ss,
                                        # 'num_of_rows': int(num_of_rows_ss),
                                        # 'is_normality': bool(is_normality_ss)
                                        }])
            # End of Mentel-Haenszel test case: include strata column
            # For Partial correlation coefficent: include control column
            elif ('Strata Column' not in df.columns) and ('Control Column' in df.columns):
                selected_row_c1 = col_meta_df[col_meta_df['column_header'] == row['Column 1']]
                selected_row_c2 = col_meta_df[col_meta_df['column_header'] == row['Column 2']]
                selected_row_cc = col_meta_df[col_meta_df['column_header'] == row['Control Column']] # control column
                # deal with possible empty value
                if not selected_row_c1.empty:
                    type_c1 = selected_row_c1['data_type'].iloc[0]
                    des_c1 = selected_row_c1['column_description'].iloc[0] if not pd.isna(selected_row_c1['column_description'].iloc[0]) else ""
                else:
                    type_c1 = 'Unknown'
                    des_c1 = ''
                if not selected_row_c2.empty:
                    type_c2 = selected_row_c2['data_type'].iloc[0]
                    des_c2 = selected_row_c2['column_description'].iloc[0] if not pd.isna(selected_row_c2['column_description'].iloc[0]) else ""
                else:
                    type_c2 = 'Unknown'
                    des_c2 = ''
                if not selected_row_cc.empty:
                    type_cc = selected_row_cc['data_type'].iloc[0]
                    des_cc = selected_row_cc['column_description'].iloc[0] if not pd.isna(selected_row_cc['column_description'].iloc[0]) else ""
                else:
                    type_cc = 'Unknown'
                    des_cc = ''
                # Number of rows, and normality information
                num_of_rows_c1 = selected_row_c1['num_of_rows'].iloc[0]
                is_normality_c1 = selected_row_c1['is_normality'].iloc[0]
                num_of_rows_c2 = selected_row_c2['num_of_rows'].iloc[0]
                is_normality_c2 = selected_row_c2['is_normality'].iloc[0]
                num_of_rows_cc = selected_row_cc['num_of_rows'].iloc[0]
                is_normality_cc = selected_row_cc['is_normality'].iloc[0]
                column_data = json.dumps([{'column_header': row['Column 1'], 
                                        # 'data_type': type_c1,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des_c1,
                                        # 'num_of_rows': int(num_of_rows_c1),
                                        # 'is_normality': bool(is_normality_c1)
                                        },
                                        {'column_header': row['Column 2'],
                                        # 'data_type': type_c2,
                                        'is_strata': False,
                                        'is_control': False,
                                        # 'description': des_c2,
                                        # 'num_of_rows': int(num_of_rows_c2),
                                        # 'is_normality': bool(is_normality_c2)
                                        },
                                        {'column_header': row['Control Column'],
                                        # 'data_type': type_cc,
                                        'is_strata': False,
                                        'is_control': True,
                                        # 'description': des_cc,
                                        # 'num_of_rows': int(num_of_rows_cc),
                                        # 'is_normality': bool(is_normality_cc)
                                        }])
            # End of partial correlation coefficent case: include control column
        # End of cases of multiple columns involved in analysis
        
        # Only one column involved: Column
        elif 'Column' in df.columns:
            selected_row0 = col_meta_df[col_meta_df['column_header'] == row['Column']]
            if not selected_row0.empty:
                type0 = selected_row0['data_type'].iloc[0]
                des0 = selected_row0['column_description'].iloc[0] if not pd.isna(selected_row0['column_description'].iloc[0]) else ""
            else:
                type0 = 'Unknown'
                des0 = ''
            # Number of rows, and normality information
            num_of_rows_0 = selected_row0['num_of_rows'].iloc[0]
            is_normality_0 = selected_row0['is_normality'].iloc[0]
            column_data = json.dumps([{'column_header': row['Column'], 
                                    #   'data_type': type0,
                                      'is_strata': False,
                                      'is_control': False,
                                    #   'description': des0,
                                    #   'num_of_rows': int(num_of_rows_0),
                                    #   'is_normality': bool(is_normality_0)
                                      }])
        else:
            # No Column information
            column_data = json.dumps({})

        '''
        Extract statistical methods and results
        '''
        methods_results = []
        if 'Method' in df.columns:
            # There is a 'Method' column: then use 'Method' column to pair with results. (Descriptive Statistics)
            for col in df.columns:
                if col not in ['Dataset Name', 'Column 1', 'Column 2', 'Column', 'Strata Column', 'Control Column', 'difficulty', 'question', 'refined question', 'Method']:
                    result_content = row[col]
                    result_dict = json.loads(result_content)
                    # Extract the value corresponding to the 'conclusion' key and remove
                    conclusion_value = result_dict.pop('conclusion', None)
                    # If the dictionary is empty, the result_value is conclusion_value;
                    # otherwise, the remaining dictionary is converted to a JSON string
                    result_value = json.dumps(result_dict) if result_dict else conclusion_value
                    methods_results.append({'method': row['Method'], 'result': result_value, 'conclusion': conclusion_value})
        elif 'Distribution' in df.columns and 'Column' in df.columns:
            # Special case: Column and Distribution present (other distribution compliance test, using KS test for uniform/exponential/gamma)
            distribution_method = "Kolmogorov-Smirnov Test" + f" for {row['Distribution']} distribution"
            for col in df.columns:
                if col not in ['Dataset Name', 'Column', 'Strata Column', 'Control Column', 'difficulty', 'question', 'refined question', 'Distribution']:
                    result_content = row[col]
                    result_dict = json.loads(result_content)
                    # Extract the value corresponding to the 'conclusion' key and remove
                    conclusion_value = result_dict.pop('conclusion', None)
                    # If the dictionary is empty, the result_value is conclusion_value;
                    # otherwise, the remaining dictionary is converted to a JSON string
                    result_value = json.dumps(result_dict) if result_dict else conclusion_value
                    methods_results.append({'method': distribution_method, 'result': result_value, 'conclusion': conclusion_value})
        else:
            # Standard processing for methods and results
            for col in df.columns:
                if col not in ['Dataset Name', 'Column 1', 'Column 2', 'Column', 'Strata Column', 'Control Column', 'difficulty', 'question', 'refined question']:
                    result_content = row[col]
                    result_dict = json.loads(result_content)
                    # Extract the value corresponding to the 'conclusion' key and remove
                    conclusion_value = result_dict.pop('conclusion', None)
                    # If the dictionary is empty, the result_value is conclusion_value;
                    # otherwise, the remaining dictionary is converted to a JSON string
                    result_value = json.dumps(result_dict) if result_dict else conclusion_value
                    methods_results.append({'method': col, 'result': result_value, 'conclusion': conclusion_value})
        results_data = json.dumps(methods_results)

        # integrate
        processed_data.append({
            'dataset': row['Dataset Name'],
            'relevant_column': column_data,
            # 'column': json.dumps(column_data),
            'task': task,
            'results': results_data,
            'origin_question': row['question'],
            # 'refine_question': row['refined question'],
            'difficulty': row['difficulty']
        })
    return processed_data


# main
if __name__ == '__main__':
    dataset_names = utils.get_dataset_name_list(work_dir)
    # integrate dataset
    all_data = []
    for dataset_name in dataset_names:
        file_path = os.path.join(work_dir, dataset_name + '.csv')
        task = dataset_task_mapping.get(dataset_name.replace(question_file_suffix, ''), 'Other Task')  # Get the task for the dataset, or use a 'Other Task'
        processed_data = process_single_dataset(file_path, task)
        all_data.extend(processed_data)

    final_df = pd.DataFrame(all_data)
    output_file_path = os.path.join(path.integ_dataset_path+path.balance_path, 'Benchmark.csv')
    final_df.to_csv(output_file_path, index=False)
    print("[+] Integrated dataset saved at: ", output_file_path)

    # minidev dataset for possible simple test
    # randomly select from integrated dataset to from a mini dataset for simple test
    mini_input_file = path.integ_dataset_path + path.balance_path + 'Benchmark.csv'  # Replace with your input file path
    n = 15  # The number of rows you want to keep (excluding the header row)
    mini_output_file = path.integ_dataset_path + path.balance_path + 'Benchmark minidev.csv'  # Replace with your output file path

    utils.random_select_mini_dataset(mini_input_file, n, mini_output_file)
    print('[+] Mini dev integrated dataset for test use saved at: ' + mini_output_file)

    # reorganize and shuffle dataset
    # utils.reorganize_shuffle_dataset(input_dir=path.integ_dataset_path, file_name='Integrated Dataset')
    # utils.reorganize_shuffle_dataset(input_dir=path.integ_dataset_path, file_name='Integrated Dataset mini')