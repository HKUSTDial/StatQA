# -*- coding: gbk -*-
import math
import os
import json
import utils
import path
import mappings
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


'''
Process, analyze, and visualize LLMs' answer
'''


'''
Extract json answer from model reply
Set 'Invalid Answer' if not include a json answer in the reply
'''
def extract_model_answer(file_name: str):
    file_path = path.model_ans_path + path.orgin_ans_path + file_name + '.csv'
    output_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    try:
        # Attempt to load the CSV file
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[!] The file {file_path} is not found.")
        return
    except Exception as e:
        print(f"[!] An error occurred while reading the file: {e}")
        return
    try:
        # Attempt to apply a function to the specified column and create a new column for extracted JSON strings
        df['extracted_answer'] = df['model_answer'].apply(utils.extract_json_answer)
        # Attempt to save the modified DataFrame to a new CSV file for review
        df.to_csv(output_path, index=False)
    except Exception as e:
        print(f"[!] An error ocurred when processing the data: {e}")
        return
    print(f"[+] Answer extracted successfully at {output_path}.")


'''
Compared with ground truth, count and mark the extracted answer
target: 'methods' to compare methods or 'columns' to compare relevant columns
'''
def compare_and_count_answer_row(target: str, extracted_answer, ground_truth):
    try:
        # Normalize and parse the model_answer and ground_truth data to ensure consistent formatting
        # Remove issues with extra spaces, newlines, and quotation marks
        model_answer_all = json.loads(extracted_answer)
        model_answer_list = model_answer_all.get(target, [])

        # Parse the ground truth after replacing single quotes with double quotes to ensure valid JSON
        ground_truth_all = json.loads(ground_truth.replace('\'', '"'))
        ground_truth_list = ground_truth_all.get(target, [])
        # Convert both lists of methods to lower case to ensure case-insensitive comparison
        model_answer_list = [method.lower().strip() for method in model_answer_list]
        ground_truth_list = [method.lower().strip() for method in ground_truth_list]

        # Calculate correct, wrong, and missed counts
        correct = len(set(model_answer_list) & set(ground_truth_list))
        wrong = len(set(model_answer_list) - set(ground_truth_list))
        missed = len(set(ground_truth_list) - set(model_answer_list))
        # Construct the comparison result as a JSON string
        comparison_res_str = json.dumps({
            "Correct": correct,
            "Wrong": wrong,
            "Missed": missed
        })
        return comparison_res_str
    except Exception as e:
        return "Invalid Answer"

# Compare and count for the methods' and columns' selection for the whole file
def compare_and_count_answer(file_name: str):
    file_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    output_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    try:
        # Attempt to load the CSV file
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[!] The file {file_path} is not found.")
        return
    except Exception as e:
        print(f"[!] An error occurred while reading the file: {e}")
        return
    # Apply function to each row
    methods_comparison_result = [
        compare_and_count_answer_row(
            target = 'methods',
            extracted_answer=row['extracted_answer'], 
            ground_truth=row['ground_truth'],
        ) 
        for index, row in df.iterrows()
    ]
    columns_comparison_result = [
        compare_and_count_answer_row(
            target = 'columns',
            extracted_answer=row['extracted_answer'], 
            ground_truth=row['ground_truth'],
        ) 
        for index, row in df.iterrows()
    ]
    # Add the comparison results columns
    df['methods_comparison_result'] = methods_comparison_result
    df['columns_comparison_result'] = columns_comparison_result
    # Save the modified dataframe to a new CSV file
    df.to_csv(output_path, index=False)
    print(f"[+] The comparison and count for answers is successfully saved at {file_path}")
    return


