("""Utilities to load CSVs from a folder into pandas DataFrames.

Usage: run this module or import `load_csvs_from_folder`.
""")

import os
import glob
import pandas as pd


def _csv_instrument_key(path):
	basename = os.path.splitext(os.path.basename(path))[0]
	if "_" in basename:
		return basename.split("_", 1)[0]
	return basename


def load_csvs_from_folder(folder_path="data"):
	"""Recursively load all CSV files under `folder_path` into a dict of DataFrames.

	Keys are the instrument names derived from the CSV filenames.
	For example, `CRUDEOILM_historical_data.csv` becomes `CRUDEOILM`.

	Returns:
		dict: {instrument_name: pandas.DataFrame}
	"""
	folder = os.path.abspath(folder_path)
	if not os.path.isdir(folder):
		raise FileNotFoundError(f"Folder not found: {folder}")

	# Find CSVs recursively
	csv_paths = sorted(glob.glob(os.path.join(folder, "**", "*.csv"), recursive=True))
	dataframes = {}
	for path in csv_paths:
		key = _csv_instrument_key(path)
		try:
			# Detect if a 'date' column exists (case-insensitive) and parse it
			header_cols = pd.read_csv(path, nrows=0).columns.tolist()
			lower_cols = [c.lower() for c in header_cols]
			parse_dates = [header_cols[i] for i, c in enumerate(lower_cols) if c == 'date'] or None
			if parse_dates:
				df = pd.read_csv(path, parse_dates=parse_dates)
			else:
				df = pd.read_csv(path)
			dataframes[key] = df
		except Exception as e:
			print(f"Failed to load {path}: {e}")
	return dataframes


def load_req_csvs(folder_path="data", instruments=None):
	"""Load only CSVs whose file name matches one of the provided instruments.

	Args:
		folder_path (str): root folder to search (recursively).
		instruments (list[str]): list of instrument names to filter by. Matching is
			case-insensitive and checks if an instrument string appears anywhere in
			the CSV filename, such as `CRUDEOILM_historical_data.csv`.

	Returns:
		dict: {instrument_name: pandas.DataFrame} for matching files.
	"""
	if not instruments:
		raise ValueError("`instruments` must be a non-empty list of instrument names")

	# normalize instruments for case-insensitive matching
	inst_upper = [str(i).upper() for i in instruments]

	folder = os.path.abspath(folder_path)
	if not os.path.isdir(folder):
		raise FileNotFoundError(f"Folder not found: {folder}")

	csv_paths = sorted(glob.glob(os.path.join(folder, "**", "*.csv"), recursive=True))
	dataframes = {}
	for path in csv_paths:
		key = _csv_instrument_key(path)
		key_upper = key.upper()

		# include file if any instrument name is found in the CSV filename
		if not any(inst in key_upper for inst in inst_upper):
			continue

		try:
			header_cols = pd.read_csv(path, nrows=0).columns.tolist()
			lower_cols = [c.lower() for c in header_cols]
			parse_dates = [header_cols[i] for i, c in enumerate(lower_cols) if c == 'date'] or None
			if parse_dates:
				df = pd.read_csv(path, parse_dates=parse_dates)
			else:
				df = pd.read_csv(path)
			dataframes[key] = df
		except Exception as e:
			print(f"Failed to load {path}: {e}")

	return dataframes


def filter_close_price(df):
	"""Filter the DataFrame to include only 'date' and 'close' columns, if they exist."""
	cols = df.columns.str.lower()
	date_col = df.columns[cols == 'date'][0] if 'date' in cols else None
	close_col = df.columns[cols == 'close'][0] if 'close' in cols else None

	if date_col and close_col:
		return df[[date_col, close_col]].rename(columns={date_col: 'date', close_col: 'close'})
	else:
		print("Warning: 'date' or 'close' column not found. Returning original DataFrame.")
		return df


if __name__ == "__main__":
	dfs = load_req_csvs("data", instruments=['NIFTY', 'BANKNIFTY', 'CRUDEOILM', 'GOLDGUINEA', 'NATGASMINI', 'SILVERMIC', 'USDINR', 'EURINR'])
	print(f"Loaded {len(dfs)} CSVs: {list(dfs.keys())}")

