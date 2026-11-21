#!.venv/bin/python

import main
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

route = "petroleum/sum/snd/data"
params = {
	"frequency": "monthly",
	"data[0]": "value",
	"facets[duoarea][]": "NUS", # United States nationally
	"facets[product][]": "EP00", # Total petroleum products
	"facets[process][]": "VPP", # Product supplied
	"start": "1920-01",
	"end": "2005-08",
	"sort[0][column]": "period",
	"sort[0][direction]": "asc",
	"offset": 0,
	"length": 5000
}

# response = main.fetch_EIA_data(route, **params)
# main.store_http_response(route, params, response)
# main.commit_and_close_database()
response = main.recall_http_response(route, params)


# credit to ChatGPT
values, units = main.values_units_from(response)
# print(units)

data = response["response"]["data"]

dates = [entry["period"] for entry in data]

# plt.figure(figsize=(14, 6))
# plt.plot(dates, values, marker=".", markersize=3)

# plt.xlabel("Date")
# plt.ylabel(f"Product Supplied ({units[0]})")
# plt.title("U.S. Total Petroleum Product Supplied")
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.tight_layout()
# plt.show()

values, units = main.values_units_from(response)
data = response["response"]["data"]

print("Number of records:", len(data))
print("Number of values:", len(values))
print("Units:", units)

for entry, value in list(zip(data, values))[:20]:
    print(entry["period"], entry["value"], value)

print("\nLast 20 records:")
for entry, value in list(zip(data, values))[-20:]:
    print(entry["period"], entry["value"], value)

# Filter data between January 1981 and December 1982
filtered = [
    (datetime.strptime(entry["period"], "%Y-%m"), value)
    for entry, value, unit in zip(data, values, units)
    if unit == "MBBL/D"
#     if "1981-01" <= entry["period"] <= "1982-12"
#     and unit == "MBBL/D"
]

dates, values_filtered = zip(*filtered)

# Plot
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(dates, values_filtered, marker=".", markersize=3)

ax.set_xlabel("Date")
ax.set_ylabel(f"Product Supplied ({units[0]})")
ax.set_title("U.S. Total Petroleum Product Supplied (1981–1982)")

# Display yearly date labels
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45)
ax.grid(True)

fig.tight_layout()
plt.show()