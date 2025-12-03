import json
import os

# fonction used to check if the sampling happened correctly
def check_no_sampling(inferences):

	#define an indicator for sampling and no sampling
	no_sample_okay = True
	sample_okay = True

	#filter samples with sampling and without sampling
	no_samples = [sample for sample in inferences if not sample["do_sample"]]
	samples = [sample for sample in inferences if sample["do_sample"]]

	#filter based on the reasoning level
	no_sample_low = [sample for sample in no_samples if sample["reasoning"]=="low"]
	no_sample_medium = [sample for sample in no_samples if sample["reasoning"]=="medium"]
	no_sample_high = [sample for sample in no_samples if sample["reasoning"]=="high"]

	sample_low = [sample for sample in samples if sample["reasoning"]=="low"]
	sample_medium = [sample for sample in samples if sample["reasoning"]=="medium"]
	sample_high = [sample for sample in samples if sample["reasoning"]=="high"]


	#for each rwsoning level, there must be 2 without sampling and 4 with sampling
	#if this is not the case, print something and put the indicator to False
	if not ((len(no_sample_low)== 2 and len(no_sample_medium) ==2 and len(no_sample_high) ==2) and (len(sample_low)== 4 and len(sample_medium) ==4 and len(sample_high) ==4)) :
		print("Problem with the number of samples")
		no_sample_okay = False
		sample_okay = False

	#parse the elements with no sampling, check that they are the same, turn the indicator to False if this is not the case
	for i in [no_sample_low,no_sample_medium,no_sample_high]:
		for j in range(len(i)):
			no_sample_okay = no_sample_okay and (i[0]["text"]==i[j]["text"])

	#parse the elements with sampling, check that they are different, turn the indicator to False if this is not the case
	for i in [sample_low,sample_medium,sample_high]:
		for j in range(len(i)):
			for k in range(len(i)):
				if j==k:
					pass
				else:
					sample_okay = sample_okay and (i[j]["text"] != i[k]["text"])

	#return alright if both indicators are True (everything went fine) and return that there is a problem otherwise
	if no_sample_okay and sample_okay:
		return "Alright"
	else:
		return "There is a problem"

#parse all files in a folder and retrieve the name of the files with output in their name, but no temp or new in their name
def retrieve_json_file(base_path):
	files_to_analyze = []
	for file in os.listdir(base_path):
		if ("output" in file and "temp" not in file and "new" not in file):
			files_to_analyze.append(f"{base_path}/{file}")

	return files_to_analyze


if __name__=="__main__":
	#retrieve the file names
	files_to_analyze = retrieve_json_file("./output/final/redo") + retrieve_json_file("./output/final")

	#parse all the files
	for file in files_to_analyze:
		#load the file and check if the sampling was good
		with open(file,"r",encoding="utf-8") as f:
			inferences = json.load(f)
		#display the result
		print(f"{file} -> {check_no_sampling(inferences)}")
