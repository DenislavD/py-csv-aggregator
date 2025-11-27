import logging
import os
import csv
from datetime import datetime, time
from collections import namedtuple

# dev only
import pprint

log = logging.getLogger(__name__)

class Extractor:
	data = [] # holds cleaned data for all files
	FINAL_HEADERS = 'day, trades, result, note, begin' # (hh:mm)
	DataRow = namedtuple('DataRow', FINAL_HEADERS)

	@classmethod
	def process(cls, file):
		rows = cls._ingest_file(file)
		mapping = cls._match_headers(rows)
		cls.data.extend(cls._load_data(mapping, rows))

		#pprint.pp(cls.data[:3])


	@classmethod
	def _ingest_file(cls, file): # CSV Ingestion
		rows = []
		try:
			with open(file, 'r', newline='', encoding='utf-8-sig') as csv_file:
				reader = csv.reader(csv_file)
				headers = False
				for row in reader:
					# skip first X rows that can be annotations
					if row[0] and (headers or 'Day' in row or '# trades' in row):
						headers = True
						rows.append(row)
		except FileNotFoundError:
			log.error(f'File "{file}" does not exist.')
		except csv.Error as e:
			raise SystemExit(f'CSV error in {filename}, line {reader.line_num}: {e}')

		log.info(f'File "{os.path.split(file)[1]}" ingested.')
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

		return mapping


	@classmethod
	def _load_data(cls, mapping, rows):
		_data = []
		for col in rows[1:]:
			_data.append(cls.DataRow(
				cls.parse_date(col[mapping['day']]),
				int(col[mapping['trades']] or 0),
				int(col[mapping['balance']] or 0),
				col[mapping['note']],
				cls.parse_time(col[mapping['begin']]) if mapping['begin'] else None,
			))
		return _data


	# Data normalization methods
	@classmethod
	def parse_date(cls, datestr) -> datetime:
		try:
			d = datetime.strptime(datestr, '%d-%m-%Y')
		except ValueError:
			parts = datestr.split('-') # 30 06 17 (year)
			if len(parts[2]) == 2:
				parts[2] = '20' + parts[2]
			parts.reverse()
			d = datetime(*map(int, parts))
		finally:
			return d


	@classmethod
	def parse_time(cls, timestr) -> time:
		try:
			t = time(*map(int, timestr.split(':')))
		except ValueError:
			t = None
		finally:
			return t

