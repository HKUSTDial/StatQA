cd ..

echo "[i] The program may take a long time to run, so please be patient."
sleep 3s

wait
echo "preliminary question generation starts..."
python Construction/preliminary_question_generation.py
wait
python Construction/preliminary_question_generation_for_descriptive_stats.py
echo "preliminary question generation ends..."

wait
echo "set difficulty level starts..."
python Construction/set_difficulty_level.py
echo "set difficulty level ends..."

wait
echo "integrate dataset starts..."
python Construction/integrate_dataset.py
echo "integrate dataset ends..."

wait
echo "Datset balancing and GPT refine question starts..."
python Construction/gpt_api_demo.py
wait
python Construction/benchmark_balancing.py
echo "Datset balancing and GPT refine question ends..."

wait
echo "benchmark postprocessing starts..."
python Construction/benchmark_postprocessing.py
echo "benchmark postprocessing ends..."

wait
echo "integrated dataset feature and distribution analysis starts..."
python stats_dataset_features.py
echo "integrated dataset feature and distribution analysis ends..."