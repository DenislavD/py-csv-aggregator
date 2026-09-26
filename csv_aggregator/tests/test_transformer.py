from .. transformer import Transformer
import pytest
from datetime import date

from collections import namedtuple
DataRow = namedtuple('DataRow', ['day', 'trades', 'result', 'note', 'begin'])

@pytest.fixture
def transformer(scope='module'):
	sample_row_data = [ # do not change order or review all tests below
		DataRow(day=date(2017, 6, 30), trades=1, result=-15, note='missed trades before 18:00 . Need to be ready to ACT', begin=None),                                
		DataRow(day=date(2027, 6, 2), trades=5, result=100, note='no market data', begin=None),                                                                         
		DataRow(day=date(2015, 6, 13), trades=1, result=20, note='', begin=None), 
		DataRow(day=date(2017, 6, 3), trades=0, result=0, note='', begin='15:30:00'),                                                                                    
		DataRow(day=date(2015, 6, 4), trades=0, result=0, note='', begin=None),                                                                                    
		DataRow(day=date(2015, 6, 5), trades=1, result=-5, note="first trading day after 3 days of rest, was careful. Had", begin=None),
		DataRow(day=date(2015, 7, 7), trades=2, result=100, note='TEST ROW', begin=None),    
		DataRow(day=date(2015, 7, 8), trades=2, result=100, note='TEST ROW', begin=None),    
	]
	return Transformer(sample_row_data)

def test_group_year_sorted(transformer):
	transformer.group('year')
	assert all(transformer.grouped_df.index == (2015, 2017, 2027)) # compares each array item

def test_group_month_sorted(transformer):
	transformer.group('month')
	assert transformer.grouped_df.shape[0] == 4
	assert transformer.grouped_df.index[0] == '2015-06'

def test_group_weekday(transformer):
	transformer.group('weekday')
	rows_count = transformer.grouped_df.iloc[:, 1].count() # get first column's row count
	assert rows_count == 5

def test_aggregate_winlose(transformer):
	transformer.group('year', 'winlose')

	test_group = transformer.grouped_df.values[0] # [6 5 '80.0%' nan]
	assert test_group[1] == 5 and test_group[2] == '80.0%'

def test_filter_empty(transformer):
	transformer.filterdate(None, None)
	assert transformer.df.shape[0] == 8

def test_filterdate(transformer):
	since = date(2016, 1, 1)
	until = date(2018, 1, 1)
	transformer.filterdate(since, until) # should take days (2017, 6, 3) and (2017, 6, 30)
	assert transformer.df.shape[0] == 2
	assert all(transformer.df.iloc[..., :2] == [[0, 0], [1, -15]])

def test_filter_since(transformer):
	since = date(2027, 6, 2)
	transformer.filterdate(since, None)
	assert transformer.df.shape[0] == 1

def test_filter_until(transformer):
	until = date(2005, 12, 31)
	transformer.filterdate(None, until)
	assert transformer.df.shape[0] == 0

def test_get_top_n_results(transformer):
	transformer.get_top_n_results(-4)
	assert transformer.df.shape[0] == 4
	assert all(transformer.df.values[0][:2] == [1, -15])
