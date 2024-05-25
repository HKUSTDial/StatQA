# -*- coding: gbk -*-
import os
import pandas as pd

'''
Define a function to compute the overall score_rate of the model: 
the total number of correct choices divided by the total number of rows
'''
def calculate_overall_score_rate(df):
    total_obtained = df['obtained_valid_score'].sum()
    total_full = df['total_full_score'].sum()
    overall_score_rate = total_obtained / total_full if total_full else 0
    return round(overall_score_rate, 5)


'''
Summary the performance of all models in certrain directories.
'''
def analyze_directory_data(perf_type: str):
    if perf_type == 'overall':
        input_directory_path = 'Model Answer/Task Performance/Selection Overall/All'
    elif perf_type == 'methods':
        input_directory_path = 'Model Answer/Task Performance/Methods Selection/All'
    elif perf_type == 'columns':
        input_directory_path = 'Model Answer/Task Performance/Columns Selection/All'
    # Derive the base output directory by removing the last directory segment from the input path
    output_directory_path = os.path.dirname(input_directory_path)
    
    # Get all CSV files in the input directory
    csv_files = [os.path.join(input_directory_path, f) for f in os.listdir(input_directory_path) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    # Sample a CSV to extract the task names
    sample_df = pd.read_csv(csv_files[0])
    columns = ['model', 'overall_score_rate'] + list(sample_df['task'].unique())
    # Initialize an empty DataFrame to store the summarized data
    summary_df = pd.DataFrame(columns=columns)
    # Use a list to collect data from all models, and then use pandas.concat to merge
    model_data_list = []

    # Traverse all csv files and calculate the data of each model
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        overall_score_rate = calculate_overall_score_rate(df)
        # Get model name from file name
        model_name = os.path.splitext(os.path.basename(csv_file))[0]
        # Organize the model's data into one row
        model_data = {'model': model_name, 'overall_score_rate': overall_score_rate}
        for _, row in df.iterrows():
            model_data[row['task']] = row['score_rate']
        model_data_list.append(model_data)

    summary_df = pd.concat([summary_df, pd.DataFrame(model_data_list)], ignore_index=True)
    summary_df_new_order = [
        "model",
        "overall_score_rate",
        "Correlation Analysis",
        "Contingency Table Test",
        "Distribution Compliance Test",
        "Variance Test",
        "Descriptive Statistics"
    ]
    summary_df = summary_df.reindex(columns=summary_df_new_order)
    # Save the summary DataFrame to the derived output directory
    summary_csv_path = os.path.join(output_directory_path, f'{perf_type}_selection_summary_performance.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"[+] Summary file has been created at {summary_csv_path}.")



if __name__ == '__main__':
    analyze_directory_data('overall')
    analyze_directory_data('methods')
    analyze_directory_data('columns')