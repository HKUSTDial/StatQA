# -*- coding: gbk -*-
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import json
import path
import numpy as np
from matplotlib.colors import to_rgba
from mappings import *

file_name = 'StatQA'
file_path = path.integ_dataset_path + path.balance_path + file_name + '.csv'
data = pd.read_csv(file_path)

# Figure name
figure_name = file_name + ' - Dataset feature and distribution'


# Define the inner ring color
task_colors = {
    'Correlation Analysis': '#fecccb',  # light red
    'Distribution Compliance Test': '#bed9ee',  # light blue
    'Contingency Table Test': '#c4dfb2',  # light green
    'Descriptive Statistics': '#f0daef',  # light purple
    'Variance Test': '#fed9a6'  # light orange
}


# Adaptive text size based on sector size
def adjust_text_size_inner(sizes, min_size=10, max_size=14):
    size_range = max_size - min_size
    max_size = max(sizes)
    text_sizes = []
    for size in sizes:
        new_size = min_size + (size / max_size) * size_range
        # if new_size >= min_size - 1:
        #     new_size = 16
        text_sizes.append(new_size)
    return text_sizes

def adjust_text_size_outer(sizes, min_size=10, max_size=14):
    size_range = max_size - min_size
    max_size = max(sizes)
    text_sizes = []
    for size in sizes:
        new_size = min_size + (size / max_size) * size_range
        if new_size <= min_size:
            new_size = 5
        text_sizes.append(new_size)
    return text_sizes


# Initialize the list of the full names of the outer rings used for the legend
outer_legend_labels = []

# Counter for tasks and methods
task_counts = data['task'].value_counts()  # Use absolute frequency for tasks
total_task_count = task_counts.sum()

# Prepare the plot data
# inner ring
inner_sizes = task_counts.values
inner_labels = [f"{task_abbreviations.get(task, task)}\n{count/total_task_count:.1%}" for task, count in zip(task_counts.index, task_counts.values)]
inner_colors = [task_colors.get(task, '#999999') for task in task_counts.index]
# outer ring
outer_sizes = []
outer_labels = []
outer_colors = []

# Calculate the angle and cumulative angle of each task in the inner circle
angle_per_task = {task: 360 * count for task, count in task_counts.items()}
cumulative_angles = 360
start_angle = 140  # starting angle


for task in task_counts.index:
    task_data = data[data['task'] == task]
    methods_json = task_data['results'].apply(json.loads)
    # Calculate the number of each method if applicable
    method_applicable_counts = {}
    for methods in methods_json:
        for method in methods:
            if method['conclusion'] != "Not applicable":
                method_name = method['method']
                method_applicable_counts[method_name] = method_applicable_counts.get(method_name, 0) + 1
    
    # Get the total number of applicable method for the current task
    total_applicable_methods = sum(method_applicable_counts.values())
    # Calculate angles and colors for each method
    for method, m_count in method_applicable_counts.items():
        method_angle = (m_count / total_applicable_methods) * (task_counts[task] / task_counts.sum() * 360)
        outer_sizes.append(method_angle)
        outer_labels.append(method_abbreviations[method])
        outer_colors.append(task_colors.get(task, '#999999'))
        # Add to the legend
        # outer_legend_labels.append(f"{method_abbreviations[method]} (Method): {method} ({m_count})")
        method_to_show = method.replace('distribution', 'distr.').replace('Exponential', 'Exp.').replace('Uniform', 'Uni.').replace('Gamma', 'Gam.')
        outer_legend_labels.append(f"{method_abbreviations[method]}: {method_to_show} ({m_count})")
        

# Convert colors to RGBA format and add transparency to outer ring colors
outer_colors_alpha = [to_rgba(color, alpha=0.6) for color in outer_colors]

# Inner and outer text size list
inner_text_sizes = adjust_text_size_inner(inner_sizes, min_size=20, max_size=20)
outer_text_sizes = adjust_text_size_outer(outer_sizes, min_size=14, max_size=18)


# Draw chart for dataset distribution
fig, ax = plt.subplots()

# Plot inner ring
inner_pie = ax.pie(inner_sizes, radius=1.6, colors=inner_colors, labeldistance=0.9,
                   wedgeprops=dict(width=0.9, edgecolor='w'), startangle=start_angle)

# Sets the position of the inner ring label
for i, (wedge, label) in enumerate(zip(inner_pie[0], inner_labels)):
    angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1 # Calculate the angle of the center of each sector
    x = 1.15 * np.cos(np.deg2rad(angle)) # Adjust the radius to fit
    y = 1.15 * np.sin(np.deg2rad(angle)) # Adjust the radius to fit
    ax.text(x, y, label, ha='center', va='center', fontsize=inner_text_sizes[i])

