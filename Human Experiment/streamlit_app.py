import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import json
import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide")


# Function for reading CSV file
@st.cache_data
def load_data(data_file):
    return pd.read_csv(data_file)


# Initialize session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'selected_groups' not in st.session_state:
    st.session_state.selected_groups = [[]]
if 'method_ans' not in st.session_state:
    st.session_state.method_ans = [[]]
if 'column_ans' not in st.session_state:
    st.session_state.column_ans = ['']
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'df' not in st.session_state:
    st.session_state.df = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'show_video' not in st.session_state:
    st.session_state.show_video = False

# Login page
def login():
    empty_area_1, login_area, empty_area_2 = st.columns([0.65,2,0.65], gap="small")
    with login_area:
        st.markdown(f"""<span style='font-size: 54px; color: #fc5c65; margin-bottom: 50px; font-family: Times New Roman; font-style: italic;'>
                        <b>🎉Welcome!</b>
                    </span>""", 
                    unsafe_allow_html=True)
        st.write("Thank you very much for your time and participation.")
        st.write("This platfrom is designed to study human's understanding and ability to answer statistical questions. All tests will be anonymous. Your real, honest and independent answers will be greatly appreciated.")
        with st.form("login_form"):
            group = st.selectbox("Experimental Group", ["Stats Background", "Non-Stats Background"])
            mode = st.selectbox("Test Mode", ["Closed-book", "Open-book"])
            block = st.selectbox("Task Block ID", [0, 1, 2, 3])
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if password == "3.14159":
                    st.session_state.authenticated = True
                    st.session_state.group = group
                    st.session_state.mode = mode
                    st.session_state.block = block
                    st.session_state.start_time = time.time()  # Reset start time on login
                    load_data_for_block(block)  # Load data after successful login
                    st.rerun()
                else:
                    st.error("Password incorrect!")
        
        if st.button('Show/Hide Tutorial'):
            st.session_state.show_video = not st.session_state.show_video
        
        if st.session_state.show_video:
            video_url = 'StatsHumanExp tutorial.mp4'
            st.video(video_url)


# Load data for the correspondig task block ID
def load_data_for_block(block_id):
    file_name = f'data/task_block_{block_id}.csv'
    # file_name = f'questions.csv'
    st.session_state.df = pd.read_csv(file_name)
    initialize_state_with_data()


# Initialize state with data
def initialize_state_with_data():
    df = st.session_state.df
    st.session_state.selected_groups = [[] for _ in range(len(df))]
    st.session_state.method_ans = [[] for _ in range(len(df))]
    st.session_state.column_ans = ['' for _ in range(len(df))]


# Main page display
def main_page():
    display_sidebar()
    show_question()


# The ending page
def end():
    empty_area_1, thanks_area, empty_area_2 = st.columns([1,2,1], gap="medium")
    with thanks_area:
        st.markdown(f"""
                    <span style='font-size: 44px;'>
                        🥳
                    </span>
                    <span style='font-size: 44px; color: #fc5c65; margin-bottom: 50px; font-family: Times New Roman; font-style: italic;'>
                        <b>Thanks for participation!</b>
                    </span>""", 
                    unsafe_allow_html=True)
        st.write('Thank you very much for your time and participation in this study. Your answers are invaluable. Have a nice day!')
        st.write('If you have any questions or comments, please feel free to contact us.')
        st.success('✅Submitted successfully!')


