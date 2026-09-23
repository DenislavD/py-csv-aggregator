import logging
import csv
from datetime import date, datetime as dt
from itertools import groupby

import pandas

log = logging.getLogger('csv_aggregator.transformer')

class Transformer:
	def __init__(self, dataframe: pandas.DataFrame):
		self.df = dataframe.sort_index()

	def group(self, group_by) -> object:

		def grouper(elem):
			match group_by:
				case 'year':
					return str(elem.day.year)
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


	def filterdate(self, since: date | None, until: date | None):
		since = dt(since.year, since.month, since.day, 0, 0, 0) if since else dt.min
		until = dt(until.year, until.month, until.day, 0, 0, 0) if until else dt.max
		self.df = self.df[since:until]


	def get_top_n_results(self, n):
		descending = n >= 0
		self.rows = sorted(self.rows, key=lambda row: row.result, reverse=descending)[:abs(n)]


	def _dump_raw(self):
		with open('sample.csv', 'w',  newline='', encoding='utf-8-sig') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow('day, trades, result, note, begin'.split(', '))
			writer.writerows(self.rows)

