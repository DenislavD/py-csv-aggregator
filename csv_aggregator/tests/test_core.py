from .. core import get_csv_in_dir, get_file_queue
import pytest
import os

PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__)) # one level up

def test_get_csv_in_dir_empty():
	path = os.path.join(PACKAGE_DIR, 'tests')
	result = get_csv_in_dir(path)
	assert result == [], 'Files other than .csv found'

def test_get_csv_in_dir_data():
	path = os.path.join(PACKAGE_DIR, 'data')
	result = set(get_csv_in_dir(path))

	full_data = { # set
		os.path.join(path, '2017-06 Journal.csv'), 
		os.path.join(path, '2017-2018 Journal.csv'), 
		os.path.join(path, '2019-2020 Journal.csv'), 
		os.path.join(path, 'INFO 2023.csv'), 
		os.path.join(path, '2017', '2017-07 Journal.csv'), 
		os.path.join(path, '2017', '2017-08 Journal date.csv'), 
		os.path.join(path, '2017', '2017-09 Journal.csv'), 
		os.path.join(path, '2017', '2017-10 Journal.csv'), 
		os.path.join(path, '2017', '04-05', '2017-04-05 Journal.csv'), 
		os.path.join(path, '2022', '2021-2022 Journal.csv'), 
	}
	assert result.issubset(full_data), 'Collected .csv file paths do not match the initial files structure'

def test_get_file_queue_file_and_dir():
	path = os.path.join(PACKAGE_DIR, 'data')
	args_path = ['2017-06 Journal.csv', 'data\\2017']
	result = get_file_queue(args_path)

	data = {
		os.path.join(path, '2017-06 Journal.csv'),
		os.path.join(path, '2017', '2017-07 Journal.csv'), 
		os.path.join(path, '2017', '2017-08 Journal date.csv'), 
		os.path.join(path, '2017', '2017-09 Journal.csv'), 
		os.path.join(path, '2017', '2017-10 Journal.csv'), 
		os.path.join(path, '2017', '04-05', '2017-04-05 Journal.csv'),
	}
	assert result.issubset(data), 'Additional files were found or files were renamed'


