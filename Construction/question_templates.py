# Define question templates

'''
For statistical test tasks
Correation analysis, Distribution compliance test, Variance test, Contingency table test
'''

# Correlation analysis question templates (except Partial correlation coefficent)
# 2 Columns
correlation_analysis_templates = [
    'Is there a correlation between {Column 1} and {Column 2}?',
    'How strong is the correlation between {Column 1} and {Column 2}?',
    'Do changes in {Column 1} relate to changes in {Column 2}?',
    'Are {Column 1} and {Column 2} related in any way?',
    'Is the relationship between {Column 1} and {Column 2} consistent?',
    'Are variations in {Column 1} associated with variations in {Column 2}?',
    'How do changes in {Column 1} correlate with changes in {Column 2}?',
    'Is there a direct relationship between {Column 1} and {Column 2}?',
    'Are there any correlations between {Column 1} and {Column 2} over time?',
    'Is there a linear relationship between {Column 1} and {Column 2}?',
    'How closely do {Column 1} and {Column 2} follow a straight-line relationship?',
    'Are movements in {Column 1} reflected similarly in {Column 2}?',
    'How consistent is the relationship between {Column 1} and {Column 2}?',
    'Is the connection between {Column 1} and {Column 2} strong?',
    'Are {Column 1} and {Column 2} correlated with each other in a linear manner?',
    'How does the direction of change in {Column 1} relate to {Column 2}?',
    'Do {Column 1} and {Column 2} show any linear correlation?',
    'Do patterns observed in {Column 1} similarly appear in {Column 2}?'
]

# Correlation analysis question templates for partial correlation coefficent
# 3 Columns (Column 1, 2, and Control Column)
partial_correlation_analysis_templates = [
    'How does {Column 1} correlate with {Column 2} when {Control Column} is held constant?',
    'After controlling for {Control Column}, what is the relationship between {Column 1} and {Column 2}?',
    'After factoring in {Control Column}, how do {Column 1} and {Column 2} interact?',
    'Is there a significant link between {Column 1} and {Column 2} when controlling for {Control Column}?',
    'How does controlling for {Control Column} change the relationship between {Column 1} and {Column 2}?',
    'With {Control Column} controlled, what is the correlation strength between {Column 1} and {Column 2}?',
    'After neutralizing the effect of {Control Column}, how do {Column 1} and {Column 2} relate to each other?',
    'What is the partial correlation between {Column 1} and {Column 2} considering {Control Column}?',
    'When {Control Column} is fixed, how do {Column 1} and {Column 2} correlate?',
    'After {Control Column} is controlled for, what remains the relationship between {Column 1} and {Column 2}?',
    'What is the impact of {Column 1} on {Column 2} with {Control Column} taken into consideration?',
    'How does the relationship between {Column 1} and {Column 2} manifest when isolating {Control Column}?',
    'With the influence of {Control Column} removed, how are {Column 1} and {Column 2} related?',
    'What connection exists between {Column 1} and {Column 2} upon controlling for {Control Column}?',
    'After minimizing the influence of {Control Column}, what correlation exists between {Column 1} and {Column 2}?',
    'What is the nature of the relationship between {Column 1} and {Column 2} after {Control Column} is considered?',
]

# Contingency table test question templates (Chi-square and Fisher)
# 2 Columns
contingency_table_test_templates = [
    'Is there a correlation between {Column 1} and {Column 2}?',
    'Are {Column 1} independent of {Column 2}?',
    'Among {Column 1} and {Column 2}, does the observed frequency conform to the independence assumption?',
    'Do changes in {Column 1} correspond to changes in {Column 2}?',
    'Can a relationship between {Column 1} and {Column 2} be observed in the data?',
    'Does {Column 1} show any dependency with {Column 2}?',
    'Are variations in {Column 1} associated with variations in {Column 2}?',
    'Is there any indication of a link between {Column 1} and {Column 2}?',
    'Are there any patterns between {Column 1} and {Column 2} that suggest a relationship?',
    'Does the presence of specific categories in {Column 1} influence the distribution in {Column 2}?',
    'Is there a discernible interaction between {Column 1} and {Column 2}?',
    'Does {Column 1} and {Column 2} have a mutual impact on their frequency?',
    'Does the data suggest that {Column 1} and {Column 2} are related?',
    'How are the categories of {Column 1} reflected in the frequency of {Column 2}?',
    'Can we see a clear association pattern between {Column 1} and {Column 2}?',
    'Is there an evident dependency between the classifications of {Column 1} and {Column 2}?',
    'Are the frequency observed in {Column 1} mirrored in the changes in {Column 2}?'
]

