import json
import pandas as pd
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_data_path', required=True, type=str)
    parser.add_argument('--save_path', required=True, type=str)
    parser.add_argument('--ground_truth_file', required=False, default=None, type=str)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    csv_df = pd.read_csv(args.csv_data_path)
    if args.ground_truth_file:
        df = pd.read_csv(args.ground_truth_file)
        csv_df["ground_truth"] = df["ground_truth"]
    csv_df.to_json(args.save_path, orient='records', indent=4)
