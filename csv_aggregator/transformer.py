import logging
import csv
from datetime import date, datetime as dt
from itertools import groupby

import pandas as pd

log = logging.getLogger('csv_aggregator.transformer')

class Transformer:
	def __init__(self, dataframe: pd.DataFrame):
		self.df = dataframe.sort_index()
		self.grouped_df = None

	def group(self, group_by, agg_by):
		def winlose(x: pd.Series):
			coeff = x[x >= 0].count() / x.count()
			return coeff # f'{coeff:.1%}' formatting shouldn't be here

		match group_by:
			case 'year': 	clause = self.df.index.year
			case 'weekday': clause = self.df.index.day_name(locale=None)
			case _: 		clause = self.df.index.strftime('%Y-%m')

		match agg_by:
			case 'mean': 	aggfunc = 'mean'
			case 'winlose': aggfunc = winlose
			case _: 		aggfunc = 'sum'

		self.grouped_df = self.df.groupby(clause).agg({
			'trades': 'sum',
			'result': ['count', aggfunc],
			'begin': 'mean',
		})
		self.grouped_df.index.name = group_by

	def filterdate(self, since: date | None, until: date | None):
		# need to convert filter from date to datetime because it will be deprecated in pandas 4
		since = dt(since.year, since.month, since.day, 0, 0, 0) if since else dt.min
		until = dt(until.year, until.month, until.day, 23, 59, 59) if until else dt.max
		self.df = self.df[since:until]

	def get_top_n_results(self, n):
		ascending = n < 0
		self.df = self.df.sort_values(by='result', ascending=ascending).head(abs(n))

	def _dump_raw(self):
		self.df.to_excel('sample.xlsx')
