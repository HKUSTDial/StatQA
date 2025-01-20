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
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# [ATTENTION]: The config file is confidential and can NOT be uploaded or backed up!
# read config to get authorization
config_file = open('gpt_config.txt', 'r')
config_content = config_file.readlines()
config_file.close()
config_list = [line.strip() for line in config_content] # [url, authorization]

'''
Call GPT to generate answer
'''
def gpt_answer(prompt, row_index):
    max_try = 8
    url = config_list[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": 'Bearer ' + config_list[1]
    }
    data = {
        "model": selected_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    
    for attempt in range(max_try):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                return row_index, response.json()['choices'][0]['message']['content']
            else:
                print(f"[!] Error with status code {response.status_code} at attempt {attempt+1} for row {row_index}")
        except Exception as e:
            print(f"[!] Exception occurred: {e} at attempt {attempt+1} for row {row_index}")
        if attempt < max_try - 1:
            print(f"[ ] Waiting 10 seconds before retrying row {row_index}...")
            time.sleep(10)
    return row_index, "Error"

def process_batch(batch_df, thread_count=5):
    """Process a batch of prompts using multiple threads"""
    results = {}
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(gpt_answer, row['prompt'], index): index 
            for index, row in batch_df.iterrows()
        }
        
        # Process completed tasks with progress bar
        for future in tqdm(as_completed(future_to_index), total=len(future_to_index)):
            row_index, answer = future.result()
            results[row_index] = answer
    
    # Sort results by index and return
    return [results[idx] for idx in sorted(results.keys())]

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate answers using a selected model and trick.')
    parser.add_argument('--selected_model', default='gpt-3.5-turbo', type=str, required=True, help='The model to use for generation.')
    parser.add_argument('--trick', type=str, default='zero-shot', required=True, help='The trick to apply for generation.')
    parser.add_argument('--suffix', type=str, default='', help='Suffix for the dataset and output files.')
    parser.add_argument('--batch_size', type=int, default=10, help='Number of prompts to process in each batch')
    parser.add_argument('--threads', type=int, default=5, help='Number of concurrent threads')
    
    args = parser.parse_args()
    selected_model = args.selected_model
    trick = args.trick
    dataset_name = 'mini-StatQA for ' + trick
    suffix = args.suffix

    # Path setting
    input_csv_path = 'Data/Integrated Dataset/Dataset with Prompt/Test Set/' + dataset_name + f'{suffix}.csv'
    output_csv_path = f'Model Answer/Origin Answer/{selected_model}_{trick}{suffix}.csv'
    
    # Load existing progress
    if os.path.exists(output_csv_path):
        df_existing = pd.read_csv(output_csv_path)
        last_processed_row = len(df_existing)
    else:
        df_existing = pd.DataFrame()
        last_processed_row = 0

    df = pd.read_csv(input_csv_path)
    start_row = max(last_processed_row, 0)
    print(f"Starting from row: {start_row}")
    
    start_time = time.time()
    
    # Process data in batches
    batch_size = args.batch_size
    for batch_start in range(start_row, len(df), batch_size):
        batch_end = min(batch_start + batch_size, len(df))
        batch_df = df.iloc[batch_start:batch_end]
        
        # Process batch with multiple threads
        batch_answers = process_batch(batch_df, args.threads)
        
        # Update DataFrame and save progress
        df.loc[df.index[batch_start:batch_end], 'model_answer'] = batch_answers
        df_existing = pd.concat([df_existing, df.iloc[batch_start:batch_end]])
        df_existing.to_csv(output_csv_path, index=False)
        
        print(f'[+] Model: {selected_model}. Processed and saved batch: {batch_start} to {batch_end-1}')
        
        # Add a small delay between batches to avoid rate limiting
        time.sleep(1)

    end_time = time.time()
    time_consumption = end_time - start_time
    print('------------------------------------------------')
    print(f"Finished, output path: {output_csv_path}")
    print(f"Time consumption: {time_consumption} seconds")
    print('------------------------------------------------')
    # python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot-aprompt-4o-mini" --batch_size 6 --threads 3