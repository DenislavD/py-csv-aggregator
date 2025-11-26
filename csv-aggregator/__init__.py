import argparse
import os
import sys
import logging
import logging.handlers

logging.basicConfig(
	handlers=[
		logging.StreamHandler(sys.stderr), 
		logging.handlers.TimedRotatingFileHandler('myapp.log', 'midnight'),
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

	print('Path:', args.path, ' Agg:', args.agg_by)

	# @TODO add file path here
	base_path = os.path.join(os.path.dirname(__file__), 'data') # , '2017'
	base_file = os.path.join(base_path, args.path[0]) # INFO 2023.csv
	print('Path:', base_file) # os.path.isfile(fname)

	# Extractor.parse_paths
	Extractor.ingest_file(base_file)

	#print('Rows:', len(Extractor.data))

	



if __name__ == '__main__':
	main()
	# run with: py __init__.py "2017-06 Journal.csv"