<h3>Project 2 — CSV Aggregator (my chosen)</h3>

Purpose: aggregate data from many CSVs into summary outputs with configurable grouping and aggregations.

</br>
<h5>Minimal features:</h5>
<li>Accept input directory or file list; recursively find CSV files.</li>
<li>CLI options: --group-by (columns), --agg (sum, mean, count), --out-format (csv/json), --since/--until (date filters).</li>
<li>Robust parsing: handle different delimiters, header mismatches, missing values.</li>
<li>Tests: unit tests for parsing, grouping, and edge cases.</li>
<li>Logging: operations logged (files processed, rows aggregated, errors).</li>
<li>Packaging: installable with an entry point csv-agg.</li>
</br>
<h5>Stretch features:</h5>
<li>Concurrency: process multiple CSV files in parallel (I/O bound -> threads).</li>
<li>Dry-run and verbose modes.</li>
<li>Support for gzipped CSVs.</li>
</br>
Complexity writeup: include time/space complexity for main aggregation path (e.g., O(N) rows where N=sum of rows across files; memory depends on grouping cardinality).
Acceptance: README + example, pip install -e ., csv-agg --help, tests pass.

<h5>Current progress:</h5>
Argparse + one csv ingest

</br>

Run with:
<code>py csv-aggregator/__init__.py filenames [options]</code>


</br>
</br>