# Contingency table test question templates (Mantel-Haenszel Test)
# 2 Columns to be analyzed and 1 strata column
mantel_haenszel_test_templates = [
    'Is there a significant difference in the impact of {Column 1} on {Column 2} across different levels of {Strata Column}?',
    'Considering different levels of {Strata Column}, does the influence of {Column 1} on {Column 2} remain consistent across different strata?',
    'Does the relationship between {Column 1} and {Column 2} differ significantly when stratified by {Strata Column}?',
    'In the context of different {Strata Column} levels, is the association between {Column 1} and {Column 2} stable?',
    'Are there variations in the effect of {Column 1} on {Column 2} when analyzed across various categories of {Strata Column}?',
    'How does the impact of {Column 1} on {Column 2} change when considering the different segments of {Strata Column}?',
    'Is the interaction between {Column 1} and {Column 2} influenced by the stratification based on {Strata Column}?',
    'Across the distinct levels of {Strata Column}, does the correlation between {Column 1} and {Column 2} remain uniform?',
    'When accounting for {Strata Column}, is there a noticeable fluctuation in how {Column 1} affects {Column 2}?',
    'Considering the stratification by {Strata Column}, is the linkage between {Column 1} and {Column 2} subject to variation?',
    'Do the levels of {Strata Column} play a role in modifying the relationship between {Column 1} and {Column 2}?',
    'In the framework of {Strata Column} stratification, does the influence of {Column 1} on {Column 2} show differential patterns?'
]

# Normal distribution compliance test templates
# 1 Column
nomal_distribution_test_templates = [
    'Does the distribution of {Column} follow a normal curve?',
    'Does {Column} follow a normal distribution?',
    'Can I assume normality in {Column} for statistical procedures?',
    'Is there evidence against {Column} being normally distributed?',
    'Do the values in {Column} exhibit characteristics of a normal distribution?',
    'Is the distribution of {Column} close enough to normal for practical purposes?',
    'How does the distribution of {Column} compare to a theoretical normal distribution?',
    'What are the implications if {Column} is not normally distributed?',
    'Is {Column} suitable for methods assuming normality?',
    'How likely is it that {Column} comes from a normal distribution?',
    'Is the {Column} consistent with a normal distribution?',
    'How can I visually assess if {Column} is normally distributed?',
    'How robust is the normality assumption for {Column}?'
]

# KS distribution comparison test templates
# 2 Columns
ks_distribution_comparison_templates = [
    'Are the distributions of {Column 1} and {Column 2} similar?',
    'Do {Column 1} and {Column 2} follow the similar distribution curve?',
    'Are there observable differences in the distribution shapes of {Column 1} and {Column 2}?',
    'How do the cumulative distributions of {Column 1} and {Column 2} compare?',
    'How similar are the distribution of {Column 1} and {Column 2}?',
    'Can the Kolmogorov-Smirnov test reveal any disparities between the distributions of {Column 1} and {Column 2}?',
    'Do the distribution profiles of {Column 1} and {Column 2} differ significantly?',
    'Are the distributions of {Column 1} and {Column 2} closely aligned?',
    'How to assess the alignment of distributions in {Column 1} and {Column 2}?',
    'Is there a notable discrepancy in the distribution frequency of {Column 1} versus {Column 2}?',
    'Can we infer distributional equivalence of {Column 1} and {Column 2}?',
    'Are the data distributions in {Column 1} and {Column 2} statistically indistinguishable?',
    'What is the extent of distributional similarity of {Column 1} and {Column 2}?',
    'Is there a statistically significant difference in the data distribution of {Column 1} compared to {Column 2}?'
]

# other distribution compliance test templates
# 2 Columns
# Column 1: title of the selected data column
# Column 2: the test method (Exponential/Uniform/Gamma)
other_distribution_compliance_templates = [
    'Whether the data of {Column} is subject to {Distribution} distribution?',
    'Does {Column} conform to a {Distribution} distribution?',
    'Is {Column} demonstrating as {Distribution} distribution?'
    'Is the {Distribution} distribution a good fit for {Column} data?',
    'Does it proper to model the data of {Column} by a {Distribution} distribution?',
    'Do the data in {Column} exhibit a {Distribution} distribution?',
    'Is the {Distribution} distribution a suitable representation for the data in {Column}?',
    'Does the data distribution of {Column} comply with the {Distribution} model?',
    'Is it a {Distribution} distribution that {Column} data follows?',
    'Is the distribution of data values in {Column} consistent with a {Distribution} distribution?',
    'Could the {Distribution} distribution serve as an accurate representation for {Column} data?',
    'Is it possible for {Column} data to have been drawn from a {Distribution} distribution?',
    'Does the pattern of {Column} resemble a {Distribution} distribution?',
    'Does {Column} reflect the properties of a {Distribution} distribution?',
    'Is the observed distribution of {Column} similar to a {Distribution} distribution?',
    'Does statistical analysis suggest a {Distribution} distribution of the {Column} data?',
    'Based on the statistical test, can we consider {Column} to exhibit a {Distribution} distribution?',
    'Could it be proper to say that {Column} data presents a {Distribution} distribution?',
    'Can we confirm the {Distribution} distribution hypothesis for {Column}?',
]

