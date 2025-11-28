import logging
import csv

log = logging.getLogger(__name__)

class Transformer:
	# implement me!

	def dump_raw(data):
		with open('sample.csv', 'w',  newline='', encoding='utf-8-sig') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow('day, trades, result, note, begin'.split(', '))
			writer.writerows(data)

