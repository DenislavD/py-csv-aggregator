import logging
import csv
from datetime import date
import pprint

log = logging.getLogger(__name__)


class Transformer:
	def __init__(self, **args):
		# @TODO not sure this is needed
		self.agg_by = args['agg_by']
		self.group_by = args['group_by']
		self.top_n = args['top_n']
		self.since = args['since']
		self.until = args['until']


	def _aggregate():
		...

	def _groupby():
		if self.group_by:
			...


	# @property
	# def group_by(self):
	# 	return self._group_by
	# @group_by.setter
	# def group_by(self, arg):
	# 	if arg not in ['year', 'month', 'weekday', None]:
	# 		log.error('Grouping can be by: year, month or weekday')
	# 		self._group_by = input('Please provide grouping criteria: ')
	# 	else:
	# 		self._group_by = arg
	


	def dump_raw(data):
		with open('sample.csv', 'w',  newline='', encoding='utf-8-sig') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow('day, trades, result, note, begin'.split(', '))
			writer.writerows(data)


# dev area
a = Transformer(agg_by='sum', group_by='year', top_n=None, since=date(2017, 5, 1), until=date(2017, 12, 31))

pprint.pp(vars(a))