'''
**[This function is temporarily deprecated!]
Calculate the accuracy of classification of model answer
This function computes the accuracy by considering only the valid comparison results, excluding 'Invalid Answer'.
'''
def calculate_task_classification_accuracy(file_name: str):
    file_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    df = pd.read_csv(file_path)
    total_rows = df.shape[0]
    # Invalid answer counter
    invalid_answer_count = df[df['comparison_result'] == "Invalid Answer"].shape[0]
    # Filter out rows where comparison_result is not "Invalid Answer"
    valid_results_df = df[df['comparison_result'] != "Invalid Answer"]
    # Valid answer counter
    valid_count = valid_results_df.shape[0]
    # Count the number of correct results (not "Task Misclassified")
    correct_count = valid_results_df[valid_results_df['comparison_result'] != "Task Misclassified"].shape[0]
    # Calculate accuracy
    accuracy = correct_count / valid_count if valid_count > 0 else 0
    accuracy_percentage = "{:.4f}%".format(accuracy * 100)
    output_str = (f"[*] {file_name} - Accuracy of task classification: {accuracy_percentage} "
                  f"\n    (Correct classifications: {correct_count}, "
                  f"Valid answers: {valid_count}, "
                  f"Invalid answers: {invalid_answer_count}, "
                  f"Total rows: {total_rows})")
    return output_str


