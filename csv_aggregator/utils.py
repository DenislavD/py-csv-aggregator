from fpdf import FPDF
from fpdf.fonts import FontFace
import logging
import json
import string
import os
from datetime import datetime

PACKAGE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(PACKAGE_DIR, 'fonts')
outputs_filename = os.path.join(PACKAGE_DIR, 'outputs', f'Csv-agg {datetime.now().strftime('%Y%m%d_%H%M%S') } ')


# factory creator
def get_serializer(format, name_string):
	global outputs_filename
	outputs_filename += name_string.strip()
	match format:
		case 'json':
			func = _serialize_json
		case 'pdf': 
			func = _serialize_pdf
		case _:
			func = _serialize_json
	return func


# implementations/products
def _serialize_json(groups, rows, top_n):
	output_groups = []
	output_rows = []
	if groups:
		output_groups = [{'group': item['group'], 'data': item['outputs']} for item in groups]
	if top_n or len(rows) <= 50:
		for row in rows:
			output_rows.append({
				'day': row.day.strftime('%Y-%m-%d'),
				'trades': row.trades,
				'result': row.result,
				'note': row.note
			})
	output = [output_groups, output_rows]
	print(json.dumps(output, indent=4))
	with open(f'{outputs_filename}.json', 'w') as file:
		json.dump(output, file)


def _serialize_pdf(groups, rows, top_n):
	if groups:
		keys = groups[0]['outputs'].keys()
		output_groups = [['Group', *map(lambda x: string.capwords(x.replace('-', ' '), ' '), keys)]]
		for item in groups:
			output_groups.append(map(str, [item['group'], *item['outputs'].values()] ))

	output_rows = None
	if top_n or len(rows) <= 50:
		output_rows = [['Day', 'Result', 'Trades', 'Note']]
		for row in rows:
			output_rows.append([row.day.strftime('%Y-%m-%d'), row.result, row.trades, row.note])

	# Data serialized, start fpdf2 output
	pdf = PDFWithBackground(orientation='landscape')
	pdf.add_page()
	pdf.add_font('Tahoma', '', os.path.join(FONTS_DIR, 'Tahoma.ttf'), uni=True)
	pdf.add_font('Tahoma', 'B', os.path.join(FONTS_DIR, 'Tahomabd.ttf'), uni=True)
	headings_style = FontFace(fill_color=(67, 67, 67), color=(255, 255, 255), emphasis='BOLD')

	pdf.set_font('Tahoma', 'B', size=26)
	pdf.cell(text='Trading Summary report', center=True)
	pdf.ln(25)

	if groups:
		pdf.set_font('Tahoma', 'B', size=16)
		pdf.cell(text='Aggregated data', center=True)
		pdf.ln(10) # adds vertical space

		pdf.set_font('Tahoma', size=12)
		with pdf.table(text_align='CENTER', headings_style=headings_style) as table:
			for data_row in output_groups:
				row = table.row()
				for datum in data_row:
					row.cell(datum)
		pdf.ln(30)

	if output_rows:
		pdf.set_font('Tahoma', 'B', size=16)
		pdf.cell(text='Daily data', center=True)
		pdf.ln(10)

		pdf.set_font('Tahoma', size=12)
		with pdf.table(col_widths=(10, 10, 10, 70), headings_style=headings_style, \
			text_align=("CENTER", "CENTER", "CENTER", "LEFT")) as table2:
			for data_row in output_rows:
				row = table2.row()
				for datum in data_row:
					row.cell(str(datum))

	pdf.ln(20)
	pdf.cell(text='--- REPORT END ---', center=True)
	pdf.output(f'{outputs_filename}.pdf')


class PDFWithBackground(FPDF):
    def header(self):
        # Claude AI: This is called automatically at the start of each new page
        # The image is drawn first, so it's in the background
        self.image(os.path.join(PACKAGE_DIR, 'data', 'confidential_back.jpg'), x=0, y=0, w=self.w, h=self.h)