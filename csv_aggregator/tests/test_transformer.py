from .. transformer import Transformer
import pytest
from datetime import date

from collections import namedtuple
DataRow = namedtuple('DataRow', ['day', 'trades', 'result', 'note', 'begin'])

@pytest.fixture
def sample_row_data():
	return [ # do not change order or review all tests below
		DataRow(day=date(2017, 6, 30), trades=1, result=-15, note='missed trades before 18:00 . Need to be ready to ACT', begin=None),                                
		DataRow(day=date(2027, 6, 2), trades=5, result=100, note='no market data', begin=None),                                                                         
		DataRow(day=date(2015, 6, 13), trades=1, result=20, note='', begin=None), 
		DataRow(day=date(2017, 6, 3), trades=0, result=0, note='', begin=None),                                                                                    
		DataRow(day=date(2015, 6, 4), trades=0, result=0, note='', begin=None),                                                                                    
		DataRow(day=date(2015, 6, 5), trades=1, result=-5, note="first trading day after 3 days of rest, was careful. Had", begin=None),
		DataRow(day=date(2015, 7, 7), trades=2, result=100, note='TEST ROW', begin=None),    
		DataRow(day=date(2015, 7, 8), trades=2, result=100, note='TEST ROW', begin=None),    
	]

def test_group_year_sort(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.group('year')
	assert len(transformer.groups) == 3 and transformer.groups[0]['group'] == '2015'

def test_group_month_sort(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.group('month')
	assert len(transformer.groups) == 4 and transformer.groups[0]['group'] == '2015-06'

def test_group_weekday(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.group('weekday')
	assert len(transformer.groups) == 5

def test_aggregate_winlose(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.group('year').aggregate('winlose')

	test_group = transformer.groups[0]
	assert test_group['outputs']['days-count'] == 5 and test_group['outputs']['results-winlose'] == '80.0%'

def test_filter_empty(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.filterdate(None, None)
	assert len(transformer.rows) == 8

def test_filterdate(sample_row_data):
	transformer = Transformer(sample_row_data)
	since = date(2016, 1, 1)
	until = date(2018, 1, 1)
	transformer.filterdate(since, until)
	assert len(transformer.rows) == 2 and transformer.rows[0] == sample_row_data[0] # not sorted yet

def test_filter_since(sample_row_data):
	transformer = Transformer(sample_row_data)
	since = date(2027, 6, 2)
	transformer.filterdate(since, None)
	assert len(transformer.rows) == 1

def test_filter_until(sample_row_data):
	transformer = Transformer(sample_row_data)
	until = date(2005, 12, 31)
	transformer.filterdate(None, until)
	assert len(transformer.rows) == 0

def test_get_top_n_results(sample_row_data):
	transformer = Transformer(sample_row_data)
	transformer.get_top_n_results(-4)
	assert len(transformer.rows) == 4 and transformer.rows[0] == sample_row_data[0]
