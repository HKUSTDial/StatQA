# llama-3 3_8b_instruct ecxperiments script

cd ..


# # llama 3_8b_instruct ecxperiments script
# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark" --trick "zero-shot"

# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark" --trick "one-shot"

# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark" --trick "two-shot"

# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark" --trick "zero-shot-CoT"

# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark" --trick "one-shot-CoT"

# # direct exp
# wait
# python llama_answer_vllm.py --model_type "3_8b_instruct" --dataset_name "Balanced Benchmark Llama " --trick "free direct-test"



# llama 3_8b ecxperiments script
wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark" --trick "zero-shot"

wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark" --trick "one-shot"

wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark" --trick "two-shot"

wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark" --trick "zero-shot-CoT"

wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark" --trick "one-shot-CoT"

# direct exp
wait
python llama_answer_vllm.py --model_type "3_8b" --dataset_name "Balanced Benchmark Llama" --trick "free direct-test"

python gpt_answer.py --selected_model "gpt-3.5-turbo" --trick "zero-shot"