# variance test templates
# 2 Columns
variance_test_templates = [
    'Does the variability in {Column 1} match that of {Column 2}?',
    'Are the variances in {Column 1} and {Column 2} significantly different?',
    'Can we assume there is no major difference in variances for {Column 1} and {Column 2}?',
    'Is there a homogeneity of variance between {Column 1} and {Column 2}?',
    'Do {Column 1} and {Column 2} show similar levels of data spread?',
    'Are the fluctuations in {Column 1} comparable to those in {Column 2}?',
    'Is the data scatter in {Column 1} not much different to that in {Column 2}?',
    'Do {Column 1} and {Column 2} have parallel variance patterns to some degree?',
    'Are the dispersions of {Column 1} and {Column 2} statistically similar?',
    'Is there a uniformity in the variance of {Column 1} compared to {Column 2}?',
    'Do {Column 1} and {Column 2} demonstrate similar levels of data dispersion?',
    'Are the variations in {Column 1} and {Column 2} statistically indistinguishable?',
    'Do {Column 1} and {Column 2} show comparable data variability?',
    'Is there a parity in variance between {Column 1} and {Column 2}?',
    'Are the variances of {Column 1} and {Column 2} homogenous?',
    'Do {Column 1} and {Column 2} share similar variance characteristics?',
    'Is the degree of spread in {Column 1} similar to that in {Column 2}?'
]


'''
For descriptive statistical tasks
Mean, Median, Mode, Range, Quartile, Standard Deviation, Skewness, Kurtosis
'''
Mean_templates = [
    'What is the average of the {Column} values?',
    'Can you calculate the mean for {Column}?',
    'What\'s the mean value of {Column}?',
    'How do you find the average in {Column}?',
    'Could you determine the average amount in {Column}?',
    'What does the mean of {Column} indicate?',
    'How much is the average figure for {Column}?',
    'Can you tell me the average number in {Column}?',
]

Median_templates = [
    'Can you calculate the median of {Column}?',
    'What is the middle value in {Column}?',
    'How do I find the median for {Column}?',
    'Could you determine the median figure of {Column}?',
    'What number represents the median of {Column}?',
    'Can you tell me the median value in {Column}?',
    'How to compute the median of {Column}?',
    'What falls in the middle of {Column}?',
    'Can you find out what the median is in {Column}?',
]

Mode_templates = [
    'Can you find the mode of {Column}?',
    'What is the most frequent value in {Column}?',
    'What\'s the most common value in {Column}?',
    'Could you identify the mode value of {Column}?',
    'What appears most often in {Column}?',
    'Can you tell me the most repeated value in {Column}?',
    'How to calculate the mode of {Column}?',
    'Which value occurs the most in {Column}?',
]

Range_templates = [
    'Can you calculate the total span of {Column}?',
    'What is the difference between the maximum and minimum values in {Column}?',
    'How wide is the range of values in {Column}?',
    'What\'s the extent of variation in {Column}?',
    'Could you find the full spread of {Column}?',
    'What is the scale of variation for {Column}?',
    'How broad is the scope of {Column} values?',
    'Can you determine the range covered by {Column}?',
    'What\'s the interval between the highest and lowest points of {Column}?',
    'Could you tell me the distance from the smallest to the largest value in {Column}?',
]

Quartile_templates = [
    'Can you calculate the quartiles for {Column}?',
    'What are the quartile values in {Column}?',
    'How are the data in {Column} distributed across quartiles?',
    'Could you find the quartile divisions in {Column}?',
    'Can you determine the quartile breakdown for {Column}?',
    'How do the values in {Column} spread in terms of quartiles?',
    'Could you show the quartile segmentation of {Column}?',
    'What\'s the quartile distribution for the data in {Column}?',
]

Standard_deviation_templates = [
    'Can you calculate the standard deviation for {Column}?',
    'What is the variance measure for {Column}, as indicated by its standard deviation?',
    'How spread out are the values in {Column}, in terms of standard deviation?',
    'Could you find the standard deviation value of {Column}?',
    'Can you determine the dispersion in {Column} using standard deviation?',
    'What is the measure of standard variability for {Column}?',
    'How do the numbers in {Column} vary, as shown by the standard deviation?',
    'Could you provide the standard deviation for the dataset in {Column}?',
    'What\'s the level of spread in {Column} as indicated by its standard deviation?',
]

Skewness_templates = [
    'What is the skewness value for {Column}?',
    'Can you calculate the skew of {Column}?',
    'Is {Column} positively or negatively skewed?',
    'How skewed is the distribution of {Column}?',
    'Does {Column} show any skewness in its distribution?',
    'How does the asymmetry of {Column}?',
    'What is the degree of asymmetry in {Column}?',
    'Can you determine the skewness level for {Column}?',
]

Kurtosis_templates = [
    'Can you calculate the kurtosis for {Column}?',
    'What is the level of kurtosis in {Column}?',
    'How peaked is the distribution of {Column}?',
    'Does {Column} have a high or low kurtosis?',
    'Could you determine the extent of peaked for {Column}?',
    'Is there significant kurtosis present in the data for {Column}?',
    'What is the degree of peaked for {Column}?'
]
