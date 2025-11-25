import logging
import csv

log = logging.getLogger(__name__)

class DailyData:
	def __init__(self):
		self.rows = []

	def __str__(self):
		return f'x'

	def ingest_dir(self, ):
		...

	def ingest_file(self, file): # CSV Ingestion
		try:
			with open(file, 'r', newline='', encoding='utf-8-sig') as csv_file:
				reader = csv.reader(csv_file)
				headers = False
				for row in reader:
					# skips first X rows that are annotations
					if headers or 'Day' in row or '# trades' in row:
						headers = True
						self.rows.append(row)
		except FileNotFoundError:
			log.error(f'File "{file}" does not exist.')
		except csv.Error as e:
			raise SystemExit(f'CSV error in {filename}, line {reader.line_num}: {e}')


	def match_headers(self):
		...
		# headers
		# for r in data[:5]:
		# 	print('Len', len(r), r)

# Data normalization