'''
**[This function is temporarily deprecated!]
Confusion matrix for task classification
Answers beyond the provided range will not be considered valid:
- Ignore these rows when the value of the task key in the extracted_answer column is not within the range of task (standard answer).
'''
def plot_confusion_matrix_for_task_classification(file_name: str, output_dir: str):
    file_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    df = pd.read_csv(file_path)
    # Pre-treatment to filter out valid 'extracted_answer'
    valid_answers = df['extracted_answer'].apply(lambda x: x if x != 'Invalid Answer' else None)
    # Extract the 'task' key value in 'extracted_answer'
    tasks = valid_answers.dropna().apply(lambda x: json.loads(x).get('task', None))
    # Get all possible standard answers and replace them with abbreviations
    df['task'] = df['task'].map(mappings.task_abbreviations)
    possible_tasks = set(df['task'])
    # Filter out the prediction tasks that are within the range of possible tasks
    filtered_tasks = tasks[tasks.apply(lambda x: mappings.task_abbreviations.get(x, None) in possible_tasks)]
    valid_rows = df.loc[filtered_tasks.index]
    # Count the amount of data that was filtered
    filtered_cnt = tasks.shape[0] - filtered_tasks.shape[0]

    # Compare the 'task' column and 'extracted_answer' column
    true_tasks = valid_rows['task']
    predicted_tasks = filtered_tasks.map(mappings.task_abbreviations)
    # Compute confusion matrix
    labels = sorted(possible_tasks)
    cm = confusion_matrix(true_tasks, predicted_tasks, labels=labels)
    # Plot and save picture of confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix', fontsize=14)
    plt.ylabel('Actual Task', fontsize=14)
    plt.xlabel('Answer from LLM', fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout()
    output_file_path = os.path.join(output_dir, file_name + '_confusion_matrix.png')
    plt.savefig(output_file_path, bbox_inches='tight', dpi=300)
    print(f"[+] Confusion matrix chart saved at: {output_file_path}. (Number of filtered rows: {filtered_cnt})")
    return


'''
Calculate scores of answer for each row
target: 'methods' or 'columns'
method_metric: 'jaccard' (Jaccard index) or 'acc' (Accuracy)
Score policy for methods:
- Add one point for each correct, deduct one point for each incorrect, no point for miss.
- If the score is less than 0, it will be recorded as 0.
Score policy for columns:
- Add one point if all correct, otherwise, zero point. Therefore, score ratio for columns equals to accuracy of columns selection.
'''
# Score policy
def model_answer_score_policy(row, target: str, method_metric='jaccard'):
    if target == 'methods':
        target_header = 'methods_comparison_result'
        comparison_result = row[target_header]
        # Check if the comparison_result is a JSON string
        if comparison_result.startswith('{') and comparison_result.endswith('}'):
            try:
                result = json.loads(comparison_result)
                if method_metric == 'jaccard':
                    # Calculate score for methods selection: use Jaccard index, and for each row, the full score is 1.
                    score = result.get('Correct', 0) / (result.get('Correct', 0) + result.get('Wrong', 0) + result.get('Missed', 0))
                elif method_metric == 'acc':
                    # Use accuracy to evaluate the methods selection
                    if (result.get('Correct', 0) > 0 and result.get('Wrong', 0) == 0 and result.get('Missed', 0) == 0):
                        score = 1
                    else:
                        score = 0
            except ValueError:
                # In case of JSON parsing error, score is 0
                score = 0
        else:
            # Task Misclassified and Invalid Answer case
            score = 0
    elif target == 'columns':
        target_header = 'columns_comparison_result'
        comparison_result = row[target_header]
        # Check if the comparison_result is a JSON string
        if comparison_result.startswith('{') and comparison_result.endswith('}'):
            try:
                result = json.loads(comparison_result)
                # Calculate score for columns selection: for each row: all correct and not wrong or missed: 1, otherwise: 0.
                if (result.get('Correct', 0) > 0 and result.get('Wrong', 0) == 0 and result.get('Missed', 0) == 0):
                    score = 1
                else:
                    score = 0
            except ValueError:
                # In case of JSON parsing error, score is 0
                score = 0
        else:
            # Task Misclassified and Invalid Answer case
            score = 0
    else:
        raise ValueError("[!] Invalid target! Should be 'methods' or 'columns'.")
    
    return max(score, 0)  # Ensure score is not negative

# Calculate scores
def calculate_model_answer_score_for_row(file_name: str):
    file_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    df = pd.read_csv(file_path)
    # Apply the function to each row
    df['methods_score'] = df.apply(lambda row: model_answer_score_policy(row, target='methods', method_metric='acc'), axis=1)
    df['columns_score'] = df.apply(lambda row: model_answer_score_policy(row, target='columns', method_metric='acc'), axis=1)
    # Calculate situation of both methods and columns selection are fully correct
    df['selection_overall'] = df.apply(lambda row: 1 if (row['methods_score'] == 1 and row['columns_score'] == 1) else 0, axis=1)
    df.to_csv(file_path, index=False)
    print(f'[+] {file_name} methods and columns score calculated.')
    return df


'''
Analyze scores for each task type
target: 'methods' or 'columns' or 'overall'
Performance file:
- total_full_score: full score of a certian task
- obtained_valid_score: the obtained score of LLM which is valid
- score_rate: results on specific metrics, accuracy for columns selection, accuracy/Jaccard index for methods selection
'''
def analyze_performanece_for_tasks(file_name: str, target: str):
    file_path = path.model_ans_path + path.processed_ans_path + file_name + '.csv'
    df = pd.read_csv(file_path)

    if target == 'methods':
        output_sub_dir = 'Methods Selection/All/'
        # Calculate methods count and full score
        # df['full_score'] = df['ground_truth'].apply(lambda x: len(json.loads(x).get("methods", [])))
        # Use accuracy or Jaccard index to evaluate the methods selection: 1 or 0 point for one row
        df['full_score'] = 1
        df['valid_score'] = df.apply(lambda row: row['methods_score'] if row['methods_comparison_result'] != 'Invalid Answer' else 0, axis=1)
    elif target == 'columns':
        output_sub_dir = 'Columns Selection/All/'
        # For columns selection: 1 or 0 point for one row
        df['full_score'] = 1
        df['valid_score'] = df.apply(lambda row: row['columns_score'] if row['columns_comparison_result'] != 'Invalid Answer' else 0, axis=1)
    elif target == 'overall':
        output_sub_dir = 'Selection Overall/All/'
        # For overall selection, full score is 1 for each row
        df['full_score'] = 1
        df['valid_score'] = df.apply(lambda row: row['selection_overall'] if row['methods_comparison_result'] != 'Invalid Answer' else 0, axis=1)
    else:
        raise ValueError("[!] Invalid target! Should be 'methods' or 'columns' or 'overall.")
    
    output_path = path.model_ans_path + path.task_perf_path + output_sub_dir + target + '-' + file_name + '.csv'
    # Group by task and calculate statistics
    task_stats = df.groupby('task').agg(
        total_full_score=pd.NamedAgg(column='full_score', aggfunc='sum'),
        obtained_valid_score=pd.NamedAgg(column='valid_score', aggfunc='sum')
    ).reset_index()
    task_stats['score_rate'] = round(task_stats['obtained_valid_score'] / task_stats['total_full_score'], 5)
    # Output file path
    task_stats.to_csv(output_path, index=False)
    print(f'[+] {file_name} task performance analyzed and saved to {output_path}')
    return output_path


'''
Process the filename for display in the legend.
Parameters:
- file_path: The path of the file.
'''
def process_filename_for_radar_chart_legend(file_path):
    filename = file_path.split('/')[-1]  # Extract the filename from the path
    processed_name = filename.replace('.csv', '').replace('_', ' ').replace('methods-','').replace('columns-','').replace('overall-','')
    return processed_name


"""
Adjust the font size and weight in the radar chart based on the score.
"""
def adjust_font_in_radar_chart(score, min_size=4, max_size=8):
    score = max(0, min(1, score))
    if score <= 0.09:
        font_weight = 'normal'
    else:
        font_weight = 'bold'
    font_size = int(round(min_size + (max_size - min_size) * score))
    if font_size >= 6:
        font_size = max(font_size, 8)
    return font_size, font_weight


'''
**[This function is temporarily deprecated!]
Analyze summarized task performance information and plot radar chart
Input: work directory containing multiple csv files of task performance to be analyzed.
target: 'methods' or 'columns' or 'overall'
'''
def plot_radar_chart_for_task_performance(work_dir: str, output_name: str, target: str):
    file_list = utils.get_dataset_name_list(work_dir)
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    colors = plt.cm.tab20(np.linspace(0, 1, len(file_list)))
    # Set the maximum score rate as 1.0
    ax.set_ylim(0, 1.0)
    legend_elements = []  # For custom legend
    for file_name, color in zip(file_list, colors):
        task_stats_df = pd.read_csv(work_dir + file_name + '.csv')
        task_stats_df['Task Abbreviation'] = task_stats_df['task'].map(mappings.task_abbreviations)
        task_stats_df['Label'] = task_stats_df['task'].map(
            lambda x: f"{mappings.task_abbreviations[x]} ({x}, {round(task_stats_df[task_stats_df['task'] == x]['score_rate'].values[0] * 100, 2)}%)")
        num_vars = len(mappings.task_abbreviations)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values = task_stats_df['score_rate'].values.flatten().tolist()
        values += values[:1]
        angles += angles[:1]
        # Calculates the area and average metrics
        area = utils.calculate_polygon_area(values[:-1], angles[:-1])
        pentagon_full_area = 5 * 0.5 * math.sin(72 * math.pi / 180)
        st_area = area / pentagon_full_area # standarized area
        avg = utils.calculate_radar_chart_average(values[:-1])
        # Plot
        ax.fill(angles, values, color=color, alpha=0.25)
        ax.plot(angles, values, color=color, linewidth=2, label=file_name.split('/')[-1])
        # Annotate each task score
        for angle, value, task in zip(angles[:-1], values[:-1], task_stats_df['task']):
            ax.annotate(f"{round(value, 2)}", xy=(angle, value), textcoords='offset points', xytext=(0,8),
                        ha='center', va='center', color=color, 
                        # Adjust weight and font size based on score value
                        weight=adjust_font_in_radar_chart(score=round(value, 2), min_size=5, max_size=8)[1], 
                        fontsize=adjust_font_in_radar_chart(score=round(value, 2), min_size=5, max_size=8)[0])
        # Add to legend elements
        label_with_area = f"{process_filename_for_radar_chart_legend(file_name)} (St Area: {round(st_area, 4)}; Avg: {round(avg, 4)})"
        # label_with_area = f"{process_filename_for_radar_chart_legend(file_name)} (Avg: {round(avg, 4)})"
        legend_elements.append(plt.Line2D([0], [0], color=color, label=label_with_area))
    
    # # Task abbreviations and full names for the legend - [If no need for task abbreviation, comment this.]
    # for task, abbreviation in mappings.task_abbreviations.items():
    #     legend_elements.append(plt.Line2D([0], [0], color='black', marker='.', linestyle='None',
    #                                       markersize=12, label=f"{abbreviation}: {task}"))
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(task_stats_df['Task Abbreviation'], fontsize=14)
    # plt.legend(loc='lower right', bbox_to_anchor=(1.5, 0.02))
    plt.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(2.33, -0.1))
    plt.title(f'Performance radar chart in {target} selection', size=16, color='black', y=1.06)
    plt.savefig(path.chart_dir + path.radar_dir + f"{output_name}-radar chart for {target} selection.png", bbox_inches='tight', dpi=300)
    print(f"[+] {output_name}-radar chart for {target} selection.png saved to " + path.chart_dir)
    

