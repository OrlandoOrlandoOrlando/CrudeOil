#!.venv/bin/python

import requests
import argparse
import requests
import sqlite3
import json

parser = argparse.ArgumentParser()
parser.add_argument("path_to_env")
args = parser.parse_args()
database_con = sqlite3.connect("megadatabase")

def parse_env(path_to_env):
	with open(path_to_env) as env:
		return {
			key.strip(): value.strip()
			for key, _, value in (
				pair.partition("=") for pair in env if not pair.strip().startswith("#")
			)
		}
env = parse_env(args.path_to_env)

def fetch_EIA_data(route, **query_params):
	url = "https://api.eia.gov/v2/"
	url += route
	url += "/data"
	response = requests.get(url, params={"api_key": env["EIA_API_KEY"], **query_params})
	response.raise_for_status()
	return response.json()

def init_database():
	database_con.execute("""
		CREATE TABLE IF NOT EXISTS http_response_cache (
			url TEXT,
			params TEXT,
			response TEXT,
			PRIMARY KEY (url, params)
		)
	""")
init_database()

def store_http_response(route, params, response):
	params = json.dumps(params, sort_keys=True)
	response = json.dumps(response)

	database_con.execute("""
		INSERT OR REPLACE INTO http_response_cache (url, params, response)
		VALUES (?, ?, ?)
	""", (route, params, response))

	database_con.execute("""
		DELETE FROM http_response_cache
		WHERE rowid NOT IN (
			SELECT rowid FROM http_response_cache
			ORDER BY rowid DESC
			LIMIT 100
		)
	""")

def recall_http_response(route, params):
	params = json.dumps(params, sort_keys=True)
	result = database_con.execute("""
		SELECT response FROM http_response_cache
		WHERE url = ? AND params = ?
	""", (route, params)).fetchone()

	return json.loads(result[0]) if result else None

def commit_and_close_database():
	database_con.commit()
	database_con.close()

def test_database_con():
	route = "petroleum/sum/sndw"
	params = {
		"frequency": "weekly",
		"data[0]": "value",
		"start": "2026-01-01",
		"end": "2026-01-07",
		"sort[0][column]": "period",
		"sort[0][direction]": "asc"
	}

	response = fetch_EIA_data(route, **params)
	store_http_response(route, params, response)
	assert response == recall_http_response(route, params)

def values_units_from(response):
	entries = response["response"]["data"]
	return [float(entry["value"]) for entry in entries], [entry["units"] for entry in entries]