import logging
import csv
from datetime import date
from itertools import groupby
import pprint

log = logging.getLogger('csv_aggregator.transformer')

# dev only
# from collections import namedtuple
# DataRow = namedtuple('DataRow', ['day', 'trades', 'result', 'note', 'begin'])
# from extractor import Extractor

class Transformer:
	def __init__(self, data):
		self.rows = data
		self.groups = []

		# self.raw = [
		# 	DataRow(day=date(2017, 6, 30), trades=1, result=-15, note='missed trades before 18:00 . Need to be ready to ACT', begin=None),                                
		# 	DataRow(day=date(2027, 6, 2), trades=5, result=100, note='no market data', begin=None),                                                                         
		# 	DataRow(day=date(2015, 6, 13), trades=1, result=20, note='', begin=None), 
		# 	DataRow(day=date(2017, 6, 3), trades=0, result=0, note='', begin=None),                                                                                    
		# 	DataRow(day=date(2015, 6, 4), trades=0, result=0, note='', begin=None),                                                                                    
		# 	DataRow(day=date(2015, 6, 5), trades=1, result=-5, note="first trading day after 3 days of rest, was careful. Had", begin=None)
		# ]

	def group(self, group_by) -> object:

		def grouper(elem):
			match group_by:
				case 'year':
					return elem.day.year
				case 'month':
					return elem.day.strftime('%Y-%m')
				case 'weekday':
					return elem.day.strftime('%A') # .isoweekday()

		groups = []
		for key, group in groupby(sorted(self.rows, key=grouper), key=grouper):
			# transpose number sequences for easier aggregation
			trades, results, begins = zip(*[(row.trades, row.result, row.begin) for row in group])
			groups.append({
				'group': key,
				'data_series': {
					'trades': trades,
					'results': results,
					'begins': begins,
				},
				'outputs': {},
				})
		
		self.groups = groups
		return self


	def aggregate(self, agg_by):

		def aggregator(results):
			match agg_by:
				case 'mean':
					return round(sum(results) / len(results), 1)
				case 'winlose':
					return f'{len([*filter(lambda x: x >= 0, results)]) / len(results):.1%}'
				case _:
					return sum(results)

		for group in self.groups:
			group['outputs']['days-count'] = len(group['data_series']['trades'])
			group['outputs']['trades-sum'] = sum(group['data_series']['trades'])
			group['outputs']['trades-mean'] = round(group['outputs']['trades-sum'] / group['outputs']['days-count'], 1)
			group['outputs'][f'results-{agg_by}'] = aggregator(group['data_series']['results'])


	def filterdate(self, since, until):
		since = since or date.min
		until = until or date.max
		self.rows = [row for row in self.rows if row.day >= since and row.day <= until]


	def get_top_n_results(self, n):
		descending = n >= 0
		self.rows = sorted(self.rows, key=lambda row: row.result, reverse=descending)[:abs(n)]


	def dump_raw(self):
		with open('sample.csv', 'w',  newline='', encoding='utf-8-sig') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow('day, trades, result, note, begin'.split(', '))
			writer.writerows(self.rows)


# dev area
# a = Transformer(agg_by='winlose', group_by='month', top_n=100, since=date(2017, 5, 1), until=date(2017, 12, 31))

# pprint.pp(vars(a))
