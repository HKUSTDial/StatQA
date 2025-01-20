cd ..
echo "[i] GPT experiments."
sleep 5s

# gpt-4o-mini-2024-07-18 Vanilla v.s. APrompt
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot" --batch_size 20 --threads 20
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot-aprompt-4o-mini" --batch_size 20 --threads 20
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-3.5-turbo" --trick "zero-shot-aprompt-4o" --batch_size 20 --threads 20 # Use different APrompt as comparison


# gpt-4o-2024-08-06 Vanilla v.s. APrompt
wait
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-4" --trick "zero-shot" --batch_size 20 --threads 20
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-4" --trick "zero-shot-aprompt-4o" --batch_size 20 --threads 20
python Evaluation/parallel_gpt_evaluation.py --selected_model "gpt-4" --trick "zero-shot-aprompt-4o-mini" --batch_size 20 --threads 20 # Use different APrompt as comparison