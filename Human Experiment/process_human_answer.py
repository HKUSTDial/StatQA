import pandas as pd
import os
import json
import ast


"""
Merges multiple human answer csv files in a directory based on common prefixes and selected suffixes.
Paramters:
- work_dir: str, the directory containing the CSV files.
- prefix: str, the prefix of the files to merge.
- suffixes: list of int, the suffixes of the files to consider for merging.
"""
def merge_human_answer_by_prefix(work_dir, prefix, suffixes):
    # Initialize an empty DataFrame to hold the merged data
    merged_df = pd.DataFrame()
    for suffix in suffixes:
        # Construct the file name based on the current prefix and suffix
        file_name = f"{prefix}_{suffix}.csv"
        file_path = os.path.join(work_dir, file_name)
        if os.path.exists(file_path):
            # Read the CSV file and append it to the merged DataFrame
            df = pd.read_csv(file_path)
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        else:
            print(f"[!] The file {file_name} does not exist and will be skipped.")
    
    # Save the merged DataFrame to a new CSV file
    output_file_name = f"{prefix}_merged.csv"
    output_file_path = os.path.join(work_dir, output_file_name)
    merged_df.to_csv(output_file_path, index=False)
    print(f"[+] Merged file saved as: {output_file_name}")
    return output_file_path


"""
Adds a new column 'model_answer' to the merged answer file
Save the file with integrated human answer to ../Model Answer/Origin Answer/ for subsequent processing.
"""
def integrate_human_answer(file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    # Check if required columns exist
    if 'selected_columns' not in df.columns or 'selected_methods' not in df.columns:
        raise ValueError("The required columns 'selected_columns' and 'selected_methods' are not in the DataFrame.")

    # Function to convert string representation of lists into actual list objects
    def convert_to_list(string):
        try:
            return ast.literal_eval(string)
        except:
            return []

    # Create a new column with JSON formatted string based on the lists derived from selected_columns and selected_methods
    df['model_answer'] = df.apply(lambda row: json.dumps({
        "columns": convert_to_list(row['selected_columns']),
        "methods": convert_to_list(row['selected_methods'])
    }), axis=1)
    df['extracted_answer'] = df.apply(lambda row: json.dumps({
        "columns": convert_to_list(row['selected_columns']),
        "methods": convert_to_list(row['selected_methods'])
    }), axis=1)
    
    # Save the updated DataFrame back to CSV
    prefix = os.path.basename(file_path).split('_merged.csv')[0]
    updated_file_name = f"human_{prefix}.csv".replace('answer_', '')
    # updated_file_path = os.path.join(os.path.dirname(file_path), updated_file_name)
    updated_file_path = '../Model Answer/Origin Answer/' + updated_file_name
    # Save the updated DataFrame back to CSV
    df.to_csv(updated_file_path, index=False)
    print(f"[+] Extracted human answer, file saved as: {updated_file_path}")
    return updated_file_path


# main
if __name__ == '__main__':
    work_dir = 'answer'
    # suffixes of the files to merge
    stats_suffixes = [1, 2, 3]
    non_stats_suffixes = [1, 2, 3]

    # Merge human answer csv files by prefixes
    stats_merged_path_closed_book = merge_human_answer_by_prefix(work_dir=work_dir, 
                                                     prefix='answer_Stats Background_Closed-book', 
                                                     suffixes=stats_suffixes)
    non_stats_merged_path_closed_book = merge_human_answer_by_prefix(work_dir=work_dir, 
                                                         prefix='answer_Non-Stats Background_Closed-book', 
                                                         suffixes=non_stats_suffixes)
    stats_merged_path_open_book = merge_human_answer_by_prefix(work_dir=work_dir, 
                                                     prefix='answer_Stats Background_Open-book', 
                                                     suffixes=stats_suffixes)
    non_stats_merged_path_open_book = merge_human_answer_by_prefix(work_dir=work_dir, 
                                                         prefix='answer_Non-Stats Background_Open-book', 
                                                         suffixes=non_stats_suffixes)

    # Integrate for the merged human answer
    # Save to ../Model Answer/Origin Answer/ for subsequent processing
    integrate_human_answer(stats_merged_path_closed_book)
    integrate_human_answer(non_stats_merged_path_closed_book)
    integrate_human_answer(stats_merged_path_open_book)
    integrate_human_answer(non_stats_merged_path_open_book)
