import argparse
import os
import sys
import logging
import logging.handlers
from datetime import date
# dev only
import pprint

logging.basicConfig(
	handlers=[
		logging.StreamHandler(sys.stderr), 
		#logging.handlers.TimedRotatingFileHandler('myapp.log', 'midnight'),
	], 
	level=logging.DEBUG,
	#format='%(asctime)s: %(levelname)s@%(filename)s~%(lineno)d: %(message)s',
	format='%(asctime)s [%(levelname)s]: %(message)s',
	datefmt='%m/%d/%Y %H:%M:%S',
)

from extractor import Extractor
from transformer import Transformer

log = logging.getLogger(__name__)

def main():
	#log.info('Started app')
	#breakpoint() # commands: w (stack trace), d/u, s(tep), n(ext), 
	#unt [lineno], r(eturn - step out), c(ontinue), pp (evaluate expr)

	# Argument parsing
	parser = argparse.ArgumentParser(
		prog='CSV Aggregator',
		description="""Ingests data from multiple CSV files and provides summaries.\n
			Available columns: day:date, trades:int, result:int, note:str, begin:time""",
		epilog='I hope you enjoy it!',
	)

	parser.add_argument('path', nargs='+') # 1+ -> list
	parser.add_argument('-a', '--agg-by', help='Aggregate trades and result', choices=['sum', 'mean', 'count', ])
	parser.add_argument('-g', '--group-by', help='Group by', choices=['year', 'month', 'weekday', ])
	parser.add_argument('-t', '--top-n', help='Top n results', type=int)
	parser.add_argument('-s', '--since', help='Since yyyy-mm-dd', type=date.fromisoformat)
	parser.add_argument('-u', '--until', help='Until yyyy-mm-dd', type=date.fromisoformat)
	args = parser.parse_args()
	#log.info(f'Args: {args}')

	# Path parsing and collecting files
	file_queue = set()
	for cur_path in args.path:
		# allow lazily not supplying data\ as folder
		norm_path = cur_path if os.path.exists(cur_path) else os.path.join('data', cur_path)

		if os.path.isfile(norm_path):
			file_queue.add(norm_path)
		elif os.path.isdir(norm_path):
			file_queue.update(get_csv_in_dir(norm_path))

	if not file_queue:
		sys.exit('Files couldn\'t be found.')
	for filepath in file_queue:
		Extractor.process(filepath)

	log.info(f'{len(Extractor.data)} total rows gathered.')
	#Transformer.dump_raw(Extractor.data)

	# Data processing
	transformer = Transformer(**vars(args)) # args is a Namespace
	pprint.pp(vars(transformer))



def get_csv_in_dir(directory) -> list:
	files = []
	for root, *_ in os.walk(directory):
		for filename in os.listdir(root):
			filepath = os.path.join(root, filename)
			if os.path.isfile(filepath) and filename.lower().endswith('.csv'):
				files.append(filepath)
	return files


if __name__ == '__main__':
	main()
	# run with:     py __init__.py "2017-06 Journal.csv"
	# Full example: py __init__.py data\2017 -a sum -g year -t 5 -s 2017-05-01 -u 2017-12-31