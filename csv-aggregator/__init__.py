import argparse
import os
import sys
import logging
import logging.handlers

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

from core import Extractor

log = logging.getLogger(__name__)

def main():
	#log.info('Started app')
	#breakpoint() # commands: w, s, n, unt [lineno], r, c, pp (evaluate)

	# Argument parsing
	parser = argparse.ArgumentParser(
		prog='CSV Aggregator',
		description='Ingests data from multiple CSV files and provides summaries.',
		epilog='I hope you enjoy it!',
	)

	parser.add_argument('path', nargs='+') # 1+ -> list
	parser.add_argument('-a', '--agg-by', help='Aggregate by', type=int)
	args = parser.parse_args()
	log.info(f'Path: {args.path}  Agg: {args.agg_by}')

	# Path parsing and dir loop
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
		print(filepath)
		#Extractor.process(filepath)

	print('---- end walk -----')
	log.info(f'{len(Extractor.data)} total rows gathered.')
	exit()
	base_path = os.path.join(os.path.dirname(__file__), 'data') # , '2017'
	base_file = os.path.join(base_path, args.path[0]) # INFO 2023.csv
	print('Path:', base_file) # os.path.isfile(fname)


	

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
	# run with: py __init__.py "2017-06 Journal.csv"