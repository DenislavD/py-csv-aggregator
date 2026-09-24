import logging
import os
import csv
from datetime import date, time, timedelta
from collections import namedtuple

log = logging.getLogger('csv_aggregator.extractor')

class Extractor:
	"""Parses a CSV file and returns a list of namedtuple data.
	Intentionally training on class- and static methods instead of instances
	"""
	FINAL_HEADERS = ['day', 'trades', 'result', 'note', 'begin'] # (hh:mm)
	DataRow = namedtuple('DataRow', FINAL_HEADERS)

	@classmethod
	def process(cls, file):
		rows: list = cls._ingest_file(file)
		mapping: dict = cls._match_headers(rows)
		clean_data: list[DataRow] = cls._format_data(mapping, rows)
		return clean_data


	@classmethod
	def _ingest_file(cls, file) -> list:
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
	def _match_headers(cls, rows) -> dict:
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
	def _format_data(cls, mapping, rows) -> list[DataRow]:
		data = []
		last_known_date = date(2017, 10, 1) # default, shouldn't actually appear
		for col in rows[1:]:
			if col[mapping['trades']]: # drop weekends and non-trading days
				data.append(cls.DataRow(
					cls.parse_date(col[mapping['day']], last_known_date),
					int(col[mapping['trades']] or 0),
					int(col[mapping['balance']] or 0),
					col[mapping['note']],
					cls.parse_time(col[mapping['begin']]) if mapping['begin'] else None,
				))
				last_known_date = data[-1].day
		return data


	# Data normalization methods
	@staticmethod
	def parse_date(datestr, last_known_date: date) -> date:
		# target is datetime.strptime(datestr, '%d-%m-%Y'), but
		# default is 31-02-17 , could be only 29-02 as well, so:
		parts = datestr.split('-')
		if len(parts) < 2 or len(parts) > 3 or not ''.join(parts).isdecimal():
			return last_known_date + timedelta(days=1) # fatal mismatch, use fallback
		if len(parts) == 2:
			parts.append(str(last_known_date.year)) # year is missing
		if len(parts[2]) == 2:
			parts[2] = '20' + parts[2]
		if len(parts[2]) != 4:
			parts[2] = last_known_date.year # fallback to last seen year
		parts.reverse()
		return date(*map(int, parts))


	@staticmethod
	def parse_time(timestr) -> time | None:
		parts = timestr.split(':')
		if len(parts) < 2:
			return None;
		return time(*map(int, parts))

