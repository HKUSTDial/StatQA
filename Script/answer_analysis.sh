cd ..

wait
python analyze_model_answer.py
wait
python 'Model Answer/Task Performance/summary_performance.py'
wait
python 'Model Answer/Task Performance/draw_radar_chart.py'
wait
python 'Model Answer/Task Performance/task_confusion_analysis.py'
wait
python 'Model Answer/Task Performance/error_type_analysis.py