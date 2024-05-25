cd ..

wait
echo "datasets preprocess starts..."
python Construction/dataset_preprocess.py
echo "datasets preprocess ends..."

echo "info extract starts..."
python Extraction/correlation_info_extraction.py
python Extraction/partial_correlation_info_extraction.py
python Extraction/contingency_table_test_info_extraction.py
python Extraction/KS_distribution_comparison_info_extraction.py
python Extraction/matel_haenszel_test_info_extraction.py
python Extraction/nomal_distribution_compliance_test_info_extraction.py
python Extraction/other_distribution_compliance_test_info_extraction.py
python Extraction/variance_test_info_extraction.py
python Extraction/descriptive_stats_info_extraction.py
echo "info extract ends..."

wait
echo "----------------------------------------------------------------------------"
echo "[i] Extraction finished!"
echo "[i] Reminder: manual filtering is recommended."