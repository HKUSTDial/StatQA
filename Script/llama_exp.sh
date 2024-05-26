cd ..

# llama-2-7b
wait
python Evaluation/llama_evaluation.py --model_type "2_7b" --dataset_name "mini-StatQA" --trick "zero-shot"

wait
python Evaluation/llama_evaluation.py --model_type "2_7b" --dataset_name "mini-StatQA" --trick "one-shot"

wait
python Evaluation/llama_evaluation.py --model_type "2_7b" --dataset_name "mini-StatQA" --trick "zero-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "2_7b" --dataset_name "mini-StatQA" --trick "one-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "2_7b" --dataset_name "mini-StatQA" --trick "stats-prompt"


# llama-2-13b
wait
python Evaluation/llama_evaluation.py --model_type "2_13b" --dataset_name "mini-StatQA" --trick "zero-shot"

wait
python Evaluation/llama_evaluation.py --model_type "2_13b" --dataset_name "mini-StatQA" --trick "one-shot"

wait
python Evaluation/llama_evaluation.py --model_type "2_13b" --dataset_name "mini-StatQA" --trick "zero-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "2_13b" --dataset_name "mini-StatQA" --trick "one-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "2_13b" --dataset_name "mini-StatQA" --trick "stats-prompt"


# llama-3-8b-Instruct
wait
python Evaluation/llama_evaluation.py --model_type "3_8b_instruct" --dataset_name "mini-StatQA" --trick "zero-shot"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b_instruct" --dataset_name "mini-StatQA" --trick "one-shot"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b_instruct" --dataset_name "mini-StatQA" --trick "zero-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b_instruct" --dataset_name "mini-StatQA" --trick "one-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b_instruct" --dataset_name "mini-StatQA" --trick "stats-prompt"


# llama-3-8b-Instruct
wait
python Evaluation/llama_evaluation.py --model_type "3_8b" --dataset_name "mini-StatQA" --trick "zero-shot"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b" --dataset_name "mini-StatQA" --trick "one-shot"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b" --dataset_name "mini-StatQA" --trick "zero-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b" --dataset_name "mini-StatQA" --trick "one-shot-CoT"

wait
python Evaluation/llama_evaluation.py --model_type "3_8b" --dataset_name "mini-StatQA" --trick "stats-prompt"


# finetuned model
# wait
# python Evaluation/llama_evaluation.py --model_type "sft" --dataset_name "mini-StatQA" --trick "zero-shot"