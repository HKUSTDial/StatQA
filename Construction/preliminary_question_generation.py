# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import pandas as pd
import random
import numpy as np
import question_templates as qt
import path


''' 
Generate preliminary questions based on parameters (Selected column 1 and 2, or a single column)
sample_num: select templates to generate several questions for each line
'''
def generate_preliminary_question(file_name: str, templates: list, column1_name: str, column2_name: str=None, column3_name: str=None, sample_num: int=3):
    try:
        # file_path = path.info_dir + path.manual_dir + file_name + '.csv'
        file_path = path.info_dir + file_name + '.csv'
        output_path = path.info_dir + path.prequestion_dir + file_name + '_withPreliminaryQuestions.csv'
        # read csv file
        df = pd.read_csv(file_path)
        # # Create the new column 'question', create the question based on random choice of templates
        # df['question'] = df.apply(lambda row: random.choice(templates).format(**row), axis=1)

        # Ensure there are at least sample_num templates to choose from
        if len(templates) < sample_num:
            raise ValueError("[!] Template list must contain at least " + str(sample_num) + " templates.")

        # Function to generate sample_num unique questions
        def generate_questions(row):
            chosen_templates = random.sample(templates, sample_num)
            return [template.format(**row) for template in chosen_templates]

        # Apply the function to each row and create a new DataFrame with expanded rows
        questions = df.apply(generate_questions, axis=1).explode()
        expanded_df = df.loc[df.index.repeat(sample_num)].reset_index(drop=True)
        expanded_df['question'] = questions.array

        # Output
        expanded_df.to_csv(output_path, index=False)

        # Output
        # df.to_csv(output_path, index=False)
        print('[+] ' + file_name + ' Questions generated successfully!')
    except FileNotFoundError:
        print(f"[!] Error: File not found at path {file_path}")
    except pd.errors.EmptyDataError:
        print(f"[!] Error: The file at path {file_path} is empty.")
    except pd.errors.ParserError:
        print(f"[!] Error: Unable to parse the CSV file at path {file_path}.")
    except ValueError as ve:
        print(f"[!] Error: {ve}")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
    return


# main
if __name__=='__main__':
    # Call the function and pass in the corresponding parameters
    # generate_preliminary_question(file_name='Test', column1_name='Column 1', column2_name='Column 2')

    # Refer to extracted information and set the sample_num to make the dataset more balanced

    # Generate preliminary questions for correlation analysis (exclude partial correaltion)
    generate_preliminary_question(sample_num=5, file_name='Correlation analysis info extraction (Strongly correlated)', column1_name='Column 1', column2_name='Column 2', templates=qt.correlation_analysis_templates)
    generate_preliminary_question(sample_num=5, file_name='Correlation analysis info extraction (Not strongly correlated)', column1_name='Column 1', column2_name='Column 2', templates=qt.correlation_analysis_templates)

    # Generate preliminary questions for correlation analysis (partial correlation) 
    generate_preliminary_question(sample_num=1, file_name='Partial correlation info extraction (Strongly correlated)', column1_name='Column 1', column2_name='Column 2', column3_name='Control Column', templates=qt.partial_correlation_analysis_templates)
    generate_preliminary_question(sample_num=1, file_name='Partial correlation info extraction (Not strongly correlated)', column1_name='Column 1', column2_name='Column 2', column3_name='Control Column', templates=qt.partial_correlation_analysis_templates)
    
    # Generate preliminary questions for contingency table test (chi-square and fisher)
    generate_preliminary_question(sample_num=10, file_name='Chi-square and fisher exact test info extraction (Independent)', column1_name='Column 1', column2_name='Column 2', templates=qt.contingency_table_test_templates)
    generate_preliminary_question(sample_num=8, file_name='Chi-square and fisher exact test info extraction (Not independent)', column1_name='Column 1', column2_name='Column 2', templates=qt.contingency_table_test_templates)
    
    # Generate preliminary questions for normality distibuton test
    generate_preliminary_question(sample_num=12, file_name='Normality test info extraction (Normally distributed)', column1_name='Column', templates=qt.nomal_distribution_test_templates)
    generate_preliminary_question(sample_num=5, file_name='Normality test info extraction (Non-normally distributed)', column1_name='Column', templates=qt.nomal_distribution_test_templates)

    # Generate preliminary questions for Kolmogorov-Smirnov distibuton comparison test
    generate_preliminary_question(sample_num=6, file_name='KS distribution comparison info extraction (Distribution not significantly different)', column1_name='Column 1', column2_name='Column 2', templates=qt.ks_distribution_comparison_templates)
    generate_preliminary_question(sample_num=3, file_name='KS distribution comparison info extraction (Distribution significantly different)', column1_name='Column 1', column2_name='Column 2', templates=qt.ks_distribution_comparison_templates)

    # Generate preliminary questions for other distribution compliance test 
    generate_preliminary_question(sample_num=3, file_name='Other distribution info extraction (Not compliance)', column1_name='Column', column2_name='Distribution', templates=qt.other_distribution_compliance_templates)
    generate_preliminary_question(sample_num=5, file_name='Other distribution info extraction (Compliance)', column1_name='Column', column2_name='Distribution', templates=qt.other_distribution_compliance_templates)

    # Generate preliminary questions for variance test
    generate_preliminary_question(sample_num=15, file_name='Variance test info extraction (Variance not significantly different)', column1_name='Column 1', column2_name='Column 2', templates=qt.variance_test_templates)
    generate_preliminary_question(sample_num=5, file_name='Variance test info extraction (Variance significantly different)', column1_name='Column 1', column2_name='Column 2', templates=qt.variance_test_templates)

    # Generate preliminary questions for Mantel-Haenszel test
    generate_preliminary_question(sample_num=4, file_name='Mantel Haenszel test info extraction (Independent)', column1_name='Column 1', column2_name='Column 2', column3_name='Strata Column', templates=qt.mantel_haenszel_test_templates)
    generate_preliminary_question(sample_num=4, file_name='Mantel Haenszel test info extraction (Not independent)', column1_name='Column 1', column2_name='Column 2', column3_name='Strata Column',templates=qt.mantel_haenszel_test_templates)

    print('Preliminary question (exclude descriptive stats) generated.')
