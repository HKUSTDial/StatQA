# -*- coding: gbk -*-
import sys
import os

from matplotlib.lines import Line2D
current_path = os.path.dirname(__file__)
main_directory = os.path.abspath(os.path.join(current_path, '..', '..'))
sys.path.append(main_directory)


import math
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
Process the filename for display in the legend.
Parameters:
- file_path: The path of the file.
'''
def process_filename_for_radar_chart_legend(file_path):
    filename = file_path.split('/')[-1]  # Extract the filename from the path
    processed_name_1 = filename.replace('.csv', '').replace('_', ' ').replace('methods-','').replace('columns-','').replace('overall-','')
    processed_name_2 = processed_name_1.replace('zero', '0').replace('one', '1').replace('two', '2').replace('Non-Stats Background', 'Non-Stats').replace('Stats Background', 'Stats').replace('instruct', 'inst').replace('gpt-3.5-turbo', 'ChatGPT').replace('gpt-4', 'GPT-4')
    processed_name_3 = processed_name_2.replace(' stats-prompt', '').replace(' 1-shot-CoT', '').replace(' 0-shot', '').replace(' Open-book', '')
    return processed_name_3


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
    font_size = 0
    font_weight = 'normal'
    return font_size, font_weight


'''
Analyze summarized task performance information and plot radar chart
'''
def plot_radar_chart_from_summary(csv_file_path: str, output_name: str, custom_colors=None, titles=None):
    # Load the CSV file
    data = pd.read_csv(csv_file_path, skip_blank_lines=False)
    
    # Identify blocks by empty rows
    block_indices = data.index[data.isna().all(axis=1)].tolist()
    block_starts = [0] + [index + 1 for index in block_indices]
    block_ends = block_indices + [len(data)]
    
    # Number of blocks (subplots)
    num_blocks = len(block_starts)
    
    # Setup figure and axes
    fig, axes = plt.subplots(1, num_blocks, figsize=(4 * num_blocks, 4), subplot_kw=dict(polar=True))
    if num_blocks == 1:
        axes = [axes]  # Ensure axes is always a list for consistency in single plot scenarios
    
    # Determine global color mapping for models across all blocks
    unique_models = pd.concat([data.iloc[start:end].dropna()['model'] for start, end in zip(block_starts, block_ends)]).unique()
    if custom_colors and len(custom_colors) >= len(unique_models):
        color_map = {model: custom_colors[i] for i, model in enumerate(unique_models)}
    else:
        color_map = {model: plt.cm.tab20(i / len(unique_models)) for i, model in enumerate(unique_models)}

    # Iterate over each block to create radar charts
    for i, (start, end) in enumerate(zip(block_starts, block_ends)):
        block_df = data.iloc[start:end].dropna()  # Select block and drop any NaN rows
        ax = axes[i]
        # Set the title for each subplot
        if titles and len(titles) > i:
            ax.text(0.5, -0.15, titles[i], transform=ax.transAxes, ha='center', va='center', fontsize=20)

        # Plot each model in the block
        for index, row in block_df.iterrows():
            model_name = row['model']
            scores = row[2:]  # Assuming scores start from the third column
            # tasks = scores.index.tolist()
            tasks = [mappings.task_abbreviations[task] if task in mappings.task_abbreviations else task for task in scores.index.tolist()]
            num_vars = len(tasks)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist() + [0]

            values = scores.values.tolist() + [scores.values[0]]
            color = color_map[model_name]

            ax.fill(angles, values, color=color, alpha=0.2)
            ax.plot(angles, values, color=color, linewidth=2, label=model_name)

        # Custom settings for each axis
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(tasks, fontsize=16)
        ax.set_ylim(0, 1)

    # Global legend
    # legend_elements = [Patch(facecolor=color_map[model], label=model) for model in unique_models]
    legend_elements = [Line2D([0], [0], color=color_map[model], linewidth=2.5, label=process_filename_for_radar_chart_legend(model)) for model in unique_models]
    fig.legend(handles=legend_elements, 
               loc='center right', 
               bbox_to_anchor=(1.28, 0.5), 
               fontsize=20)

    # Save the figure
    plt.tight_layout()
    plt.savefig(f"Chart\Radar Chart\{output_name} radar chart.pdf", format='pdf', bbox_inches='tight', dpi=300)
    print(f"[+] Radar charts saved as {output_name}_radar_charts.pdf")


# main
if __name__ == '__main__':
    # custom_colors = ['#ffb8b8', '#D6A2E8', '#1B9CFC', '#48dbfb', '#98df8a', '#badc58', '#6ab04c','#8c7ae6', '#38ada9', '#fd9644', '#fdcb6e', '#ff6b81']
    custom_colors = ['#95a5a6',
                     '#f8a5c2',
                     '#1B9CFC', 
                     '#1dd1a1', 
                     '#8c7ae6', 
                     '#fd9644', 
                     '#38ada9', 
                     '#fdcb6e', 
                     '#eb6a82'] 
    subtitle_list = ["(a) LLaMA-2/3", "(b) GPT Models", "(c) Best in Each Section"]
    plot_radar_chart_from_summary('Model Answer\Task Performance\Selected Performance\selected_overall.csv', 'Leading model overall', custom_colors, titles=subtitle_list)