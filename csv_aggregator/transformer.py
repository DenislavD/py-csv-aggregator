from datetime import date, datetime as dt

import pandas as pd

from .extractor import Extractor

class Transformer:
	"""Transforms (sorts, filters, groups, aggregates) the raw data."""

	def __init__(self, data: list[Extractor.DataRow]):
		self.df = pd.DataFrame.from_records(data, columns=Extractor.FINAL_HEADERS, index='day')
		self.df.index = pd.to_datetime(self.df.index, format='%Y-%m-%d', exact=True)
		self.df.begin = pd.to_datetime(self.df.begin, format='%H:%M:%S', exact=False, errors='coerce')
		self.df.sort_index(inplace=True)

		self.grouped_df = None

	def group(self, group_by: str, agg_by: str='sum'):
		def winlose(x: pd.Series):
			coeff = x[x >= 0].count() / x.count()
			return f'{coeff:.1%}' # should formatting be here?

		match group_by:
			case 'year': 	clause = self.df.index.year
			case 'weekday': clause = self.df.index.day_name(locale=None)
			case _: 		clause = self.df.index.strftime('%Y-%m')

		match agg_by:
			case 'mean': 	aggfunc = 'mean'
			case 'winlose': aggfunc = winlose
			case _: 		aggfunc = 'sum'

		self.grouped_df = self.df.groupby(clause).agg({
			'trades': ['count', 'sum'],
			'result': aggfunc,
			'begin': 'mean',
		})

		# tidy up groups format
		self.grouped_df['begin', 'mean'] = self.grouped_df['begin', 'mean'].dt.strftime('%H:%M')
		# ColumnIndex now looks like: MultiIndex([('trades', 'sum'), ('result', 'mean'), ...
		self.grouped_df.columns = [ f"{col.capitalize()} {stat.capitalize()}" # flatten it
										for col, stat in self.grouped_df.columns ]
		self.grouped_df.columns.values[0] = 'Days Traded'
		self.grouped_df.index.name = group_by.capitalize() # update row index naming

	def filterdate(self, since: date | None, until: date | None):
		# need to convert filter from date to datetime because it will be deprecated in pandas 4
		since = dt(since.year, since.month, since.day, 0, 0, 0) if since else dt.min
		until = dt(until.year, until.month, until.day, 23, 59, 59) if until else dt.max
		self.df = self.df[since:until]

	def get_top_n_results(self, n: int):
		ascending = n < 0
		self.df = self.df.sort_values(by='result', ascending=ascending).head(abs(n))

	def _dump_raw(self):
		self.df.to_excel('sample.xlsx')
