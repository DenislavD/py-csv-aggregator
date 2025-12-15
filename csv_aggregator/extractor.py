import logging
import os
import csv
from datetime import date, time, timedelta
from collections import namedtuple

log = logging.getLogger('csv_aggregator.extractor')

class Extractor:
	data = [] # holds cleaned data for all files
	FINAL_HEADERS = ['day', 'trades', 'result', 'note', 'begin'] # (hh:mm)
	DataRow = namedtuple('DataRow', FINAL_HEADERS)
	_last_date = None

	@classmethod
	def process(cls, file):
		rows = cls._ingest_file(file)
		mapping = cls._match_headers(rows)
		cls.data.extend(cls._load_data(mapping, rows))


	@classmethod
	def _ingest_file(cls, file): # CSV Ingestion
		rows = []
		with open(file, 'r', newline='', encoding='utf-8-sig') as csv_file:
			reader = csv.reader(csv_file)
			headers = False
			for row in reader:
				# skip first X rows that can be annotations
				if row[0] and (headers or 'Day' in row or '# trades' in row):
					headers = True
					rows.append(row)

		log.info(f'File "{os.path.split(file)[1]}" ingested with {len(rows)-1} rows.')
		return rows


	@classmethod
	def _match_headers(cls, rows):
		mapping = {
			'day': None,
			'trades': None,
			'balance': None,
			'note': None,
			'begin': None,
		}
		for k, header in enumerate(rows[0]):
			for search_term in mapping.keys():
				if len(header) < 15 and search_term in header.lower():
					if mapping[search_term] == None: # don't overwrite if already found
						mapping[search_term] = k
		
		for key in ('day', 'trades', 'balance'):
			if mapping[key] is None:
				raise KeyError(f'Header {key} was not found. Please adjust the source file. Exiting program.')
		return mapping


	@classmethod
	def _load_data(cls, mapping, rows):
		_data = []
		for col in rows[1:]:
			if col[mapping['trades']]: # drop weekends and non-trading days
				_data.append(cls.DataRow(
					cls.parse_date(col[mapping['day']]),
					int(col[mapping['trades']] or 0),
					int(col[mapping['balance']] or 0),
					col[mapping['note']],
					cls.parse_time(col[mapping['begin']]) if mapping['begin'] else None,
				))
		return _data


	@classmethod
	def reset(cls):
		cls.data = []


	# Data normalization methods
	@classmethod
	def parse_date(cls, datestr) -> date:
		# target is datetime.strptime(datestr, '%d-%m-%Y'), but
		# default is 31-02-17 , could be only 29-02 as well, so:
		parts = datestr.split('-')
		if len(parts) < 2: # fatal mismatch, use fallback
			return cls._last_date + timedelta(days=1)
		if len(parts) < 3:
			parts.append(str(cls._last_date.year))
		if len(parts[2]) == 2:
			parts[2] = '20' + parts[2]
		if len(parts[2]) != 4:
			parts[2] = cls._last_date.year # fallback to last seen year
		parts.reverse()
		cls._last_date = date(*map(int, parts))
		return cls._last_date


	@classmethod
	def parse_time(cls, timestr) -> time | None:
		parts = timestr.split(':')
		if len(parts) < 2:
			return None;
		return time(*map(int, parts))

