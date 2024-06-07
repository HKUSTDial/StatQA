# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import random
import numpy as np
import question_templates as qt
import json
import path


''' 
Generate preliminary questions for decriptive statistical tasks
'''
def generate_questions_for_stats(file_name: str, templates_dict: dict, sample_num: int=1):
    try:
        # file_path = path.info_dir + path.manual_dir + file_name + '.csv'
        file_path = path.info_dir + file_name + '.csv'
        output_path = path.info_dir + path.prequestion_dir + file_name + '_withPreliminaryQuestions.csv'
        # read csv
        df = pd.read_csv(file_path) 
        # Prepare a list to store issues and their details
        questions_details = []

        for _, row in df.iterrows():
            dataset_name = row['Dataset Name']
            column_name = row['Column']
            # For each statistical feature, check if it is a JSON with 'conclusion' not equal to 'Not applicable'
            for stat_feature in templates_dict.keys():
                # Try parsing JSON, skip the line if it fails
                try:
                    result_json = json.loads(row[stat_feature])
                    if result_json.get('conclusion') != "Not applicable":
                        # Randomly choose templates and generate questions, then add to the list
                        chosen_templates = random.sample(templates_dict[stat_feature], k=sample_num)
                        for template in chosen_templates:
                            question = template.format(Column=column_name)
                            questions_details.append({
                                'Dataset Name': dataset_name,
                                'Column': column_name,
                                'Method': stat_feature,
                                'Results': row[stat_feature],
                                'question': question
                            })
                except json.JSONDecodeError:
                    # Handle JSON decode error (e.g., if the content is not valid JSON)
                    continue
                
        # Convert list of questions and their details to DataFrame and save to csv file
        questions_df = pd.DataFrame(questions_details)
        questions_df.to_csv(output_path, index=False)
        print('[+] ' + file_name + ' Questions generated successfully!')
    except FileNotFoundError:
        print(f"[!] Error: File not found at path {file_path}")
    except pd.errors.EmptyDataError:
        print(f"[!] Error: The file at path {file_path} is empty.")
    except pd.errors.ParserError:
        print(f"[!] Error: Unable to parse the CSV file at path {file_path}.")
    except ValueError as ve:
        print(f"[!] Error: {ve}")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
    return

# template dictionary
templates_dict = {
    'Mean': qt.Mean_templates,
    'Median': qt.Median_templates,
    'Mode': qt.Mode_templates,
    'Range': qt.Range_templates,
    'Quartile': qt.Quartile_templates,
    'Standard Deviation': qt.Standard_deviation_templates,
    'Skewness': qt.Skewness_templates,
    'Kurtosis': qt.Kurtosis_templates
}


# main
if __name__=='__main__':
    generate_questions_for_stats(sample_num=2, file_name='Descriptive statistics info extraction', templates_dict=templates_dict)
