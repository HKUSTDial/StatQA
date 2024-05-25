# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import argparse
import pandas as pd
import requests
import json
import time


# [ATTENTION]: The config file is confidential and can NOT be uploaded or backed up!
# read config to get authorization
config_file = open('gpt_config.txt', 'r')
config_content = config_file.readlines()
config_file.close()
config_list = [line.strip() for line in config_content] # [url, authorization]


'''
Call GPT to generate answer
'''
def gpt_answer(prompt):
    max_try = 8
    url = config_list[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": config_list[1]
    }
    data = {
        "model": selected_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    # Try 3 times in case of accident like internet fault.
    for attempt in range(max_try):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                # Request successful
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"[!] Error with status code {response.status_code} at attempt {attempt+1}")
        except Exception as e:
            print(f"[!] Exception occurred: {e} at attempt {attempt+1}")
        if attempt < max_try - 1:
            print("[ ] Waiting 10 seconds before retrying...")
            time.sleep(10)
    return "Error"  # If all 3 attempts fail, return "Error"


# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate answers using a selected model and trick.')
    parser.add_argument('--selected_model', default='gpt-3.5-turbo', type=str, required=True, help='The model to use for generation.')
    parser.add_argument('--trick', type=str, default='zero-shot', required=True, help='The trick to apply for generation.')
    parser.add_argument('--suffix', type=str, default='', help='Suffix for the dataset and output files.')
    
    args = parser.parse_args()
    
    selected_model = args.selected_model
    trick = args.trick
    dataset_name = 'Balanced Benchmark test for ' + trick
    suffix = args.suffix

    input_csv_path = 'Dataset/' + dataset_name + f'{suffix}.csv'
    output_csv_path = f'Model Answer/{selected_model}_{trick}{suffix}.csv'

    if os.path.exists(output_csv_path):
        df_existing = pd.read_csv(output_csv_path)
        last_processed_row = len(df_existing)
    else:
        df_existing = pd.DataFrame()
        last_processed_row = 0

    df = pd.read_csv(input_csv_path)

    start_row = max(last_processed_row, 0)
    print(f"Starting from row: {start_row}")

    answers = []
    start_time = time.time()

    for index, row in df.iterrows():
        if index < start_row:
            continue
        
        prompt = row['prompt']
        answer = gpt_answer(prompt)
        answers.append(answer)
        
        if (index + 1) % 5 == 0 or index == len(df) - 1:
            answer_slice = pd.Series(answers)
            slice_start = index + 1 - len(answers)
            slice_end = index + 1
            df.loc[df.index[slice_start:slice_end], 'model_answer'] = answer_slice.values
            df_existing = pd.concat([df_existing, df.loc[df.index[slice_start:slice_end]]])
            df_existing.to_csv(output_csv_path, index=False)
            answers = []
            print(f'[+] Model: {selected_model}. Processed and saved up to row: {index}')

    end_time = time.time()
    time_consumption = end_time - start_time
    print('------------------------------------------------')
    print(f"Finished, output path: {output_csv_path}")
    print(f"Time consumption: {time_consumption} seconds")
    print('------------------------------------------------')