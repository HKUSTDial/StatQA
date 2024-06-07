# -*- coding: gbk -*-
import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.metrics import confusion_matrix
# from matplotlib import gridspec
from matplotlib.gridspec import GridSpec
import seaborn as sns
import json


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


'''
Analyzes csv files in a work directory to identify and calculate the proportion of four types of errors out of all errors (selection_overall = 0)
Error Types:
1. Invalid Answers (Only this one error type): The 'extracted_answer' does not contain any of the specified methods, indicating a misunderstanding or lack of knowledge.
2. Column Selection Errors (Only this one error type): The 'columns_score' is 0, suggesting incorrect data column selection in the assessment.
3. Statistical Task Confusion (Only this one error type): The 'methods_comparison_result' contains a 'Correct' count of 0 and non-zero 'Wrong' and 'Missed' counts, indicating confusion between statistical tasks.
4. Applicability Errors (Only this one error type): The 'methods_comparison_result' has a 'Correct' count greater than 0 and non-zero 'Wrong' and 'Missed' counts, suggesting errors in applying the correct statistical methods despite some correct identifications.
5. Mixed Errors (Multiple error types): Containing multiple error types.
'''
def error_analysis(work_dir):
    summary_list = []
    for filename in os.listdir(work_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(work_dir, filename)
            data = pd.read_csv(file_path)
            # Denominator: wrong number of rows
            # data_filtered = data[data['selection_overall'] == 0]
            # Denominator: total number of rows
            data_filtered = data

            # Initialize counters for error types
            invalid_answers = 0
            column_errors = 0
            statistical_confusion = 0
            applicability_errors = 0
            # mixed_errors = 0
            mixed_errors_column_statistical = 0
            mixed_errors_column_applicability = 0
            mixed_errors_statistical_applicability = 0
            mixed_errors_all = 0

            for index, row in data_filtered.iterrows():
                # Detect if there's an invalid answer
                if not any(method in row['extracted_answer'].lower() for method in methods_list):
                    invalid_answers += 1
                else:
                    # Initialize a dictionary to track other errors
                    errors = {
                        'column_error': row['columns_score'] == 0,
                        'statistical_confusion': False,
                        'applicability_error': False
                    }

                    # Process JSON data for confusion and applicability errors
                    try:
                        methods_result = json.loads(row['methods_comparison_result'])
                        correct = methods_result.get('Correct', 0)
                        wrong_missed = methods_result.get('Wrong', 0) + methods_result.get('Missed', 0)
                        if correct == 0 and wrong_missed > 0:
                            errors['statistical_confusion'] = True
                        if correct > 0 and wrong_missed > 0:
                            errors['applicability_error'] = True
                    except json.JSONDecodeError:
                        errors['statistical_confusion'] = True

                    # Determine the error types, excluding invalid answers for mixed error calculation
                    error_count = sum(errors.values())
                    if error_count == 1:
                        if errors['column_error']:
                            column_errors += 1
                        elif errors['statistical_confusion']:
                            statistical_confusion += 1
                        elif errors['applicability_error']:
                            applicability_errors += 1
                    elif error_count > 1:
                        # mixed_errors += 1
                        if errors['column_error'] and errors['statistical_confusion']:
                            mixed_errors_column_statistical += 1
                        elif errors['column_error'] and errors['applicability_error']:
                            mixed_errors_column_applicability += 1
                        elif errors['statistical_confusion'] and errors['applicability_error']:
                            mixed_errors_statistical_applicability += 1
                        elif errors['column_error'] and errors['statistical_confusion'] and errors['applicability_error']:
                            mixed_errors_all += 1

            # Calculate proportions based on filtered rows
            total_cnt = len(data_filtered)
            summary_list.append({
                'Model': filename.replace('.csv', ''),
                'Invalid Answer': round((invalid_answers / total_cnt), 5) if total_cnt else 0,
                'Column Selection Error (CSE)': round((column_errors / total_cnt), 5) if total_cnt else 0,
                'Statistical Task Confusion (STC)': round((statistical_confusion / total_cnt), 5) if total_cnt else 0,
                'Applicability Error (AE)': round((applicability_errors / total_cnt), 5) if total_cnt else 0,
                # 'Mixed Error': round((mixed_errors / total_errors), 5) if total_errors else 0,
                'Mixed Errors (CSE+STC)': round((mixed_errors_column_statistical / total_cnt), 5) if total_cnt else 0,
                'Mixed Errors (CSE+AE)': round((mixed_errors_column_applicability / total_cnt), 5) if total_cnt else 0,
                'Mixed Errors (STC+AE)': round((mixed_errors_statistical_applicability / total_cnt), 5) if total_cnt else 0,
                'Mixed Errors (CSE+STC+AE)': round((mixed_errors_all / total_cnt), 5) if total_cnt else 0
            })
            print(f"[+] {filename} processed.")

    # Convert the summary list to a DataFrame and save as CSV
    summary_df = pd.DataFrame(summary_list)
    output_path = os.path.join('Model Answer/Task Performance/', 'error_analysis_summary.csv')
    summary_df.to_csv(output_path, index=False)
    return output_path


'''
Plotting the error analysis bar chart - for selected file order
'''
def plot_error_analysis(file_path, output_name: None, subplot_titles: None):
    data = pd.read_csv(file_path, skip_blank_lines=False)
    empty_rows = data.index[data.isnull().all(1)]
    datasets = []
    model_counts = []
    start_idx = 0

    for end_idx in empty_rows:
        if start_idx != end_idx:
            segment = data[start_idx:end_idx]
            datasets.append(segment)
            model_counts.append(len(segment['Model'].dropna().unique()))
        start_idx = end_idx + 1
    if start_idx < len(data):
        segment = data[start_idx:]
        datasets.append(segment)
        model_counts.append(len(segment['Model'].dropna().unique()))

    total_models = sum(model_counts)
    widths = [count / total_models for count in model_counts]

    fig = plt.figure(figsize=(20, 9.9))
    gs = GridSpec(1, len(datasets), width_ratios=widths)

    # Custom subgraph title list
    # subplot_titles = ['LLaMA-2', 'LLaMA-3', 'GPT Models', 'SFT', 'Human']

    for i, dataset in enumerate(datasets):
        ax = fig.add_subplot(gs[i])
        if not dataset.empty:
            # Replace model name
            models = [model.replace('_', ' ').replace('zero', '0').replace('one', '1').replace('two', '2').replace(' Background', '').replace('instruct', 'inst').replace('human ', '').replace('llama2 ', '').replace('llama3 ', '').replace('gpt-3.5-turbo', 'GPT-3.5T').replace('gpt-4', 'GPT-4').replace('7b sft 0-shot', 'llama2-7b sft').replace('8b sft 0-shot', 'llama3-8b sft').replace('8b inst sft 0-shot', 'llama3-8b inst sft').replace('stats-prompt', '1-shot+DK')
                      for model in dataset['Model'].dropna().unique()]
            error_types = ['Invalid Answer', 
                           'Column Selection Error (CSE)', 
                           'Statistical Task Confusion (STC)', 
                           'Applicability Error (AE)', 
                           'Mixed Errors (CSE+STC)', 
                           'Mixed Errors (CSE+AE)', 
                           'Mixed Errors (STC+AE)',
                           'Mixed Errors (CSE+STC+AE)'
                           ]
            colors = ['#FED9A6', '#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4', '#f3f0ba', '#bce7d7', '#d3cfc7']
            bar_width = 0.88

            for j, error_type in enumerate(error_types):
                ax.bar(models, dataset[error_type], bottom=dataset[error_types[:j]].sum(axis=1), color=colors[j], edgecolor='white', width=bar_width, label=error_type)
            
            for k, rect in enumerate(ax.patches):
                height = rect.get_height()
                if round(height, 2) > 0.020:
                    ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_y() + height / 2.0, f'{height:.2f}', 
                            ha='center', va='center', fontsize=18)  # Adjusted font size here
                elif round(height, 2) <= 0.020 and round(height, 3) >= 0.01:
                    ax.text(rect.get_x() + rect.get_width() / 2.0, rect.get_y() + height / 2.0, f'{height:.2f}', 
                            ha='center', va='center', fontsize=12)  # Adjusted font size here
            
            for label in ax.get_xticklabels():
                label.set_horizontalalignment('right')

            ax.set_title(subplot_titles[i], fontsize=22)  # Set a custom title for each subplot
            ax.tick_params(axis='x', rotation=45, labelsize=20)
            ax.set_ylim(0, 1)  # Limit the ordinate range to 0 to 1
            # Only show y-axis ticks for the first subplot
            if i != 0:
                ax.tick_params(axis='both', which='both', length=0)  # Hide ticks
                ax.set_yticklabels([])
            else:
                ax.set_ylabel('Error Rate', fontsize=18)
    

    # fig.suptitle('Error Type Analysis Across Experiments', fontsize=20)  # Set a large title for the entire picture
    handles, labels = ax.get_legend_handles_labels()
    # fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(1, 0.9), title="Error Types", fontsize=14, title_fontsize=16)
    # fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1), title="Error Types", fontsize=14, title_fontsize=16, ncol=len(labels))
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1), fontsize=20, title_fontsize=18, ncol=len(labels)//2, columnspacing=1.0, handletextpad=0.5)

    # plt.tight_layout(rect=[0, 0, 0.9, 0.98])  # Adjust layout to accommodate large headlines
    plt.tight_layout(rect=[0, 0, 1, 0.89]) 
    plt.subplots_adjust(right=1, wspace=0.0)
    plt.savefig(f'Chart/Error Analysis/{output_name}.pdf', format='pdf', bbox_inches='tight', dpi=500)
    print(f"[+] Error type analysis bar chart saved: {output_name}.")


# main
if __name__ == '__main__':
    # Define the directory path where CSV files are located
    directory_path = 'Model Answer/Processed Answer/'
    # Flatten the list of methods for easier checking
    methods_list = [method.lower() for sublist in tasks_to_methods.values() for method in sublist]
    
    # Conduct statistics for error types and obtain a summary csv
    error_analysis_path = error_analysis(directory_path)

    # Plot bar chart for error analysis - for selected file order
    # plot_error_analysis('Model Answer/Task Performance/selected error_analysis_summary new.csv', 
    #                     output_name='Error Analysis Bar Chart', 
    #                     subplot_titles = ['LLaMA-2', 'LLaMA-3', 'GPT Models', 'SFT', 'Human'])
    # plot_error_analysis('Model Answer/Task Performance/selected error_analysis_summary for CoT.csv', 
    #                     output_name='Error Analysis Bar Chart for CoT',
    #                     subplot_titles = ['LLaMA-2', 'LLaMA-3', 'GPT Models'])


