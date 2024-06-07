# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import requests
import json
import pandas as pd
import math
import utils
import time
import path
from gpt_refine_question import update_refined_question_in_csv, retry_refine_for_errors


# [ATTENTION]: The config file is confidential and can NOT be uploaded or backed up!
# read config to get authorization
config_file = open('gpt_config.txt', 'r')
config_content = config_file.readlines()
config_file.close()
config_list = [line.strip() for line in config_content] # [url, authorization]


# Set prompt template
SYSTEM_PROMPT = "I'm here to help you rewrite and paraphrase sentences, but not change their original meaning."
USER_PROMPT = "Please rewrite and paraphrase the given sentence using flexible expressions; you can use synonyms, change the grammatical structure, or change the tense and voice of the sentence, but you must keep the meaning exactly the same as the original. Sentence to be rewritten: {}"


'''
Adjust and revise the difficulty level in the benchmark
Facilitate following procedures of sampling and expansion to make benchmark more balanced.
'''
def adjust_difficulty_for_benchmark(file_path, output_path):
    df = pd.read_csv(file_path)
    # Check if the 'difficulty' column exists; if not, create and initialize it as None
    if 'difficulty' not in df.columns:
        df['difficulty'] = None
    # Adjust and revise
    for index, row in df.iterrows():
        try:
            # Parse json
            results_list = json.loads(row['results'].replace("'", "\""))
            # Iterate over each result in the results list
            difficulty = 'easy'  # default as easy
            for result in results_list:
                # Checks for the presence of items whose inclusion is Not Applicable
                if 'conclusion' in result and result['conclusion'] == 'Not applicable':
                    difficulty = 'hard'
                    break  # Find one and stop checking and set it to Hard difficulty
        except Exception as e:
            # If an exception occurs during processing, set the difficulty to easy 
            # (this is usually the case when Quartile is encountered).
            difficulty = 'easy'
        df.at[index, 'difficulty'] = difficulty
    df.to_csv(output_path, index=False)
    print('[i] Finished benchmark difficulty adjustment.')
    return output_path


'''
Use GPT to paraphrase and rewrite questions' sentences
'''
def paraphrase_question_gpt(question: str, model_type: str="gpt-3.5-turbo", temperature: float=0.7) -> str:
    # url and authorization information is stored in config.txt
    url = config_list[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": config_list[1]
    }
    data = {
        "model": model_type,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(question)}
        ],
        "temperature": temperature
    }
    # 3 attempt in case of internet failure
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                # response.raise_for_status()  # Trigger HTTPError if status code is not 200
                result = response.json() 
                refined = result['choices'][0]['message']['content']
                # Remove excessive whitespace characters and returned prompts structures
                refined = refined.replace('\n', '').replace('The revised sentence is: ', '')
                return refined
            else:
                print(f"[!] Error: {response.status_code} at attempt {attempt+1}.")
        except Exception as e:
            print(f"[!] Error: {e}")
        if attempt < 2:
            time.sleep(10)  # Wait for 10 second before the next attempt
    return 'Error' # Return 'Error' if all attempts fail


'''
Simulates the paraphrasing of a sentence by appending a unique identifier.
This is a mock function used in test to simulate the behavior of actual calling.
'''
def mock_paraphrase_question_gpt(question: str, model_type: str, temperature:int) -> str:
    import uuid
    return f"{question} (refined: {model_type}-{str(temperature)}-{str(uuid.uuid4())[:8]})"


"""
Samples the dataset based on the task type and difficulty.

Parameters:
- file_path: Path to the input dataset.
- output_path: Path where the sampled dataset will be saved.
- sample_ratio_mapping: A dictionary mapping tasks to their sample ratios for [easy, hard] difficulties.
"""
def sample_dataset(file_path, output_path, sample_ratio_mapping):
    # Load the dataset
    data = pd.read_csv(file_path)
    # Initialize an empty DataFrame to store sampled data
    sampled_data = pd.DataFrame()
    for task, ratios in sample_ratio_mapping.items():
        for difficulty, ratio in zip(['easy', 'hard'], ratios):
            # Filter rows matching the current task and difficulty
            task_difficulty_data = data[(data['task'] == task) & (data['difficulty'] == difficulty)]
            
            if ratio <= 1:
                # Sample the rows according to the provided ratio
                sampled_rows = task_difficulty_data.sample(frac=ratio, replace=False, random_state=1)
            else:
                # Keep all rows if the ratio is greater than 1, for later expansion
                sampled_rows = task_difficulty_data
            # Append sampled rows to the DataFrame
            sampled_data = pd.concat([sampled_data, sampled_rows], ignore_index=True)
    # Save the sampled dataset
    sampled_data.to_csv(output_path, index=False)
    print("[+] Sampled dataset saved to", output_path)
    return output_path


