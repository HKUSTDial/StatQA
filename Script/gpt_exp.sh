cd ..

# gpt-3.5
python Evaluation/gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "one-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "one-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "stats-prompt"

# gpt-4
wait
python Evaluation/gpt_evaluation.py --selected_model "gpt-4" --trick "zero-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4" --trick "one-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4" --trick "zero-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4" --trick "one-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4" --trick "stats-prompt"

# gpt-4o
wait
python Evaluation/gpt_evaluation.py --selected_model "gpt-4o" --trick "zero-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4o" --trick "one-shot" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4o" --trick "zero-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4o" --trick "one-shot-CoT" &
python Evaluation/gpt_evaluation.py --selected_model "gpt-4o" --trick "stats-prompt"