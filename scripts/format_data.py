import pandas as pd

rawdata = pd.read_excel("../rawdata/FinalSet_Cleaned.xlsx", skiprows=1, keep_default_na=False, engine="openpyxl")

data = rawdata.copy()
data = rawdata.drop(columns=["Misc Tags"])
data = data.rename(columns={
	"Title": "title",
	"Performance Eval Category": "performance_eval",
	"Performance Eval Subcategory": "performance_eval_sub",
	"Reader": "reader",
	"Data Categories": "data_cat",
	"Category": "method_cat",
	"Families": "objective_cat",
	"Level": "region_level",
	"Target	Metrics": "metrics",
	"Uncertainty v2": "uncertainty",
	"Uncertainty?": "uncertainty_sub",
	"Broad Categories": "limitations",
})

data.reader = data.reader.map(lambda x: "further discussion" if "further discussion" in x else x)

for col in data.columns:
	data[col] = data[col].map(lambda x: x.encode("ascii", "ignore").decode("ascii"))
	data[col] = data[col].map(lambda x: x.replace(u"\xa0", ""))

data.title = data.title.map(lambda x: x.replace("&amp;", "&"))

data.to_csv("../data/finaldata.csv", index=False)
