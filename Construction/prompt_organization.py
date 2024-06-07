# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import argparse
import json
import utils
import path
import pandas as pd
from random import choice, sample
from prompt_wording import *


"""
**[This function is temporarily deprecated!]
Extracts the information of columns specified in the 'column' column of a given row.
"""
def extract_column_info(row_index) -> list:
    # Ensure the row_index is within the DataFrame's range
    if row_index >= len(df):
        return f"Row index {row_index} is out of bounds for the dataset with {len(df)} rows."
    
    # Extract the 'column' column content for the specified row
    column_content = df.at[row_index, 'relevant_column']
    # Parse the JSON content of the 'column' column
    columns_info = json.loads(column_content)
    # Initialize a list to hold the extracted information
    extracted_info = []
    # Extract the required information for each column mentioned
    for column in columns_info:
        info = {
            "column_header": column.get("column_header"),
            "description": column.get("description", "N/A"),  # Assuming 'description' might be missing
            "num_of_rows": column.get("num_of_rows", "N/A"),  # Assuming 'num_of_rows' might be missing
            "is_normality": column.get("is_normality", "N/A"),  # Assuming 'is_normality' might be missing
            "data_type": column.get("data_type", "N/A") # Assuming 'data_type' might be missing
        }
        extracted_info.append(info)
    return extracted_info


"""
**[This function is temporarily deprecated!]
Reads the dataset name from the 'dataset' column of a given row in the CSV file,
then reads the corresponding dataset file from the 'Processed Dataset/' directory, and
returns the first sveral lines of this dataset as a single string.
"""
def read_dataset_sampled_lines(row_index, sample_rows_num: int=5):
    # Read the CSV file
    # df = pd.read_csv(file_path)
    # Ensure the row_index is within the DataFrame's range
    if row_index >= len(df):
        return f"Row index {row_index} is out of bounds for the dataset with {len(df)} rows."
    # Extract the dataset name for the specified row
    dataset_name = df.at[row_index, 'dataset']
    # Construct the path to the dataset file
    dataset_file_path = f"Processed Dataset/{dataset_name}.csv"
    # Initialize a variable to hold the first sample_rows_num lines
    sampled_lines = ""
    try:
        # Open the dataset file with UTF-8 encoding and read the first several lines
        with open(dataset_file_path, 'r', encoding='utf-8') as file:
            # If there is no enough rows in dataset, just sample all
            dataset_len = len(pd.read_csv(dataset_file_path))
            sample_rows_num = min(dataset_len, sample_rows_num)
            for _ in range(sample_rows_num):
                line = file.readline()
                if not line:
                    break  # Stop if we've reached the end of the file
                sampled_lines += line
    except FileNotFoundError:
        return f"File {dataset_file_path} not found."
    return sampled_lines


"""
Extracts the 'refined_question' column information for a specified row in the CSV file.
"""
def extract_refined_question(row_index):
    # Ensure the row_index is within the DataFrame's range
    if row_index >= len(df):
        return f"Row index {row_index} is out of bounds for the dataset with {len(df)} rows."
    # Extract the 'refined_question' column content for the specified row
    refined_question_content = df.at[row_index, 'refined_question']
    return refined_question_content



