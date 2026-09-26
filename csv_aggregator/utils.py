from fpdf import FPDF
from fpdf.fonts import FontFace
import json
import os
from datetime import datetime
from functools import partial

import pandas as pd

PACKAGE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(PACKAGE_DIR, 'fonts')
MAX_OUTPUT_ROWS = 100

def get_csv_in_dir(directory) -> list:
	files = []
	for root, *_ in os.walk(directory):
		for filename in os.listdir(root):
			filepath = os.path.join(root, filename)
			if os.path.isfile(filepath) and filename.lower().endswith('.csv'):
				files.append(filepath)
	return files


def get_file_queue(args_path) -> set:
	file_queue = set()
	for cur_path in args_path:
		scripts_dir = os.path.dirname(__file__)

		if os.path.exists(os.path.abspath(cur_path)):
			norm_path = os.path.abspath(cur_path)
		elif os.path.exists(os.path.join(scripts_dir, cur_path)):
			norm_path = os.path.join(scripts_dir, cur_path)
		else: # allow lazily not supplying data\ as parent folder
			norm_path = os.path.join(scripts_dir, 'data', cur_path)

		if os.path.isfile(norm_path):
			file_queue.add(norm_path)
		elif os.path.isdir(norm_path):
			file_queue.update(get_csv_in_dir(norm_path))
	return file_queue


def get_output_filename(args) -> str:
	base_name = f'Trading Summary {datetime.now().strftime("%Y%m%d_%H%M%S")}'
	base_path = os.path.join(PACKAGE_DIR, 'outputs', base_name)

	if args.since or args.until:
		base_path += f' {args.since or "min"}--{args.until or "max"}'
	if args.top_n:
		base_path += f' top{args.top_n}'
	if args.group_by:
		base_path += f' group-by-{args.group_by} agg-by-{args.agg_by}'
	return base_path


# factory creator
def get_serializer(format, output_filename):
	match format:
		case 'json': func = _serialize_json
		case 'pdf':  func = _serialize_pdf
		case _: 	 func = _serialize_json
	return partial(func, output_filename=output_filename)

# implementations/products
def _serialize_json(groups: pd.DataFrame | None, rows: pd.DataFrame, top_n: int, *, output_filename):
	output = {}

	if groups is not None:
		json_string = groups.to_json(orient='index')
		output['groups'] = json.loads(json_string)

	if top_n or rows.shape[0] <= MAX_OUTPUT_ROWS:
		rows.index = rows.index.strftime('%Y-%m-%d') # format row index
		rows = rows[~rows.index.duplicated()] # remove duplicated days (shouldn't be any)
		rows.begin = rows.begin.dt.strftime('%H:%M') # format begin time
		json_string = rows.to_json(orient='index')
		output['rows'] = json.loads(json_string)

	print(json.dumps(output, indent=4))
	with open(f'{output_filename}.json', 'w') as file:
		json.dump(output, file)


def _serialize_pdf(groups: pd.DataFrame | None, rows: pd.DataFrame, top_n: int, *, output_filename):
	# Start fpdf2 output
	pdf = PDFWithBackground(orientation='landscape')
	pdf.add_page()
	pdf.add_font('Tahoma', '', os.path.join(FONTS_DIR, 'Tahoma.ttf'), uni=True)
	pdf.add_font('Tahoma', 'B', os.path.join(FONTS_DIR, 'Tahomabd.ttf'), uni=True)
	headings_style = FontFace(fill_color=(67, 67, 67), color=(255, 255, 255), emphasis='BOLD')

	pdf.set_font('Tahoma', 'B', size=26)
	pdf.cell(text='Trading Summary report', center=True)
	pdf.ln(25)

	if groups is not None:
		pdf.set_font('Tahoma', 'B', size=16)
		pdf.cell(text='Aggregated data', center=True)
		pdf.ln(10) # adds vertical space
		pdf.set_font('Tahoma', size=12)

		groups = groups.reset_index().fillna('-').astype(str)
		table_data = [groups.columns.tolist()] + groups.values.tolist()
		with pdf.table(table_data, text_align='CENTER', headings_style=headings_style):
			...
		pdf.ln(30)

	if top_n or len(rows) <= MAX_OUTPUT_ROWS:
		pdf.set_font('Tahoma', 'B', size=16)
		pdf.cell(text='Daily data', center=True)
		pdf.ln(10)
		pdf.set_font('Tahoma', size=12)

		rows.begin = rows.begin.dt.strftime('%H:%M') # format begin time
		rows = rows.reset_index().fillna('-').astype(str)
		table_data = [rows.columns.map(str.capitalize).tolist()] + rows.values.tolist()
		with pdf.table(table_data, col_widths=(10, 10, 10, 60, 10), headings_style=headings_style,
			text_align=("CENTER", "CENTER", "CENTER", "LEFT", "CENTER")):
			...
		pdf.ln(20)

	pdf.cell(text='--- REPORT END ---', center=True)
	pdf.output(f'{output_filename}.pdf')


class PDFWithBackground(FPDF):
    def header(self):
        # Claude AI: This is called automatically at the start of each new page
        # The image is drawn first, so it's in the background
        self.image(os.path.join(PACKAGE_DIR, 'data', 'confidential_back.jpg'), x=0, y=0, w=self.w, h=self.h)