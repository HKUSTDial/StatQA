# -*- coding: gbk -*-
import sys
import os
main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, main_folder_path)

import requests
import json


'''
Test connectivity of GPT API
'''


# [ATTENTION]: The config file is confidential and can NOT be uploaded or backed up!
# read config to get authorization
config_file = open('gpt_config.txt', 'r')
config_content = config_file.readlines()
config_file.close()
config_list = [line.strip() for line in config_content] # [url, authorization]


def refine_question(sentence: str) -> str:
    # url and authorization information is stored in config.txt
    url = config_list[0]
    headers = {
        "Content-Type": "application/json",
        "Authorization": config_list[1]
    }
    data = {
        # Available Models: gpt-4, gpt-4-32k, gpt-3.5-turbo, gpt-3.5-turbo-16k, all models' version in 0613
        "model": "gpt-4",  # select GPT model
        "messages": [
            {"role": "system", "content": "I'm here to help you correct English sentences. Please tell me the sentence you want to correct."},
            {"role": "user", "content": f"Please revise this sentence: {sentence}"}
        ],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json() 
    return result['choices'][0]['message']['content']


# test connectivity
print(refine_question("My name are Tom, and I has two apple."))
print('GPT Connected!')