# Sidebar dislay
def display_sidebar():
    df = st.session_state.df
    # Initialize language settings, default to English
    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    # Create a button to switch languages
    if st.sidebar.button('Language: EN/ZH'):
        if st.session_state.language == 'Chinese':
            st.session_state.language = 'English'
        else:
            st.session_state.language = 'Chinese'
    
    # Display corresponding prompt information according to the current language status
    if st.session_state.language == 'Chinese':
        st.sidebar.markdown(f"""
                        <span style='font-size: 32px; margin-bottom: 50px;'>
                            ⚠️
                        </span>
                        <span style='font-size: 36px; color: #ff793f; font-style: italic; margin-bottom: 50px;'>
                            <u><b>Instruction</b></u>
                        </span>""", 
                        unsafe_allow_html=True)
        with st.sidebar.container():
            st.sidebar.markdown("""
                    我们将为您提供某数据表的列信息和一个统计学问题。您需要参考列信息，选择该统计学问题涉及的列和<u>**所有适用**</u>于解决该问题的统计学方法。\n
                    提示：请注意使用某些统计学方法潜在的先决条件。""", 
                    unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
                        <span style='font-size: 32px; margin-bottom: 50px;'>
                            ⚠️
                        </span>
                        <span style='font-size: 36px; color: #ff793f; font-style: italic; margin-bottom: 50px;'>
                            <u><b>Instruction</b></u>
                        </span>""", 
                        unsafe_allow_html=True)
        with st.sidebar.container():
            st.sidebar.markdown("""
                    We will provide you with column information for a data table and a statistical question. You need to refer to column information, and then select the columns involved in the question and <u>**all applicable**</u> statistical methods to solve the question. \n
                    Hint: Please note there may be prerequisites for some statistical method.""", 
                    unsafe_allow_html=True)

    st.sidebar.markdown("---")
    # Create an empty progress display container
    progress_container = st.sidebar.empty()
    # Show progress and experiment info in bottom container
    with progress_container:
        st.sidebar.markdown(f"""Group: {st.session_state.group};  
        Test Mode: {st.session_state.mode};  
        Task Block ID: {st.session_state.block};  
        Current progress: {st.session_state.current_index + 1}/{len(df)}
        """)
        progress = (st.session_state.current_index + 1) / len(df)
        st.sidebar.progress(progress)
        

# Obtain metadata based on dataset name for GUI display
def get_metadata_for_gui(dataset_name):
    # Construct the path to the metadata file based on the dataset name
    metadata_file_path = f'../Data/Metadata/Column Metadata/{dataset_name}_col_meta.csv'
    # Load and return the metadata file
    metadata_df = pd.read_csv(metadata_file_path)
    return metadata_df


# Display current question and options: Information Area and Selecting Area
def show_question():
    df = st.session_state.df
    if 'current_index' in st.session_state and st.session_state.current_index < len(df):
        current_dataset = df.iloc[st.session_state.current_index]['dataset']
        current_dataset_meta_df = get_metadata_for_gui(dataset_name=current_dataset)
        current_dataset_num_of_rows = current_dataset_meta_df['num_of_rows'].iloc[0]
        current_dataset_meta_df = current_dataset_meta_df.drop(columns=['dataset', 'num_of_rows', 'column_description'])
        column_info_df = current_dataset_meta_df[['column_header', 'data_type', 'is_normality']].replace("quant", "quantitative").replace("cate", "categorical")
        current_benchmark_row = df.iloc[st.session_state.current_index]

        info_area, select_area = st.columns([3, 3], gap="medium")

        # information area
        with info_area:
            st.header("📋Information Area")
            info_container = st.container(border=True)
            info_container.markdown(f"""#### Statistical Question:""")
            info_container.markdown(f"""
                    <span style='font-size: 19px; color: #079992; font-style: italic; margin-bottom: 0px;'>
                        <b>{current_benchmark_row['refined_question']}</b>
                    </span>""", 
                unsafe_allow_html=True)
            info_container.markdown("""#### Column Information:""")
            # info_container.markdown(f"* Current dataset name: {current_dataset} \n\n * Current dataset number of rows: {current_dataset_num_of_rows}")
            info_container.markdown(f"""<span style='font-size: 16px;'>
                                        - Current dataset name: {current_dataset}
                                    </span>
                                    <br />
                                    <span style='font-size: 16px;'>
                                        - Current dataset number of rows: {current_dataset_num_of_rows}
                                    </span>
                                    <br />""", 
                                    unsafe_allow_html=True)
            
            # info_container.markdown(f"* Current dataset number of rows: {current_dataset_num_of_rows}")
            info_container.write(column_info_df)
        
        column_header_list = column_info_df['column_header'].tolist()
        group_options = ['Correlation Analysis', 'Distribution Compliance Test', 'Contingency Table Test', 'Descriptive Statistics', 'Variance Test']
        detailed_options = {
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

        # selecting area
        with select_area:
            st.header("🧪Selecting Area")
            select_container = st.container(border=True)

            # select relevant columns
            select_container.markdown("""#### Relevant columns selection:""")
            st.session_state.column_ans[st.session_state.current_index] = select_container.multiselect(
                label=f"Please select column headers involved in the given question. \n\n ℹ️If you think there is a strata or control variable involved, put it to the end.", 
                default=None, options=column_header_list, key=f"{st.session_state.current_index}_2")
            
            # select applicable statistical methods
            select_container.markdown("""#### *ALL* applicable methods selection:""")
            st.session_state.selected_groups[st.session_state.current_index] = select_container.multiselect(
                "Methods category: \n\n ℹ️The category here is for facilitating you to filter proper methods, the category selection won't be recorded.", group_options, key=f"{st.session_state.current_index}_groups")
            current_selections = []
            for group in st.session_state.selected_groups[st.session_state.current_index]:
                current_selections.extend(detailed_options[group])
            st.session_state.method_ans[st.session_state.current_index] = select_container.multiselect(
                "Please refer to column information, and select ALL methods applicable to solve the given statistical question:", current_selections, key=f"{st.session_state.current_index}_details")
            
            page_navigation()


# Save answers to csv
def save_answers():
    df = st.session_state.df
    curr_group = st.session_state.group
    curr_mode = st.session_state.mode
    curr_block_id = st.session_state.block
    df['selected_methods'] = [json.dumps(a) for a in st.session_state.method_ans]
    df['selected_columns'] = [json.dumps(a) for a in st.session_state.column_ans]
    df.to_csv(f'answer/answer_{curr_group}_{curr_mode}_{curr_block_id}.csv', index=False)


# Page navigation
def page_navigation():
    df = st.session_state.df
    if st.session_state.current_index < len(df) - 1:
        if st.button('Next >>'):
            if st.session_state.method_ans[st.session_state.current_index] and st.session_state.column_ans[st.session_state.current_index]:
                # Save current answer
                save_answers()
                # Go to next question
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.warning('Please complete all required selection tasks!')
    else:
        if st.session_state.method_ans[st.session_state.current_index] and st.session_state.column_ans[st.session_state.current_index]:
            if st.button('Submit all'):
                # Make sure all questions are answered
                if all(a1 and a2 for a1, a2 in zip(st.session_state.method_ans, st.session_state.column_ans)):
                    save_answers()  # 最后一次保存
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error('Please complete all required selection tasks!')
        else:
            st.warning('Please complete all required selection tasks!')


# Main page
if not st.session_state.authenticated:
    login()
else:
    if st.session_state.submitted:
        end()
    else:
        main_page()