'''
Integrate anaysis
'''
def model_answer_integrate_analysis(answer_file_name: str):
    # Extract ground truth of methods' selection in dataset
    answer_file_path = path.model_ans_path + path.orgin_ans_path + answer_file_name + '.csv'
    utils.extract_ground_truth(file_path=answer_file_path)
    # Extract json answer from model reply
    extract_model_answer(file_name=answer_file_name)
    # Compare and count answer
    compare_and_count_answer(file_name=answer_file_name)
    print("[i] Answer extraction, comparison and counting completed!")
    # # Plot confusion matrix for task classification
    # plot_confusion_matrix_for_task_classification(file_name=answer_file_name, output_dir=(path.chart_dir+path.confusion_matrix_dir))
    # Calculate scores
    calculate_model_answer_score_for_row(file_name=answer_file_name)
    # Analyze task performance
    analyze_performanece_for_tasks(file_name=answer_file_name, target='methods')
    analyze_performanece_for_tasks(file_name=answer_file_name, target='columns')
    analyze_performanece_for_tasks(file_name=answer_file_name, target='overall')
    
    # # Calculate model answer accuracy
    # print('---------------------------------------------------------------------------------')
    # print('Task Classification Accuracy:')
    # print(calculate_task_classification_accuracy(file_name=answer_file_name))
    # print('---------------------------------------------------------------------------------')


