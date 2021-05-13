import data_collector
import data_analyzer
import argparse
import sys
import subprocess

def main(fetch_new_tweets=False, retrain=False, reanalyze=False):

    if fetch_new_tweets:
        # Get all the data from the past 7 days
        for minus_days in range(7):
           data_collector.get_new_tweets(items=2000, minus_days=minus_days)

    if retrain or reanalyze:
        # Wipe out and retrain all models
        data_analyzer.sentiment_analysis(retrain)

    # Run Dash using subprocess, this is to avoid everything gets run again when Dash creates a new subprocess 
    process = subprocess.Popen([sys.executable, 'data_visualisation.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    # Output everything from the subprocess to existing terminal
    for line in process.stdout:
        sys.stdout.write(line)

if  __name__ == "__main__":
    # take input
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true', help='Fetch new tweets')
    parser.add_argument('--train', action='store_true', help='Re-train all models')
    parser.add_argument('--analyze', action='store_true', help='Re-analyze all models')

    args = parser.parse_args()

    main(fetch_new_tweets=args.fetch, retrain=args.train, reanalyze=args.analyze)