'''
Organize prompt for row
trick: input should be in string format, refer to tricks for LLMs:
    1) 'zero-shot'; 2)'one-shot'; 3)'two-shot'; 4)'zero-shot-CoT'; 5)'one-shot-CoT'; 6) 'stats-prompt' (introducing domain knowledge).
'''
def prompt_organization(row_index, curr_dataset: str, trick: str)->str:
    FEW_SHOT_LIST = [CA_EG, CTT_EG, DCT_EG, VT_EG, DS_EG]
    COT_SHOT_LIST = [COT_CA_EG, COT_CTT_EG, COT_DCT_EG, COT_VT_EG, COT_DS_EG]
    # Statistical question
    refined_question = extract_refined_question(row_index=row_index)
    # Extract all column metadata for the current dataset
    curr_dataset_meta_df = utils.get_metadata(dataset_name=curr_dataset)
    meta_info_list = []
    # Replace some string
    for i in range(curr_dataset_meta_df.shape[0]):
        row = curr_dataset_meta_df.iloc[i]
        col_meta_str = ''
        for header in curr_dataset_meta_df.columns:
            # Value of key "dataset" and "column_description" will be not provided
            if (header != "dataset" and header != "column_description"):
                col_meta_str += f"{header}: {row[header]}; "
        # replace semicolon in the end of the row with period mark
        col_meta_str = col_meta_str[:-2] + '.'
        col_meta_str = col_meta_str.replace("cate", "categorical")
        col_meta_str = col_meta_str.replace("quant", "quantitative")
        # Merge the metadata into a list
        meta_info_list.append(col_meta_str)
    
    # Generate and organize prompt based on tricks
    if trick == 'zero-shot':
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + PROMPT_CLASSIFICATION \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_RESPONSE
    elif trick == 'one-shot':
        shot_example = choice(FEW_SHOT_LIST)
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + PROMPT_CLASSIFICATION \
                + "\n### Demonstration Example:\n<example start>\n" + shot_example + "\n</example end>" \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_RESPONSE
    elif trick == 'two-shot':
        shot_example_list = sample(FEW_SHOT_LIST, 2)
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + PROMPT_CLASSIFICATION \
                + "\n### Here are two demonstration examples:\n<example start>" \
                + "\n## Demonstration Example No.1:\n" + shot_example_list[0] \
                + "\n## Demonstration Example No.2:\n" + shot_example_list[1] + "\n</example end>" \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_RESPONSE
    elif trick == 'zero-shot-CoT':
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + PROMPT_CLASSIFICATION \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_COT + PROMPT_RESPONSE_EXPLAIN
    elif trick == 'one-shot-CoT':
        CoT_example = choice(COT_SHOT_LIST)
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + PROMPT_CLASSIFICATION \
                + "\n### Demonstration Example:\n<example start>\n" + CoT_example + "\n</example end>" \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_COT + PROMPT_RESPONSE_EXPLAIN
    elif trick == 'stats-prompt':
        shot_example = choice(FEW_SHOT_LIST)
        organized_prompt = "### Task Description: " + PROMPT_TASK_DESCRIPTION \
                + "\n### Instruction: "  + PROMPT_INSTRUCTION \
                + "\n### Classification List: \n" + STATS_PROMPT \
                + "\n### Demonstration Example:\n<example start>\n" + shot_example + "\n</example end>" \
                + "\n### Column Information: \n" + '\n'.join(meta_info_list) \
                + "\n### Statistical Question: " + refined_question \
                + "\n### Response: " + PROMPT_RESPONSE
    else:
        raise ValueError("[!] Invalid trick: " + trick)       
    return organized_prompt
    

# main
if __name__ == "__main__":
    # Attention: for training set which will be used in finetuning, the trick should be selected as zero-shot.
    parser = argparse.ArgumentParser(description='Process dataset to generate prompt based on a specified trick.')
    parser.add_argument('--trick_name', default='zero-shot', type=str, required=True,
                        help="The trick to be applied for prompt generation. Available tricks: 'zero-shot', 'one-shot', 'two-shot', 'zero-shot-CoT', 'one-shot-CoT'.")
    parser.add_argument('--integ_dataset_name', default='Benchmark test', type=str, required=True,
                        help='The name of the integrated dataset to be processed.')

    args = parser.parse_args()

    trick_name = args.trick_name
    integ_dataset_name = args.integ_dataset_name

    set_path = ''
    if integ_dataset_name.endswith('StatQA') or integ_dataset_name.endswith('test'):
        set_path = path.test_set_path
    elif integ_dataset_name.endswith('train'):
        set_path = path.training_set_path
    elif integ_dataset_name == 'Balanced Benchmark':
        set_path = ''
    else:
        raise ValueError('[!] Invalid dataset name! Please indicate a dataset ending with "train" or "test".')
    file_path = path.integ_dataset_path + path.balance_path + integ_dataset_name + '.csv'
    output_file_path = path.integ_dataset_path + path.prompt_dataset_path + set_path + integ_dataset_name + f' for {trick_name}.csv'
    # Organize prompt and add to csv
    try:
        df = pd.read_csv(file_path)
        # Add a new column for prompts, initialized with empty strings
        df['prompt'] = ''
        # Loop through each row in the DataFrame
        for row_index, row in df.iterrows():
            try:
                # Generate the prompt for the current row
                curr_dataset_name = df['dataset'].iloc[row_index]
                prompt = prompt_organization(row_index, curr_dataset=curr_dataset_name, trick=trick_name)
                # Directly assign the generated prompt to the 'prompt' column for the current row
                df.at[row_index, 'prompt'] = prompt
                # print(f"[+] Prompt generated for row {row_index}: {prompt}")
            except Exception as e:
                print(f"[!] An error occurred while organizing prompt for row {row_index}: {e}")
                # Optionally, assign a default value or error message to the 'prompt' column
                df.at[row_index, 'prompt'] = "Error!"
        
        # Remove some columns which is now useless after prompt generation, and rearrange the sequence of columns
        new_column_order = ['dataset', 'refined_question', 'relevant_column', 'task', 'difficulty','results', 'prompt']
        df = df[new_column_order]
        # Save the modified DataFrame to a new CSV file
        df.to_csv(output_file_path, index=False, encoding='utf-8')
        print(f"[+] Prompts for {trick_name} organized successfully. File saved at {output_file_path}")
    except Exception as e:
        print(f"[!] An error occurred during prompt organization: {e}")
