# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import json
import pandas as pd
import utils
import time
import path


# Filter out "Not applicable" in results column
def filter_not_applicable(json_list_str):
        try:
            # Parse the JSON list string
            json_list = json.loads(json_list_str)
            if not isinstance(json_list, list):
                return None
            # Filter the list
            filtered_list = []
            for item in json_list:
                if isinstance(item, str):
                    item_json = json.loads(item)
                elif isinstance(item, dict):
                    item_json = item
                else:
                    continue
                if item_json.get('conclusion') != 'Not applicable':
                    filtered_list.append(item_json)    
            return json.dumps(filtered_list) if filtered_list else None
        except json.JSONDecodeError:
            return None


'''
Benchmark Postprocessing
1. Extract ground truth
2. Set difficulty
3. Filter out "Not applicable" in results column
'''
def benchmark_postprocessing(input_csv_path, output_csv_path):
    # Extract ground truth and read new df
    utils.extract_ground_truth(file_path=input_csv_path)
    # Read the CSV file
    df = pd.read_csv(input_csv_path)
    # Modify the 'difficulty' and rearrange the order of other columns
    df['difficulty'] = df['difficulty'].replace('medium', 'hard')
    
    # Check if 'results' column exists
    if 'results' not in df.columns:
        raise KeyError("The 'results' column is not present in the CSV file.")
    # Apply the filter function to the 'results' column
    df['results'] = df['results'].apply(filter_not_applicable)
    # Drop rows with None values in the 'results' column
    df = df.dropna(subset=['results'])
    columns = ['dataset', 'refined_question', 'relevant_column', 'results', 'ground_truth', 'task', 'difficulty']
    df = df[columns]
    df.to_csv(output_csv_path, index=False)
    print('[+] Processed csv dataset saved.')

    # Convert DataFrame to JSON format
    json_data = df.to_json(orient='records', lines=True, force_ascii=False)
    with open(output_csv_path.replace('.csv', '.json'), 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)
    print('[+] Processed json dataset saved.')
    print('[+] Benchmark postprocessing completed.')
    return


# main
if __name__ == "__main__":
    benchmark_postprocessing(input_csv_path=path.integ_dataset_path + path.balance_path + 'Balanced Benchmark.csv', 
                             output_csv_path=path.integ_dataset_path + path.balance_path + 'StatQA.csv')
    benchmark_postprocessing(input_csv_path=path.integ_dataset_path + path.balance_path + 'Balanced Benchmark test.csv', 
                             output_csv_path=path.integ_dataset_path + path.balance_path + 'mini-StatQA.csv')