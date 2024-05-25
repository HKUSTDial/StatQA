import pandas as pd
import json


if __name__ == '__main__':
    with open("./llama3_8b_instruct_sft_generated_predictions.jsonl", "r", encoding="utf-8") as f:
        predictions = [json.loads(pred)["predict"] for pred in f.readlines()]
    df = pd.read_csv("../Model Answer/Origin Answer/llama_8b_zero-shot.csv")
    df["model_answer"] = predictions
    df.to_csv("../Model Answer/Origin Answer/llama3_8b_instruct_sft_zero-shot.csv", index=False)
