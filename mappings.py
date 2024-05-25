# -*- coding: gbk -*-

# Mapping dataset names to statistical tasks
dataset_task_mapping = {
    'Chi-square and fisher exact test info extraction (Independent)': 'Contingency Table Test',
    'Chi-square and fisher exact test info extraction (Not independent)': 'Contingency Table Test',
    'Mantel Haenszel test info extraction (Not independent)': 'Contingency Table Test',
    'Mantel Haenszel test info extraction (Independent)': 'Contingency Table Test',
    'Correlation analysis info extraction (Not strongly correlated)': 'Correlation Analysis',
    'Correlation analysis info extraction (Strongly correlated)': 'Correlation Analysis',
    'Partial correlation info extraction (Strongly correlated)': 'Correlation Analysis',
    'Partial correlation info extraction (Not strongly correlated)': 'Correlation Analysis',
    'Descriptive statistics info extraction': 'Descriptive Statistics',
    'KS distribution comparison info extraction (Distribution not significantly different)': 'Distribution Compliance Test',
    'KS distribution comparison info extraction (Distribution significantly different)': 'Distribution Compliance Test',
    'Normality test info extraction (Non-normally distributed)': 'Distribution Compliance Test',
    'Normality test info extraction (Normally distributed)': 'Distribution Compliance Test',
    'Other distribution info extraction (Compliance)': 'Distribution Compliance Test',
    'Other distribution info extraction (Not compliance)': 'Distribution Compliance Test',
    'Variance test info extraction (Variance not significantly different)': 'Variance Test',
    'Variance test info extraction (Variance significantly different)': 'Variance Test'
}

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

# Mapping of task names to their abbreviations
task_abbreviations = {
    'Correlation Analysis': 'CA',
    'Distribution Compliance Test': 'DCT',
    'Contingency Table Test': 'CTT',
    'Descriptive Statistics': 'DS',
    'Variance Test': 'VT'
}

# Mapping of method names to their abbreviations
method_abbreviations = {
    'Pearson Correlation Coefficient': 'PCC',
    'Spearman Correlation Coefficient': 'SCC',
    'Kendall Correlation Coefficient': 'KCC',
    'Partial Correlation Coefficient': 'PaCC',
    'Anderson-Darling Test': 'ADT',
    'Shapiro-Wilk Test of Normality': 'SWT',
    'Kolmogorov-Smirnov Test for Normality': 'KST-N',
    'Lilliefors Test': 'LiT',
    'Kolmogorov-Smirnov Test': 'KST',
    'Kolmogorov-Smirnov Test for Uniform distribution': 'KST-U',
    'Kolmogorov-Smirnov Test for Gamma distribution': 'KST-G',
    'Kolmogorov-Smirnov Test for Exponential distribution': 'KST-E',
    'Chi-square Independence Test': 'CIT',
    'Fisher Exact Test': 'FET',
    'Mantel-Haenszel Test': 'MHT',
    'Mean': 'Mean',
    'Median': 'Med',
    'Mode': 'Mode',
    'Range': 'Range',
    'Quartile': 'Quart',
    'Standard Deviation': 'SD',
    'Skewness': 'Skew',
    'Kurtosis': 'Kurt',
    'Mood Variance Test': 'MoVT',
    'Levene Test': 'LeT',
    'Bartlett Test': 'BT',
    'F-Test for Variance': 'FTV'
}

# Mapping of methods' name to api function name
method_api_mapping = {
    'Pearson Correlation Coefficient': 'pearson_correlation_coefficient',
    'Spearman Correlation Coefficient': 'spearman_correlation_coefficient',
    'Kendall Correlation Coefficient': 'kendall_correlation_coefficient',
    'Partial Correlation Coefficient': 'partial_correlation_coefficient',
    'Anderson-Darling Test': 'anderson_darling_test',
    'Shapiro-Wilk Test of Normality': 'shapiro_wilk_test_for_normality',
    'Kolmogorov-Smirnov Test for Normality': 'kolmogorov_smirnov_test_for_normality',
    'Lilliefors Test': 'lilliefors_test',
    'Kolmogorov-Smirnov Test': 'kolmogorov_smirnov_test',
    'Kolmogorov-Smirnov Test for Uniform distribution': 'kolmogorov_smirnov_test_for_uniform_distribution',
    'Kolmogorov-Smirnov Test for Gamma distribution': 'kolmogorov_smirnov_test_for_gamma_distribution',
    'Kolmogorov-Smirnov Test for Exponential distribution': 'kolmogorov_smirnov_test_for_expoential_distribution',
    'Chi-square Independence Test': 'chi_square_independence_test',
    'Fisher Exact Test': 'fisher_exact_test',
    'Mantel-Haenszel Test': 'mantel_haenszel_test',
    'Mean': 'mean',
    'Median': 'median',
    'Mode': 'mode',
    'Range': 'range',
    'Quartile': 'quartile',
    'Standard Deviation': 'standard_deviation',
    'Skewness': 'skewness',
    'Kurtosis': 'kurtosis',
    'Mood Variance Test': 'mood_variance_test',
    'Levene Test': 'levene_test',
    'Bartlett Test': 'bartlett_test',
    'F-Test for Variance': 'f_test_for_variance'
}
