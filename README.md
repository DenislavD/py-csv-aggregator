<h3>CSV Aggregator pipeline</h3>

Purpose: aggregate data from many CSVs into summary outputs with configurable grouping and aggregations.</br>
Sample files are provided in the csv_aggregator/data directory.

</br>
<h5>Features:</h5>
<li>Accept input directory or file list; recursively find CSV files.</li>
<li>CLI options: --group-by (columns), --agg (sum, mean, count), --out-format (csv/json),
top-n (5/-100 top results), --since/--until (date filters).</li>
<li>Robust parsing: handle different delimiters, header mismatches, missing values.</li>
<li>Uses Pandas for DataFrame operations.</li>
<li>Logging: operations logged (files processed, rows aggregated, errors).</li>
<li>Packaging: installable with an entry point csv-agg.</li>
<li>Tests: unit tests for parsing, grouping, and edge cases.</li>

</br>
<h5>Complexity for main aggregation path:</h5>
<i>number of rows in all files = n</i>
<div>
	<b>Time complexity:</b>
	Initial read O(n) + headers O(1) + load_data O(n) + Transformer: sort O(n log n) + 
	group O(n) + aggregate O(n) + top_n filter sort O(n log n) + serialize O(50) = O(1) 
	<b>=> O(n log n)</b>
</div>
<div>
	<b>Space complexity:</b>
	base data O(n) + processed data O(n) + grouped data O(n) + 
	top_n results O(n) + serialized data O(n) 
	<b>=> O(n)</b></div>
</br>

<h5>Current status: Completed</h5>
Acceptance: README + example, pip install -e ., csv-agg --help, tests pass.</br>
</br>

<h5>Run with:</h5>
<code>git clone https://github.com/DenislavD/py-csv-aggregator.git
cd py-csv-aggregator
py -m venv venv_v2 # python3 for Linux
venv_v2\scripts\activate # Windows - CMD
venv_v2\scripts\Activate.ps1 # Windows - PowerShell
source venv_v2/bin/activate # Linux
pip install --upgrade pip  # Ensure pip >= 21.3 for editable installs
pip install -e .[test]
pytest
csv-agg --help
csv-agg data -g weekday
csv-agg "2017-06 Journal.csv" data\2017 -a sum -g year -t 5 -s 2017-05-01 -u 2017-12-31
</code>

</br>
</br>