# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

from vllm import LLM, SamplingParams
import pandas as pd
import time
import argparse 


model_ans_path = "Model Answer/"
prompt_dataset_path_test = "Data/Integrated Dataset/Dataset with Prompt/Test Set/"


'''
User LLaMA to generate answers
- tricks: tricks involved, which will be remarked in output file name.
'''
def llama_answer_generation(model_type: str, dataset_name: str, output_name: str, trick: str):
    model_load_start_time = time.time()
    
    # Path settings
    if model_type == '2_7b':
        model_path = "/your_path_to/Llama-2-7b-chat-hf"
        parallel_num = 4
    elif model_type == '2_13b':
        model_path = "/your_path_to/Llama-2-13b-chat-hf"
        parallel_num = 8
    elif model_type == '3_8b_instruct':
        model_path = "/your_path_to/Meta-Llama-3-8B-Instruct"
        parallel_num = 8
    elif model_type == '3_8b':
        model_path = "/your_path_to/Meta-Llama-3-8B"
        parallel_num = 8
    else:
        raise ValueError("[!] Invalid model type. Please choose from: 2_7b, 2_13b, 3_8b_instruct and 3_8b")
    
    # max token limit settings
    if trick == 'zero-shot-CoT' or trick == 'one-shot-CoT':
        max_tokens_limit = 1024
    else:
        max_tokens_limit = 256

    answer_store_path = "Origin Answer/"
    prompt_dataset_path = prompt_dataset_path_test
    file_path = prompt_dataset_path + dataset_name + ' for ' + trick + '.csv'
    output_path = model_ans_path + answer_store_path + output_name + model_type + '_' + trick + '.csv'
    answer_column_name = "model_answer"

    # Initialize model and sampling parameters
    llm = LLM(
        model=model_path,
        tensor_parallel_size=parallel_num  # Adjust according to GPU configuration
    )
    sampling_params = SamplingParams(
        temperature=0.0, 
        top_p=1.0, 
        max_tokens=max_tokens_limit
    )

    # Read dataset with prompt
    df = pd.read_csv(file_path)
    if answer_column_name not in df.columns:
        df[answer_column_name] = ''

    # Model loading end, generation start
    model_load_end_time = time.time()
    model_load_total_time = model_load_end_time - model_load_start_time
    generation_start_time = time.time()

    # Processing quantity per batch
    answer_batch_size = 10

    # Process prompts in batches and generate Llama's answers
    for i in range(0, len(df), answer_batch_size):
        batch_df = df.iloc[i:i+answer_batch_size]  # Get the DataFrame fragment of the current batch
        prompts = batch_df['prompt'].tolist()  # Get the issue list of the current batch
        # Filter out prompts that have not yet generated an answer
        prompts = [prompt for j, prompt in enumerate(prompts) if pd.isna(batch_df.iloc[j][answer_column_name]) or batch_df.iloc[j][answer_column_name] == '']
        # Skip if there are no problems that need to be processed in the current batch
        if not prompts:  
            continue
        # Generate answers for the current batch
        outputs = llm.generate(prompts, sampling_params)
        
        # Write the generated answer back into the DataFrame
        for j, output in enumerate(outputs):
            response = output.outputs[0].text
            df_index = i + j  # Calculate the index position in the original DataFrame
            df.at[df_index, answer_column_name] = response
            # print(f'[+] Added answer for row: {df_index}')

        # Update csv dataset
        df.to_csv(output_path, index=False)
        print(f"[+] (Current model: {model_type}, Prompting stategy: {trick}) Updated after processing batch starting from row {i}.")

    print(f"[i] csv file is fully updated with llama model-{model_type}-{trick} answers.")
    # Generation end
    generation_end_time = time.time()
    generation_total_time = generation_end_time - generation_start_time
    # Print information
    print("----------------------------------------------------------------------------------")
    print(f"[i] Model loading time comsumption: {model_load_total_time} seconds.")
    print(f"[i] Generation time comsumption: {generation_total_time} seconds.")
    print("----------------------------------------------------------------------------------")


# main
if __name__ == "__main__": 
    # Set the command line parameter parser
    parser = argparse.ArgumentParser(description='Generate answers using LLaMA.')
    parser.add_argument('--model_type', type=str, default='2_7b', help="LLaMA-2/3 model type. Please choose from: '2_7b', '2_13b', '3_8b_instruct' and '3_8b'.")
    parser.add_argument('--dataset_name', type=str, default='mini-StatQA', help='The name of the dataset file without extension')
    parser.add_argument('--output_name', type=str, default="llama", help='The base name for the output file')
    parser.add_argument('--trick', type=str, default='zero-shot', help="Prompting Strategy. Please choose from: 'zero-shot', 'one-shot', 'zero-shot-CoT', 'one-shot-CoT' and 'stats-prompt' (introducing domain knowledge).")
    
    # Parse command arguments
    args = parser.parse_args()
    
    # Call the function and pass in command arguments
    llama_answer_generation(
        model_type=args.model_type,
        dataset_name=args.dataset_name,
        output_name=args.output_name,
        trick=args.trick
    )