"""
Expands the dataset by modifying the 'refined_question' column of rows based on the specified ratios.
This version includes all sampled rows and expands only those that need it, printing progress updates to the console.

Parameters:
- file_path: Path to the dataset to be expanded.
- output_path: Path where the expanded dataset will be saved.
- sample_ratio_mapping: A dictionary mapping tasks to their expansion ratios for [easy, hard] difficulties.
"""
def expand_dataset(file_path, output_path, sample_ratio_mapping):
    # Load the dataset to be expanded
    data = pd.read_csv(file_path)
    # Initialize an empty list to store expanded data rows
    expanded_data_rows = []
    total_rows = len(data)
    processed_rows = 0
    
    for task, ratios in sample_ratio_mapping.items():
        for difficulty, ratio in zip(['easy', 'hard'], ratios):
            # Filter rows for the current task and difficulty
            task_difficulty_data = data[(data['task'] == task) & (data['difficulty'] == difficulty)]
            
            for index, row in task_difficulty_data.iterrows():
                # Always include the original row in the expanded dataset
                expanded_data_rows.append(row)
                processed_rows += 1
                # Only generate additional rows if the ratio is greater than 1
                if ratio > 1:
                    for _ in range(int(ratio) - 1):  # Add n-1 modified rows
                        modified_row = row.copy()
                        modified_row['refined_question'] = paraphrase_question_gpt(
                            question=row['refined_question'],
                            model_type='gpt-4' if task == 'Correlation Analysis' else 'gpt-3.5-turbo',
                            temperature=0.9 if task == 'Correlation Analysis' else 0.7
                        )
                        expanded_data_rows.append(modified_row)
                
                # Print progress update
                if processed_rows % 10 == 0 or processed_rows == total_rows:
                    print(f"[+] Processed {processed_rows}/{total_rows} rows.")
    
    # Convert the list of rows back to a DataFrame and save it
    expanded_data = pd.concat([pd.DataFrame([row]) for row in expanded_data_rows], ignore_index=True)
    expanded_data.to_csv(output_path, index=False)
    print("Expansion complete. Dataset saved to:", output_path)



# main
if __name__ == '__main__':
    # Define the sample_ratio mapping as provided
    sample_ratio_mapping = {
        'Correlation Analysis': [0.2, 30],
        'Contingency Table Test': [0.25, 2],
        'Distribution Compliance Test': [0.25, 1],
        'Descriptive Statistics': [0.75, 0],
        'Variance Test': [2, 0.4]
    }

    # Adjust difficulty for sampling afterwards
    difficulty_adjusted_file_path = adjust_difficulty_for_benchmark(file_path=path.integ_dataset_path + path.balance_path + 'Benchmark.csv', 
                                                                    output_path=path.integ_dataset_path + path.balance_path + 'Benchmark.csv')
    
    # Execute the sampling
    sampled_file_path = sample_dataset(file_path=difficulty_adjusted_file_path, 
                                       output_path=path.integ_dataset_path + 'Balanced Benchmark/Sampled Balanced Benchmark.csv', 
                                       sample_ratio_mapping=sample_ratio_mapping)

    
    # GPT refine question sentences
    start_time = time.time()  # Start the timer
    dataset_name = 'Sampled Balanced Benchmark'
    update_refined_question_in_csv(file_name=dataset_name, csv_batch_size=10)
    end_time = time.time()  # End the timer
    # Calculate the time consumption in execution of question refining
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"[i] Total execution time: {minutes} min {seconds} sec.")
    # Call the retry function (if needed)
    retry_refine_for_errors(dataset_name='Refined ' + dataset_name)
    
    # Execute the expansion to balance benchmark
    expand_file_path = expand_dataset(file_path=path.integ_dataset_path + path.balance_path +  'Refined Sampled Balanced Benchmark.csv', 
                                      output_path=path.integ_dataset_path + path.balance_path +  'Balanced Benchmark.csv', 
                                      sample_ratio_mapping=sample_ratio_mapping)
    
    # Extract ground truth and reorganize if neccessay
    utils.extract_ground_truth(file_path=path.integ_dataset_path + 'Balanced Benchmark/Balanced Benchmark.csv')
    # utils.reorganize_shuffle_dataset(input_dir=path.integ_dataset_path+path.balance_path, file_name='Balanced Benchmark')

    # Split balanced benchmark if necessary
    # training set should not be splitted, test set can be splitted and use the sampled one for test
    utils.split_benchmark(dataset_name='Balanced Benchmark', test_ratio=0.1)
