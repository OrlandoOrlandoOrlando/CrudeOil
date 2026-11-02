#!.venv/bin/python

import argparse
import requests
import sqlite3

def parse_env(path_to_env):
    with open(path_to_env) as env:
        return {
            key.strip(): value.strip()
            for key, _, value in (
                pair.partition("=") for pair in env if not pair.strip().startswith("#")
            )
        }

def update_the_EIA_database(API_key, dest = "megadatabase"):
    url = "https://api.eia.gov/v2/"
    response = requests.get(url, params={
        "api_key": API_key
    })
    response.raise_for_status()
    return response.json()
    # con = sqlite3.connect(dest)

def update_the_EDGAR_database(dest = "megadatabase"):
    con = sqlite3.connect(dest)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_env")
    args = parser.parse_args()
    env = parse_env(args.path_to_env)
    print(update_the_EIA_database(env["EIA_API_KEY"]))