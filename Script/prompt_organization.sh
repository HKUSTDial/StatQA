cd ..

python Construction/prompt_organization.py --trick_name "zero-shot" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "one-shot" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "two-shot" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "zero-shot-CoT" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "one-shot-CoT" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "stats-prompt" --integ_dataset_name "mini-StatQA"
python Construction/prompt_organization.py --trick_name "zero-shot" --integ_dataset_name "Balanced Benchmark train"