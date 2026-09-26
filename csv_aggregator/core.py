import argparse
import os
import logging
import logging.handlers
from datetime import date

import pandas as pd

logging.basicConfig( # root level, valid for all imports as well
	handlers=[
		logging.StreamHandler(), # will use sys.stderr as default
		logging.handlers.TimedRotatingFileHandler(
			os.path.join(os.path.dirname(__file__), 'logs', 'myapp.log'), 'midnight'
		),
	],
	level=logging.WARNING,
	format='%(asctime)s: %(levelname)s@%(filename)s~%(lineno)d: %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
)
logging.getLogger('csv_aggregator').setLevel(logging.DEBUG) # package level

from .extractor import Extractor # relative now that it's packaged
from .transformer import Transformer
from .utils import get_csv_in_dir, get_file_queue, get_output_filename, get_serializer

log = logging.getLogger('csv_aggregator.core') # module level, inherits from parent


def create_parser() -> argparse.ArgumentParser:
	"""Creates, configures and returns the argparse object"""
	parser = argparse.ArgumentParser(
		prog='CSV Aggregator',
		description="""Ingests data from multiple CSV files and provides summaries.
Available columns: day:date, trades:int, result:int, note:str, begin:time
CSV files are stored in the /data project subfolder.""",
		formatter_class=argparse.RawTextHelpFormatter,
		epilog='I hope you enjoy it!',
	)
	parser.add_argument('path', nargs='+') # 1+ -> list
	parser.add_argument('-a', '--agg-by', help='Aggregate trades and result', \
						choices=['sum', 'mean', 'winlose', ], default='sum')
	parser.add_argument('-g', '--group-by', help='Group by', choices=['year', 'month', 'weekday', ])
	parser.add_argument('-t', '--top-n', help='Top n or -n results by day', type=int)
	parser.add_argument('-s', '--since', help='Since yyyy-mm-dd', type=date.fromisoformat)
	parser.add_argument('-u', '--until', help='Until yyyy-mm-dd', type=date.fromisoformat)
	parser.add_argument('-o', '--out-format', help='Output format', choices=['json', 'pdf', ], default='json')
	return parser

def main(args_list=None):
	log.info('Started program.')
	parser = create_parser()
	args = parser.parse_args(args_list) # args is a Namespace: vars(args)

	# Path parsing and collecting CSV files
	file_queue = get_file_queue(args.path)
	if not file_queue:
		log.error('Files couldn\'t be found.')
		raise SystemExit(2)

	# Extracting all the data
	data = [] # holds cleaned data for all files
	for filepath in file_queue:
		data += Extractor.process(filepath)
	log.info(f'{len(data)} total data rows gathered.')

	# Data processing
	transformer = Transformer(data)
	if args.since or args.until:	transformer.filterdate(args.since, args.until)
	if args.top_n:					transformer.get_top_n_results(args.top_n)
	if args.group_by:				transformer.group(args.group_by, args.agg_by)

	# Outputting data - simple json/pdf factory (functions)
	output_filename = get_output_filename(args)
	serializer = get_serializer(args.out_format, output_filename) # factory client
	serializer(transformer.grouped_df, transformer.df, args.top_n)

	log.info(f'Program completed with outputs saved to {output_filename}.{args.out_format} .')


if __name__ == '__main__':
	main()
	# Now that it's packaged, ensure installed:
	# activate venv -> pip install -e .[test] -> pip show csv-aggregator -> pytest
	# This is a symlink to the files folder. Then from anywhere:
	# csv-agg "2017-06 Journal.csv" data\2017 -a sum -g year -t 5 -s 2017-05-01 -u 2017-12-31
	# To remove: pip uninstall csv-aggregator