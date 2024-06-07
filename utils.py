# -*- coding: utf-8 -*-
import ast
import os
import glob
import re
import csv
import json
import path
import pandas as pd
import numpy as np
from scipy.stats import anderson
from scipy.stats import spearmanr, kendalltau
from scipy.stats import chi2_contingency
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


'''
Get the names of all csv dataset under a certain path
Output: return the file name list
'''
def get_dataset_name_list(path):
    # Use the glob module to get all CSV files under a specified path
    csv_files = glob.glob(os.path.join(path, '*.csv'))
    # # Extract file name part
    # csv_filenames = [os.path.basename(file) for file in csv_files]
    # Extract filename part and remove extension
    csv_filenames = [os.path.splitext(os.path.basename(file))[0] for file in csv_files]
    return csv_filenames


"""
Determine if a pandas Series is a categorical variable.
A series is considered categorical if the ratio of unique values to total number of values is less than threshold.
"""
def is_categorical(series, threshold=0.2):
    unique_count = series.nunique()
    total_count = len(series)
    return (unique_count / total_count) < threshold


"""
Determine if a pandas Series is a quant variable.
A series is considered quant if it is numeric and 
the ratio of unique values to total number of values is greater than or equal to threshold.
"""
def is_quantitative(series, threshold=0.2):
    is_numeric = pd.api.types.is_numeric_dtype(series)
    unique_count = series.nunique()
    total_count = len(series)
    ratio = unique_count / total_count
    return is_numeric and ratio >= threshold


'''
Test the data type of each column of a file: categorical data, quant data, other
'''
def check_column_types_for_a_file(csv_file):
    df = pd.read_csv(csv_file)
    column_types = []
    for column in df.columns:
        series = df[column]
        if is_categorical(series):
            column_types.append("cate") # categorical
        elif is_quantitative(series):
            column_types.append("quant") # quantitative
        else:
            column_types.append("other") # other
    return column_types


