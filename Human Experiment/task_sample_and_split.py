# -*- coding: gbk -*-
import pandas as pd
from sklearn.model_selection import train_test_split


def sample_testset_for_human(file_path, sample_prop=0.1):
    data = pd.read_csv(file_path)
    # Perform stratified sampling based on 'task' and 'difficulty'
    stratified_sample = data.groupby(['task', 'difficulty'], group_keys=False).apply(lambda x: x.sample(frac=sample_prop, random_state=64))
    # Save the stratified sample to a new CSV file
    sampled_file_path = 'data/Sampled Benchmark.csv'
    stratified_sample.to_csv(sampled_file_path, index=False)
    print('[+] Sampled dataset saved to', sampled_file_path)
    return sampled_file_path



def split_task_block(sampled_data_path, num_block=3):
    # Load the sampled dataset
    sampled_data = pd.read_csv(sampled_data_path)
    
    # Shuffle the rows of the dataframe to ensure random splitting, with a fixed random state for reproducibility
    sampled_data = sampled_data.sample(frac=1, random_state=64).reset_index(drop=True)
    
    # Calculate subset size
    subset_size = len(sampled_data) // num_block
    
    # Split into subsets and save
    subset_file_paths = []
    for i in range(num_block):
        start_idx = i * subset_size
        if i == num_block - 1:  # Handle last subset differently to include all remaining data
            subset = sampled_data.iloc[start_idx:]
        else:
            subset = sampled_data.iloc[start_idx:start_idx + subset_size]
        
        # Sort by the 'dataset' column within each subset
        subset = subset.sort_values(by='dataset')
        
        # Define file path for this subset
        subset_file_path = f'data/task_block_{i+1}.csv'
        subset.to_csv(subset_file_path, index=False)
        subset_file_paths.append(subset_file_path)
    
    print('[+] Task blocks splitted.')
    return subset_file_paths


if __name__ == '__main__':
    # Load the dataset
    file_path = 'data/Balanced Benchmark for Human.csv'
    sampled_file_path = sample_testset_for_human(file_path=file_path, sample_prop=0.1)
    # Call the function and print the file paths of the subsets
    subset_paths = split_task_block(sampled_data_path=sampled_file_path, num_block=3)
