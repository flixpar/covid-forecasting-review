import pandas as pd

rawdata = pd.read_csv("../rawdata/FinalSet_Cleaned_V2.csv", skiprows=1, keep_default_na=False)

data = rawdata.copy()
data = rawdata.drop(columns=["Misc Tags"])
data = data.rename(columns={
	"Title": "title",
	"Performance Eval Category": "performance_eval",
	"Performance Eval Subcategory": "performance_eval_sub",
	"Reader": "reader",
	"Data Categories": "data_cat",
	"Method": "method_cat",
	"Forecasting Window": "forecasting_window",
	"Additional Categories": "forecasting_window_sub",
	"Level": "region_level",
	"Target": "target",
	"Metrics": "metrics",
	"Uncertainty v2": "uncertainty",
	"Uncertainty?": "uncertainty_sub",
	"Broad Categories": "limitations",
})

data.reader = data.reader.map(lambda x: "further discussion" if "further discussion" in x else x)

for col in data.columns:
	data[col] = data[col].map(lambda x: x.encode("ascii", "ignore").decode("ascii"))
	data[col] = data[col].map(lambda x: x.replace(u"\xa0", ""))

data.title = data.title.map(lambda x: x.replace("&amp;", "&"))

doi_lookup_data = pd.read_csv("../rawdata/doi_lookup.csv")
doi_lookup = {row[1].title: row[1].doi for row in doi_lookup_data.iterrows()}

data.insert(1, "doi", data.title.map(lambda x: doi_lookup[x]))

data.sort_values(by=["title"], inplace=True)

data.to_csv("../data/finaldata.csv", index=False)