# Plot outer ring
outer_pie = ax.pie(outer_sizes, radius=2.4, colors=outer_colors_alpha, wedgeprops=dict(width=0.8, edgecolor='w'), startangle=start_angle)

# Set the position and orientation of the outer ring label text
for i, wedge in enumerate(outer_pie[0]):
    angle = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
    x = 2.0 * np.cos(np.deg2rad(angle))
    y = 2.0 * np.sin(np.deg2rad(angle))
    # Determine the rotation angle of the label text
    # Adjust the angle so that the text always points downwards
    if 90 < angle < 270:
        text_rotation = angle - 180
    else:
        text_rotation = angle
    # If the angle > 180, the text direction needs to be further adjusted to ensure it is facing downwards
    if text_rotation > 180:
        text_rotation -= 360
    ax.text(x, y, outer_labels[i], ha='center', va='center', fontsize=outer_text_sizes[i], rotation=text_rotation, rotation_mode='anchor')


'''
Plot and save dataset distribution double layer donut chart
'''
# Add a task legend
# task_legend_labels = [f"{task_abbreviations.get(task, task)} (Task): {task} ({count}/{total_task_count}, {count/total_task_count:.1%})" for task, count in task_counts.items()]
task_legend_labels = [f"{task_abbreviations.get(task, task)} (Task): {task} ({count}/{total_task_count})" for task, count in task_counts.items()]
plt.legend(task_legend_labels + outer_legend_labels, 
           # title="Tasks and Methods", 
           loc="center left", 
           prop = {'size': 20}, 
           bbox_to_anchor=(1.55, 0, 0.5, 1),
           ncol=2)
# plt.show()
plt.savefig(path.chart_dir + 'Dataset Notable Statistics/' + figure_name + ".pdf", format='pdf', bbox_inches='tight', dpi=600)
print("[+] "+ figure_name +".png has been saved to " + path.chart_dir + '.')


'''
Save the distribution information to a csv file
'''
all_legend_labels = task_legend_labels + outer_legend_labels
# Split each label into the abbreviation, full name, and count/percentage
legend_data = [label.split(": ") for label in all_legend_labels]
legend_data = [[item[0].split(" (")[0], item[1].rsplit(" (", 1)[0], item[1].rsplit(" (", 1)[1].strip(")")] for item in legend_data]
# Convert to DataFrame
legend_df = pd.DataFrame(legend_data, columns=['Abbreviation', 'Full Name', 'Count/Percentage'])
# Save to CSV
table_name = file_name + ' - Dataset distribution table.csv'
legend_df.to_csv(path.chart_dir + 'Dataset Notable Statistics/' + table_name, index=False)
print("[+] "+ table_name + " has been saved to " + path.chart_dir + '.')


'''
Calculate and plot difficulty distribution
'''
# Progressing with the difficulty data
difficulty_counts = data['difficulty'].value_counts()
# Calculate percentages
percentage = 100.0 * difficulty_counts / difficulty_counts.sum()
difficulty_colors = ['#fbb4ae', '#b3cde3', '#ccebc5']
fig, ax = plt.subplots(figsize=(10, 8))
scenes, _ = ax.pie(difficulty_counts, startangle=140, colors=difficulty_colors)

# Set labels with category and percentage
labels = ['{0} ({1:.1f}%)'.format(i, j) for i, j in zip(difficulty_counts.index, percentage)]
# Adjust text sizes
text_sizes = adjust_text_size_outer(difficulty_counts, min_size=14, max_size=20)

# For each wedge, create a label at an appropriate angle inside the pie.
for i, p in enumerate(scenes):
    angle = (p.theta2 - p.theta1)/2. + p.theta1
    x = 0.5 * np.cos(np.deg2rad(angle))
    y = 0.5 * np.sin(np.deg2rad(angle))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    ax.text(x, y, labels[i], ha='center', va='center', fontsize=text_sizes[i])

ax.axis('equal')
# Legend with category, percentage, and count
legend_labels = ['{0} ({1:.1f}%, {2})'.format(i,j,k) for i,j,k in zip(difficulty_counts.index, percentage, difficulty_counts)]
plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Difficulty", labels=legend_labels, prop={'size': 10})
plt.title('Difficulty Distribution', fontsize=18)
plt.savefig(path.chart_dir + 'Dataset Notable Statistics/' +  file_name + " - Difficulty Distribution.png", bbox_inches='tight', dpi=300)
print(f"[+] {file_name} - Difficulty Distribution chart saved to " + path.chart_dir)