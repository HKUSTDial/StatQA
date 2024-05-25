# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import utils
import pandas as pd
import ast
import path


# Work dir: process and set difficulty level for preliminary question file
work_dir = path.info_dir + path.prequestion_dir
file_suffix = '_withPreliminaryQuestions'


# Tasks need to be manually adjusted to medium difficulty level
medium_difficulty_tasks = [
    'Chi-square and fisher exact test info extraction (Independent)',
    'Chi-square and fisher exact test info extraction (Not independent)',
    'KS distribution comparison info extraction (Distribution not significantly different)',
    'KS distribution comparison info extraction (Distribution significantly different)',
    'Mantel Haenszel test info extraction (Independent)',
    'Mantel Haenszel test info extraction (Not independent)',
    'Partial correlation info extraction (Not strongly correlated)',
    'Partial correlation info extraction (Strongly correlated)',
    'Variance test info extraction (Variance not significantly different)',
    'Variance test info extraction (Variance significantly different)'
]


'''
Manually adjust and set the difficulty level for a specific file
Defficulty level: easy/medium/hard (all lowcase letters)
Cancelled.
'''
def set_difficulty_for_file(file_name, difficulty_level: str='easy'):
    file_path = work_dir + file_name + file_suffix + '.csv'
    try:
        df = pd.read_csv(file_path)
        # Check if 'difficulty' column exists, create it if not
        if 'difficulty' not in df.columns:
            df['difficulty'] = difficulty_level
        else:
            df['difficulty'] = difficulty_level
        # save csv
        df.to_csv(file_path, index=False)
        print(f"[m] Manually set 'difficulty' column for {file_name} to '{difficulty_level}'")

    except FileNotFoundError:
        print(f"[!] Error: File '{file_name}' not found in '{work_dir}'.")
    except pd.errors.EmptyDataError:
        print(f"[!] Error: File '{file_name}' is empty.")
    except Exception as e:
        print(f"[!] Error processing file '{file_name}': {e}")


'''
The difficulty level is adjusted according to the value of the "inclusion" key in the dictionary string in each row of data.
If applicable cases counts are less than "Not applicable", difficulty level increases by one notch: easy->medium, medium->hard.
If applicable cases counts are greater than or equal to "Not applicable" and "Not applicable" counts are non-zero, set to medium. 
In other cases, difficulty level remains unchanged.
'''
def adjust_difficulty_based_on_conclusion(row):
    applicable_count = 0
    not_applicable_count = 0
    for item in row:
        if isinstance(item, str) and item.startswith('{'):
            try:
                data_dict = ast.literal_eval(item)
                if 'conclusion' in data_dict:
                    if data_dict['conclusion'] == 'Not applicable':
                        not_applicable_count += 1
                    else:
                        applicable_count += 1
            except:
                continue
    # Adjust the difficulty level according to the rules stated above
    if applicable_count <= not_applicable_count:
        return 'medium' if row['difficulty'] == 'easy' else 'hard'
    elif applicable_count >= not_applicable_count and not_applicable_count > 0:
        return 'medium'
    else:
        return row['difficulty']


'''
Top function: set difficulty level for a file based on rules above
1. Init default difficulty level is easy,;
2. Some tasks need manual adjustment to medium are recorded in a list;
3. Set difficulty level based on key of conclusion's value.
'''
def set_difficulty_level(file_name):
    file_path = work_dir + file_name + file_suffix + '.csv'
    try:
        df = pd.read_csv(file_path)
        # The initial difficulty is all set to easy
        df['difficulty'] = 'easy'
        # If the file name is in a specific list, set the difficulty level to medium
        if file_name in medium_difficulty_tasks:
            # set_difficulty_for_file(file_name, 'medium')
            df['difficulty'] = 'medium'
            print(f"    + Manually set 'difficulty' to 'medium'")
        else:
            print(f"    - No need to manually adjust 'difficulty'")
        # Adjust the difficulty level based on the conclusion key
        df['difficulty'] = df.apply(adjust_difficulty_based_on_conclusion, axis=1)
        df.to_csv(file_path, index=False)
        print(f"[+] Dataset: {file_name} Difficulty added!")
    except FileNotFoundError:
        print(f"[!] Error: File '{file_name}' not found in '{work_dir}'.")
    except pd.errors.EmptyDataError:
        print(f"[!] Error: File '{file_name}' is empty.")
    except Exception as e:
        print(f"[!] Error processing file '{file_name}': {e}")
    return


'''
Remove difficulty column
'''
def remove_difficulty_level(file_name):
    file_path = work_dir + file_name + file_suffix + '.csv'
    try:
        df = pd.read_csv(file_path)
        # Check if 'difficulty' column exists, remove if present
        if 'difficulty' in df.columns:
            df.drop('difficulty', axis=1, inplace=True)
            # save csv
            df.to_csv(file_path, index=False)
            print(f"[-] Removed 'difficulty' column from {file_name}")
        else:
            print(f"[!] 'difficulty' column not found in {file_name}")
    except FileNotFoundError:
        print(f"[!] Error: File '{file_name}' not found in '{work_dir}'.")
    except pd.errors.EmptyDataError:
        print(f"[!] Error: File '{file_name}' is empty.")
    except Exception as e:
        print(f"[!] Error processing file '{file_name}': {e}")
    return


# main
if __name__=='__main__':
    file_name_list = utils.get_dataset_name_list(path.info_dir)
    for item in file_name_list:
        set_difficulty_level(file_name=item)
        # remove_difficulty_level(file_name=item)
    set_difficulty_for_file(file_name='Descriptive statistics info extraction', difficulty_level='easy')
    print("Difficulty level set.")
