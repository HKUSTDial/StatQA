cd ..

echo "metadata framewark creation starts..."
python metadata_helper.py
echo "metadata framewark creation ends..."

wait
echo "datasets preprocess starts..."
python dataset_preprocess.py
echo "datasets preprocess ends..."