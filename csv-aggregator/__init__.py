"""
CSV Aggregator - A tool for aggregating CSV data.

This tool collects provided .csv files/directories and gets my trade data by days from them.
Afterwards, it parses the data and summarizes it by given criteria in JSON/PDF format.
"""

__version__ = '0.1.0'
__author__ = 'Denislav Dimitrov @DenislavD'

# Import main classes/functions you want users to access directly
#from .core import ..
#from .utils import HelperClass

# Define what's available when using "from csv_agg import *"
__all__ = [
	'MainClass',
	'main_function',
	'utility_function',
]

