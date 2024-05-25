# -*- coding: gbk -*-
import pandas as pd
import json
from collections import Counter
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import os


# Mapping statistical methods to their correspinding task type
tasks_to_methods = {
    'Correlation Analysis': [
        'Pearson Correlation Coefficient', 'Spearman Correlation Coefficient', 
        'Kendall Correlation Coefficient', 'Partial Correlation Coefficient'
    ],
    'Distribution Compliance Test': [
        'Anderson-Darling Test', 'Shapiro-Wilk Test of Normality', 'Kolmogorov-Smirnov Test for Normality',
        'Lilliefors Test', 'Kolmogorov-Smirnov Test', 'Kolmogorov-Smirnov Test for Uniform distribution', 
        'Kolmogorov-Smirnov Test for Gamma distribution', 'Kolmogorov-Smirnov Test for Exponential distribution'
    ],
    'Contingency Table Test': [
        'Chi-square Independence Test', 'Fisher Exact Test', 'Mantel-Haenszel Test'
    ],
    'Descriptive Statistics': [
        'Mean', 'Median', 'Mode', 'Range', 'Quartile', 'Standard Deviation', 'Skewness', 'Kurtosis'
    ],
    'Variance Test': [
        'Mood Variance Test', 'Levene Test', 'Bartlett Test', 'F-Test for Variance'
    ]
}


task_abbreviations = {
    'Correlation Analysis': 'CA',
    'Distribution Compliance Test': 'DCT',
    'Contingency Table Test': 'CTT',
    'Descriptive Statistics': 'DS',
    'Variance Test': 'VT'
}


# Function to determine the task based on methods
def determine_task(method_list, tasks_to_methods):
    method_count = Counter(method_list)
    task_scores = {task: 0 for task in tasks_to_methods.keys()}
    
    for method, count in method_count.items():
        for task, methods in tasks_to_methods.items():
            if method in methods:
                task_scores[task] += count

    # Determine the task with the highest score
    highest_score_task = max(task_scores, key=task_scores.get)
    return highest_score_task



# Function to process the CSV files and save the modified DataFrame as a new CSV file
def process_csv_files(file_paths, tasks_to_methods):
    processed_files_path_list = []
    for file_path in file_paths:
        data = pd.read_csv(file_path)
        methods_list = []
        for answer in data['extracted_answer']:
            try:
                methods = json.loads(answer.replace("\'", "\""))['methods']
                methods_list.append(methods)
            except json.JSONDecodeError:
                methods_list.append([])  # Use empty list for unparseable entries

        data['extracted_answer'] = methods_list
        data['answer_task'] = data['extracted_answer'].apply(lambda x: determine_task(x, tasks_to_methods))
        
        # Construct a new output file path
        output_file_path = file_path.replace('.csv', '_processed.csv')
        output_file_path = output_file_path.replace('Model Answer/Processed Answer', 'Model Answer/Processed Answer (for task confusion analysis)')
        
        # Save the modified DataFrame to a new CSV file
        data.to_csv(output_file_path, index=False)
        processed_files_path_list.append(output_file_path)
        print(f"[+] Processed file: {output_file_path}")
    
    return processed_files_path_list


# Function to compare 'answer_task' with 'task' and plot confusion matrix
def plot_confusion_matrix(file_path):
    data = pd.read_csv(file_path)
    cm = confusion_matrix(data['task'], data['answer_task'], labels=list(tasks_to_methods.keys()))
    
    # Replace labels with abbreviations for plotting
    labels = [task_abbreviations[task] for task in tasks_to_methods.keys()]
    
    # Plotting confusion matrix
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels, annot_kws={"size": 14})
    plt.xlabel('Selected Tasks', fontsize=14)
    plt.ylabel('Actual Tasks', fontsize=14)
    model_name = os.path.basename(file_path).replace('.csv', '').replace('_', ' ').replace('zero', '0').replace('one', '1').replace('two', '2').replace(' Background', '').replace(' processed', '')
    # plt.title(f'{model_name} Task Confusion Matrix', fontsize=13)
    plt.tight_layout()
    
    # Save the plot to a specific folder structure
    output_image_path = f'Chart/Confusion Matrix/confusion_matrix_{model_name}.pdf'
    plt.savefig(output_image_path, format='pdf', bbox_inches='tight', dpi=200)
    plt.close()
    print(f"[+] Confusion matrix saved to: {output_image_path}")
    return output_image_path


# main
if __name__ == '__main__':
    # List all CSV files in the specific directory
    directory_path = 'Model Answer/Processed Answer'
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')]

    # Process the files
    processed_files_paths = process_csv_files(file_paths, tasks_to_methods)

    # Plot confusion matrix for each processed file
    confusion_matrix_paths = [plot_confusion_matrix(file_path) for file_path in processed_files_paths]
    # print(confusion_matrix_paths)
