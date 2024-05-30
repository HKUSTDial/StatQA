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


# [ATTENTION]: The config file is confidential and can NOT be uploaded or backed up!
# read config to get authorization
config_file = open('gpt_config.txt', 'r')
config_content = config_file.readlines()
config_file.close()
config_list = [line.strip() for line in config_content] # [url, authorization]


# Set prompt template
SYSTEM_PROMPT = "I'm a native English-speaking statistician. I will help you refine and improve expressions of statistical sentences without changing the original meaning. Please tell me the sentence you want to refine."
INSTRUCTION_PROMPT = '''Suppose you're a native English-speaking statistician, and I will give you a sentence about a statistical problem. You need to improve the English expression of the given sentence to make it grammatically and semantically correct, statistically rigorous and more coherent in expression. The given sentence will contain the names of the variables to be analyzed, and you are encouraged to based on the description, change them to more natural expressions without affecting the meaning. You can be flexible in how you improve the expression, but you must not change the original meaning of the sentence.'''


'''
refine preliminary question by calling GPT api (HKUSTGZ api)
Input: question sentence (str)
Output: GPT refiend question sentence (str)
'''
def refine_question_gpt(question: str, user_prompt) -> str:
    # url and authorization information is stored in config.txt
    url = config_list[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": config_list[1]
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt.format(question)}
        ],
        "temperature": 0.7
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
Simulate question refine, for testing purpose
'''
def mock_refine_question_gpt(question: str, user_prompt) -> str:
    import uuid
    return f"{question} (refined:{str(uuid.uuid4())[:8]}. Mock refine, pls change to real function in practice)"


'''
Update refined question in csv
Read the content of the "question" column in the csv and refine with GPT
csv_batch_size: Once # of csv_batch_size refined questions are obtained, update the csv once. Default value is 20.
'''
def update_refined_question_in_csv(file_name: str, csv_batch_size: int = 20):
    try:
        file_path = path.integ_dataset_path + path.balance_path +  file_name + '.csv'
        output_path = path.integ_dataset_path + path.balance_path + 'Refined ' + file_name + '.csv'
        df = pd.read_csv(file_path)
        try:
            output_df = pd.read_csv(output_path)
            if output_df.shape[0] > 0:
                # Find the index of the last line in the output file, to start processing from the next line
                start_index = output_df.shape[0]
            else:
                # exist but empty, start from 0
                start_index = 0
        except FileNotFoundError:
            # not exist, start from 0
            start_index = 0
        # read dataset csv
        df = pd.read_csv(file_path)
        if 'refined_question' not in df.columns:
            df['refined_question'] = ''
        # Make sure the last chunk of data can be processed correctly
        total_rows = len(df)
        chunks = math.ceil((total_rows - start_index) / csv_batch_size)

        # Iterate over the chunks
        for chunk in range(chunks):
            current_start_index = start_index + chunk * csv_batch_size
            current_end_index = min(current_start_index + csv_batch_size, total_rows)
            for i in range(current_start_index, current_end_index):
                # Extract description of columns involved
                metadata_df = utils.get_metadata(df.loc[i, 'dataset'])
                relevant_col_list = df['relevant_column'].iloc[i]
                relevant_col_info = utils.get_relevant_columns_info(metadata_df, relevant_col_list)
                num_relevent_col = len(relevant_col_info)
                description_str_list = []
                for j in range(num_relevent_col):
                    description = relevant_col_info['column_description'].iloc[j]
                    col_header = relevant_col_info['column_header'].iloc[j]
                    description_str_list.append(f"{col_header}: {description}")
                # Reorganize column description and reorganize prompt
                col_description = '; '.join(description_str_list)
                organized_user_prompt = INSTRUCTION_PROMPT + f'''\nVariable description: {col_description}.''' + '''\nSentence: {}'''
                df.loc[i, 'refined_question'] = refine_question_gpt(
                    question=df['origin_question'].iloc[i], 
                    user_prompt=organized_user_prompt)
                print(f"[+] Current row: {i + 1} / {len(df)}")

            # Write chunk to the output csv
            if chunk == 0 and start_index == 0:
                # For the first chunk, headers needed to be written.
                df[current_start_index:current_end_index].to_csv(output_path, mode='w', index=False, header=True)
            else:
                df[current_start_index:current_end_index].to_csv(output_path, mode='a', index=False, header=False)
            print(f"[+] Chunk of row {current_start_index + 1}~{current_end_index} successfully written to csv.")
            print("-------------------------------------------------")
    except Exception as e:
        print(f"[!] Error: {e}")
    

'''
Execute this function for the case of an error and is used to re-call GPT and fill in the answer
'''
def retry_refine_for_errors(dataset_name: str):
    # Try reloading a DataFrame that already contains "Error".
    dataset_path = path.integ_dataset_path + path.balance_path + dataset_name + '.csv'
    df = pd.read_csv(dataset_path)
    # Find all the lines marked as "Error".
    error_indices = df.index[df['refined_question'] == "Error"].tolist()
    # If you don't find Error, return it directly
    if not error_indices:
        print("[!] No 'Error' entries found to retry.")
        return
    print(f"[i] Retrying: There are {len(error_indices)} entries in total marked as 'Error'.")
    
    # Go through all the wrong rows and call the API again
    for index in error_indices:
        origin_question = df.at[index, 'origin_question']
        metadata_df = utils.get_metadata(df.loc[index, 'dataset'])
        relevant_col_list = df['relevant_column'].iloc[index]
        relevant_col_info = utils.get_relevant_columns_info(metadata_df, relevant_col_list)
        num_relevent_col = len(relevant_col_info)
        description_str_list = []
        for j in range(num_relevent_col):
            description = relevant_col_info['column_description'].iloc[j]
            col_header = relevant_col_info['column_header'].iloc[j]
            description_str_list.append(f"{col_header}: {description}")
        # Reorganize column description and reorganize prompt
        col_description = '; '.join(description_str_list)
        organized_user_prompt = INSTRUCTION_PROMPT + f'''\nVariable description: {col_description}.''' + '''\nSentence: {}'''

        # Call function to refine, update, and save
        refined_question = refine_question_gpt(question=origin_question, user_prompt=organized_user_prompt)
        df.at[index, 'refined_question'] = refined_question
        # Save after every 5 attempts
        if (index + 1) % 5 == 0 or index == error_indices[-1]:
            df.to_csv(dataset_path, index=False)
            print(f'[+] Updated and saved, up to error index: {index}')
    print("[i] Retry process completed.")


# main
if __name__=='__main__':
    # start_time = time.time()  # Start the timer
    # dataset_name = 'shuffled_Integrated Dataset'
    # update_refined_question_in_csv(file_name=dataset_name, csv_batch_size=10)
    # end_time = time.time()  # End the timer
    
    # # Calculate the time consumption in execution of question refining
    # elapsed_time = end_time - start_time
    # minutes = int(elapsed_time // 60)
    # seconds = int(elapsed_time % 60)
    # print(f"[i] Total execution time: {minutes} min {seconds} sec.")

    # # Call the retry function (if needed)
    # retry_refine_for_errors(dataset_name=dataset_name + ' Benchmark')

    print('[Attention] Question sentence refinement will be conducted when balancing the benchmark!')
