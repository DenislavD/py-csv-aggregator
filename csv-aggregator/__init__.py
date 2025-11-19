import argparse
import os

from core import DailyData

# Argument parsing
parser = argparse.ArgumentParser(
	prog='CSV Aggregator',
	description='Ingests data from multiple CSV files and provides summaries.',
	epilog='We hope you enjoy it!',)

parser.add_argument('path', nargs='+') # 1+ -> list
parser.add_argument('-a', '--agg-by', help='Aggregate by', type=int)
args = parser.parse_args()

print('Path:', args.path, ' Agg:', args.agg_by)

# @TODO add file path here
base_path = os.path.join(os.path.dirname(__file__), 'data') # , '2017'
base_file = os.path.join(base_path, '2017-06 Journal.csv') # INFO 2023.csv
print('Path:', base_file) # os.path.isfile(fname)

data = DailyData()
data.ingest_file(base_file)

print('Rows:', len(data.rows))
# @ TODO: Add logging next