# main
if __name__ == "__main__":

    # Model answer analysis
    # model_answer_integrate_analysis(answer_file_name='random')

    # # llama Few-shot
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_one-shot')
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_two-shot')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_one-shot')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_two-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_one-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_two-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_one-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_two-shot')
    
    # # llama CoT
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_one-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_one-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_one-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_one-shot-CoT')

    # # GPT
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_one-shot')
    # model_answer_integrate_analysis(answer_file_name='gpt-4_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='gpt-4_one-shot')
    # model_answer_integrate_analysis(answer_file_name='gpt-4o_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='gpt-4o_one-shot')

    # llama CoT
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_one-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='gpt-4_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='gpt-4_one-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='gpt-4o_zero-shot-CoT')
    # model_answer_integrate_analysis(answer_file_name='gpt-4o_one-shot-CoT')


    # # SFT
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_sft_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_sft_zero-shot')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_sft_zero-shot')
    
    # Human
    # model_answer_integrate_analysis(answer_file_name='human_Stats Background_Closed-book')
    # model_answer_integrate_analysis(answer_file_name='human_Non-Stats Background_Closed-book')
    # model_answer_integrate_analysis(answer_file_name='human_Stats Background_Open-book')
    # model_answer_integrate_analysis(answer_file_name='human_Non-Stats Background_Open-book')
    # model_answer_integrate_analysis(answer_file_name='human_Stats Background_GPT-assisted')
    # model_answer_integrate_analysis(answer_file_name='human_Non-Stats Background_GPT-assisted')

    # # LLMs with stats prompt
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='gpt-4_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='gpt-4o_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='llama2_7b_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='llama2_13b_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_instruct_stats-prompt')
    # model_answer_integrate_analysis(answer_file_name='llama3_8b_stats-prompt')
    
    # # LLMs with stats prompt and explain
    # model_answer_integrate_analysis(answer_file_name='gpt-3.5-turbo_stats-prompt-explain')

    pass