"""
Tries to get the data type of a column from its metadata.
Returns None if the metadata entry is not found or if the type is empty.
"""
def get_data_type_from_metadata(column_name, dataset_name):
    metadata_file = f"{path.meta_dir + path.col_meta_dir}{dataset_name}_col_meta.csv"
    try:
        metadata = pd.read_csv(metadata_file)
        dtype_row = metadata[metadata['column_header'] == column_name]
        if not dtype_row.empty:
            data_type = dtype_row['data_type'].values[0]
            # Check if data_type is not NaN and not empty
            if pd.notna(data_type) and data_type.strip():
                return data_type
    except FileNotFoundError:
        print(f"Metadata file {metadata_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


"""
Determines the data type of a column of data from metadata.
If not accessible in metadata or metadata empty, use is_categorical and is_quantitative to judge.
"""
def determine_data_type(series, dataset_name, threshold=0.2):
    data_type = get_data_type_from_metadata(series.name, dataset_name)
    if data_type:
        return data_type
    elif is_categorical(series, threshold): # categorical
        return "cate"
    elif is_quantitative(series, threshold): # quantitative
        return "quant"
    else: # other
        return "other"
   

'''
Check if it is a number (int or float)
'''
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


'''
Functions for processing and transforming special quant data
'''
def process_special_cont_data(series):
    def convert_value(x):
        if isinstance(x, str):
            if '%' in x:
                try:
                    return float(x.replace('%', '')) / 100
                except ValueError:
                    return None
            elif 'M' in x or 'm' in x:
                try:
                    return float(x.lower().replace('m', '')) * 1e6
                except ValueError:
                    return None
            elif 'K' in x or 'k' in x:
                try:
                    return float(x.lower().replace('k', '')) * 1e3
                except ValueError:
                    return None
        else:
            try:
                return float(x)
            except (ValueError, TypeError):
                return None
    return series.apply(convert_value)


'''
Get integrated dataset mini for test
n: # The number of rows you want to keep (excluding the header row)
'''
def random_select_mini_dataset(input_file, n, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    # Check if n is greater than the number of rows in the file (excluding the header row)
    if n >= len(df):
        print("Error: n is greater than or equal to the number of rows in the file.")
        return
    # Randomly select n rows, excluding the header row
    selected_rows = df.sample(n)
    # Combine the header row and the selected rows
    result = pd.concat([df.iloc[:1], selected_rows])
    # Save the result to a new CSV file
    result.to_csv(output_file, index=False)


"""
Thinen a CSV file by keeping every nth row, starting from the second row (excluding the header).
Aim: reduce overly large file to keep the final dataset more balanced.
Parameters:
- n: int, the interval of rows to keep. Every nth row is kept.
- file_name: str, the name of the CSV file to be reduced. The operation overwrites the original file.
"""
def thinen_csv_rows(n, file_name):
    file_path = path.info_dir + file_name + '.csv'
    # Check if n is valid
    if n < 1:
        print("Error: n must be greater than 0.")
        return
    try:
        # Read the CSV file, keeping the header
        df = pd.read_csv(file_path)
        # Ensure there's more than one row to process
        if df.shape[0] < 2:
            print("Error: The file does not contain enough rows to reduce.")
            return
        # Exclude the first row (header) from the operation, then select every nth row starting from the second data row
        reduced_df = pd.concat([df.iloc[0:1], df.iloc[1::n, :]])
        # Overwrite the original file with the reduced dataframe
        reduced_df.to_csv(file_path, index=False)
        print("[+] File: " + file_name + " reduction completed successfully.")
    except FileNotFoundError:
        print(f"[!] Error: The file {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print("[!] Error: The file is empty.")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")


'''
Reorganize and shuffle dataset
Aiming to facilitate test procedures
Same dataset rows should be together but same methods or task types gethering together should be avoided.
'''
def reorganize_shuffle_dataset(input_dir, file_name):
    try:
        input_file_path = input_dir + file_name + '.csv'
        # Load dataset from the input file
        df = pd.read_csv(input_file_path)
        # Group data by 'dataset' column
        grouped = df.groupby('dataset')
        shuffled_df = pd.DataFrame()  # Initialize an empty DataFrame to store shuffled data
        # Shuffle rows in each group and concatenate them into a single DataFrame
        for _, group in grouped:
            shuffled_group = shuffle(group)  # Shuffle data rows in the current group
            shuffled_df = pd.concat([shuffled_df, shuffled_group], ignore_index=True)  # Concatenate shuffled group with the main DataFrame
        # output path
        output_file_path = input_dir + "shuffled_" + file_name + '.csv'
        # Save shuffled dataset to the output file
        shuffled_df.to_csv(output_file_path, index=False)
        print(f"[+] Shuffled dataset has been saved to: {output_file_path}")
    except FileNotFoundError:
        print(f"[-] File not found: {input_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the shuffle_dataset function
# reorganize_shuffle_dataset('Integrated Dataset/', 'Integrated Dataset mini')


'''
Perform Anderson-Darling test for normality.
'''
def is_normality_ad(sample, alpha=0.05):
    result = anderson(sample)
    significance_levels = result.significance_level
    critical_values = result.critical_values
    for i in range(len(significance_levels)):
        if significance_levels[i] == alpha*100:
            # Anderson-Darling's significance level is returned as a percentage
            return result.statistic < critical_values[i]
    return False  # If no significance level is found, return false


'''
New extraction function:
Extracts and returns the first JSON object found within the first pair of braces in the input string.
If the substring enclosed by the first pair of braces is a valid JSON, it returns this substring.
If there are no braces or the JSON is invalid, it returns "Invalid Answer".
'''
def extract_json_answer(input_string): # New extraction function: 
    # Find the position of the first opening brace
    start_index = input_string.find('{')
    # Find the position of the first closing brace starting from just after the first opening brace
    end_index = input_string.find('}', start_index)
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # Extract the substring that includes the first set of braces
        json_str = input_string[start_index:end_index+1]
        try:
            # Attempt to parse the JSON string to check its validity
            json.loads(json_str)
            return json_str
        except ValueError:
            # Return an error message if the JSON is not valid
            return "Invalid Answer"
    else:
        # Return an error message if no valid braces are found
        return "Invalid Answer"


'''
Calculates the area of a polygon, which can be used in radar charts
Parameters:
- values: The scoring rate of each vertex (the radius of the polar coordinates).
- angles: The angle of each vertex (the angle of the polar coordinates), in radians.
'''
def calculate_polygon_area(values, angles):
    # Convert polar coordinates to Cartesian coordinates
    n = len(values)
    x = [values[i] * np.cos(angles[i]) for i in range(n)]
    y = [values[i] * np.sin(angles[i]) for i in range(n)]
    # Calculate the area of the polygon
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += x[i] * y[j] - x[j] * y[i]
    return abs(area) / 2


"""
Calculates the average value of the given scores in a radar chart.
Parameters:
- values: The scoring rate of each vertex (the radius of the polar coordinates).
"""
def calculate_radar_chart_average(values):
    # Return 0 if the list is empty to avoid division by zero
    if not values:
        return 0
    return sum(values) / len(values)


"""
Given a dataset name, returns all information from the corresponding metadata file.
Parameters:
- dataset_name: The name of the dataset.
Return: 
- A DataFrame containing the metadata of the dataset.
"""
def get_metadata(dataset_name):
    # Construct the path to the metadata file based on the dataset name
    metadata_file_path = f'Data/Metadata/Column Metadata/{dataset_name}_col_meta.csv'
    # Load and return the metadata file
    metadata_df = pd.read_csv(metadata_file_path)
    return metadata_df


"""
Given metadata and a JSON string of relevant columns, returns the information for these columns from the metadata.
Parameters: 
- metadata_df: A DataFrame containing the metadata of a dataset.
- relevant_columns_json: A JSON string representing the list of relevant columns and their properties.
Return:
- A DataFrame containing the metadata information for the relevant columns.
"""
def get_relevant_columns_info(metadata_df, relevant_columns_json):
    # Parse the JSON string to extract column headers
    relevant_columns_list = [item['column_header'] for item in json.loads(relevant_columns_json)]
    # Filter the metadata to only include rows with column headers that match the relevant columns
    relevant_info_df = metadata_df[metadata_df['column_header'].isin(relevant_columns_list)]
    return relevant_info_df


'''
Split benchmark (Similar to split into a training set and a test set, but actually just for sample). 
The proportion of test_ratio randomly selected is used as the test set, and the rest is used as the training set.
'''
def split_benchmark(dataset_name: str, test_ratio: float=0.1):
    # Make sure that the ratio parameter is valid
    if not 0 <= test_ratio <= 1:
        raise ValueError("[!] Test set ratio must be between 0 and 1.") 
    df = pd.read_csv(path.integ_dataset_path + path.balance_path +  dataset_name + '.csv')
    # Randomly divide the dataset
    train_df, test_df = train_test_split(df, test_size=test_ratio)
    # Save the training and test sets
    train_df.to_csv(f"{path.integ_dataset_path + path.balance_path}{dataset_name} rest.csv", index=False)
    test_df.to_csv(f"{path.integ_dataset_path + path.balance_path}{dataset_name} test.csv", index=False)
    print(f"[+] Files saved in folder: {path.integ_dataset_path}{dataset_name}")


'''
Extract ground truth of selection of relevant columns or applicable methods from dataset
col_to_extract: "results" for methods, or "relevant_column" for relevant columns
This function should be used after prompt organizing.
'''
# Extract ground truth of methods for a row
def extract_ground_truth_for_row(row, col_to_extract: str):
    try:
        # Convert the string representation of list of dicts into an actual list of dicts
        results = ast.literal_eval(row.replace("false", "False").replace("true", "True"))
        if col_to_extract == "results":
            # Extract 'method' values where 'conclusion' is not "Not applicable"
            ground_truth_list = [result['method'] for result in results if result['conclusion'] != "Not applicable"]
        elif col_to_extract == "relevant_column":
            # Extract 'relevant_column' ground truth
            ground_truth_list = [result['column_header'] for result in results]
        else:
            raise ValueError("[!] Invalid column to extract: " + col_to_extract + ". Please use 'results' or 'relevant_column'.")
        return ground_truth_list
    except json.JSONDecodeError:
        print("[!] Error decoding JSON from row. Row content may be malformed.")
        return []
    except Exception as e:
        print(f"[!] An unexpected error occurred while processing row: {e}")
        return []

# Extract ground truth of methods for a file
def extract_ground_truth(file_path: str):
    try:
        # Load the CSV file
        # file_path = path.model_ans_path + path.orgin_ans_path + file_name + '.csv'
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[!] The {file_path} is not found.")
        return
    except Exception as e:
        print(f"[!] An error occurred while reading the file: {e}")
        return
    try:
        # Apply the function to the 'results' and 'relevant_column' columns
        df['methods_ground_truth'] = df['results'].apply(lambda x: extract_ground_truth_for_row(x, 'results'))
        df['columns_ground_truth'] = df['relevant_column'].apply(lambda x: extract_ground_truth_for_row(x, 'relevant_column'))
        # Combine extracted methods and columns into a single column with dictionary format
        df['ground_truth'] = df.apply(lambda x: json.dumps({"columns": x['columns_ground_truth'], "methods": x['methods_ground_truth']}), axis=1)
        # Remove 'methods_ground_truth' and 'columns_ground_truth' columns before saving
        df.drop(['methods_ground_truth', 'columns_ground_truth'], axis=1, inplace=True)
        # Save the updated dataframe to a csv
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"[!] An error occurred while saving the file: {e}")
        return
    print(f"[+] Ground truth of selection of methods extracted for {file_path}")