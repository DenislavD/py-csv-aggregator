from .. extractor import Extractor
import pytest
import os
from datetime import date

PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(PACKAGE_DIR, 'data', '2017-06 Journal.csv')

# row:4 data from 2017-06 Journal.csv:
@pytest.fixture
def sample_row_data():
	return [
		['Day', '# trades', '~ Balance', 'Notes', '', '', '', 'IDEA: Set 6-stop default, use more M and MR trades, a few T and remove TR ?', '', '', '', '', '', '', '', '', '', '', '', ''], 
		['30-06-17', '1', '-15', 'missed trades before 18:00 . Need to be ready to ACT', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Trend', 'Act on LOW RISK points, then patience', ''], 
		['02-06-27', '0', '0', 'no market data', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Momentum', '6-ticks stop, no so-so trades, take profits', ''], 
		['03-06-17', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Scalp / MR', 'Reverse action for most "momentums", take profits', ''], 
	]

def test_ingest_file_skip_annotation_headers(sample_row_data):
	result = Extractor._ingest_file(file_path)
	assert sample_row_data == result[:4]

def test_match_headers_standard(sample_row_data):
	mapping = Extractor._match_headers(sample_row_data)
	assert mapping == {'day': 0, 'trades': 1, 'balance': 2, 'note': 3, 'begin': None}

# random data tests start
def test_match_headers_mixed():
	mixed = [
		['trades', 'begin', '', '', '', '', '', '', '', '', '', 'Day','notes', '', 'balance', '', '', 'IDEA:r emove TR ?','', ''], 
	]
	mapping = Extractor._match_headers(mixed)
	assert mapping == {'day': 11, 'trades': 0, 'balance': 14, 'note': 12, 'begin': 1}, 'Failure when matching mixed headers'

def test_match_headers_missing():
	missing = [
		['', 'begin', '', '', '', '', '', '', '', '', '', 'Day','notes', '', 'balance', '', '', 'IDEA:r emove TR ?','', ''], 
	]
	with pytest.raises(KeyError, match='Header .* was not found'): # day, trades or balance not found
		Extractor._match_headers(missing)

def test_parse_date_short_year():
	parsed = Extractor.parse_date('05-01-23')
	assert parsed == date(2023, 1, 5), 'Failure converting \'23 to 2023'

def test_parse_date_year_fallback():
	Extractor._last_date = date(2025, 12, 15)
	parsed = Extractor.parse_date('05-01')

	assert parsed == date(2025, 1, 5), 'Failure falling back to last known year'

def test_parse_date_fatal_mismatch():
	Extractor._last_date = date(2025, 12, 15)
	parsed = Extractor.parse_date('3nov')

	assert parsed == date(2025, 12, 16), 'Failure falling back to last day + 1'

def test_parse_time_empty():
	assert Extractor.parse_time('') is None, 'Failure parsing empty time string'
