import argparse
import os
import sys
import logging
import logging.handlers
from datetime import date

logging.basicConfig( # root level, valid for all imports as well
	handlers=[
		logging.StreamHandler(sys.stderr), 
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
from .utils import get_serializer

log = logging.getLogger('csv_aggregator.core') # module level, inherits from parent


def main():
	log.info('Started program')

	# Argument parsing
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
	args = parser.parse_args() # args is a Namespace: vars(args)

	# Path parsing and collecting files
	file_queue = get_file_queue(args.path)
	if not file_queue:
		log.error('Files couldn\'t be found.')
		sys.exit()
	for filepath in file_queue:
		Extractor.process(filepath)
	log.info(f'{len(Extractor.data)} total rows gathered.')

	# Data processing
	name_string = ''
	transformer = Transformer(Extractor.data)
	if args.since or args.until:
		transformer.filterdate(args.since, args.until)
		name_string = f'{args.since or "min"}--{args.until or "max"} {name_string}'
	if args.top_n:
		transformer.get_top_n_results(args.top_n)
		name_string = f'top{args.top_n} {name_string}'
	if args.group_by:
		transformer.group(args.group_by).aggregate(args.agg_by)
		name_string = f'group-by-{args.group_by} agg-by-{args.agg_by} {name_string}'

	# Outputting data - simple json/pdf factory (functions)
	serializer = get_serializer(args.out_format, name_string) # factory client
	serializer(transformer.groups, transformer.rows, args.top_n)

	log.info(f'Program completed with outputs provided in output.{args.out_format} .')


def get_csv_in_dir(directory) -> list:
	files = []
	for root, *_ in os.walk(directory):
		for filename in os.listdir(root):
			filepath = os.path.join(root, filename)
			if os.path.isfile(filepath) and filename.lower().endswith('.csv'):
				files.append(filepath)
	return files


def get_file_queue(args_path) -> set:
	file_queue = set()
	for cur_path in args_path:
		scripts_dir = os.path.dirname(__file__)

		if os.path.exists(os.path.abspath(cur_path)):
			norm_path = os.path.abspath(cur_path)
		elif os.path.exists(os.path.join(scripts_dir, cur_path)):
			norm_path = os.path.join(scripts_dir, cur_path)
		else: # allow lazily not supplying data\ as folder
			norm_path = os.path.join(scripts_dir, 'data', cur_path)

		if os.path.isfile(norm_path):
			file_queue.add(norm_path)
		elif os.path.isdir(norm_path):
			file_queue.update(get_csv_in_dir(norm_path))
	return file_queue


if __name__ == '__main__':
	main()
	# Now that it's packaged, ensure installed (pip install -e .[test] /// pip show csv-aggregator)
	# This is a symlink to the files folder. Then from anywhere:
	# csv-agg "2017-06 Journal.csv" data\2017 -a sum -g year -t 5 -s 2017-05-01 -u 2017-12-31
	# To remove: pip uninstall csv-aggregator