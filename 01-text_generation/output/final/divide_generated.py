#import required modules
import os
import copy
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.utils import logging
import sys
import json

#ensures no connexion to internet is made (in our run the cluster is directly disconnected)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"


#used to split the generated text between the prompt, the cot, and the final answer
def split_generated_text(element):
	#make a copy to work on it
	new_element = copy.deepcopy(element)

	#split on the <|start|>assistant<|channel|>analysis and extract the lft part which is the prompt
	new_element["text_prompt"] = new_element["text"].split("<|start|>assistant<|channel|>analysis")[0]

	#check if there is a final answer
	#if this is the case, split on <|start|>assistant<|channel|>analysis, take the right part, and then split on <|start|>assistant<|channel|>final and take the left part (COT)
	#and then does the same with the right part (FINAL)
	#Otherwise extract the COT and put "" for the final answer
	#In every case add the tokens removed by the split back
	if "<|start|>assistant<|channel|>final" in new_element["text"]:
		new_element["text_cot"] = "<|start|>assistant<|channel|>analysis" + new_element["text"].split("<|start|>assistant<|channel|>analysis")[1].split("<|start|>assistant<|channel|>final")[0]
		new_element["text_final"] = "<|start|>assistant<|channel|>final" + new_element["text"].split("<|start|>assistant<|channel|>analysis")[1].split("<|start|>assistant<|channel|>final")[1]
	else:
		new_element["text_cot"] = "<|start|>assistant<|channel|>analysis" + new_element["text"].split("<|start|>assistant<|channel|>analysis")[1].split("<|start|>assistant<|channel|>final")[0]
		new_element["text_final"] = ""
	return new_element

#retrieve all json files that have output in the name, and that do not have temp or new in their name
def retrieve_json_file(base_path):
        files_to_analyze = []
        for file in os.listdir(base_path):
                if ("output" in file and "temp" not in file and "new" not in file):
                        files_to_analyze.append(f"{base_path}/{file}")

        return files_to_analyze

#apply the first fct on all the elements of the json and count the tokens for the prompt cot and final
def apply_split_and_count_on_json(json_data,tokenizer):
	new_json_data = []
	for element in json_data:
		#split the text
		new_element = split_generated_text(element)

		#count the tokens for each part of the generated text
		#Note that we need to add <|start|>assistant to the prompt (generation tokens)
		#and we need to remove it from the cot
		#This is only done for the token counting and to be in adequation with the token counting made during the generation
		new_element["count_tokens_prompt"] = count_tokens(tokenizer,new_element["text_prompt"] + "<|start|>assistant")
		temp = new_element["text_cot"].replace("<|start|>assistant","")
		new_element["count_tokens_cot"] = count_tokens(tokenizer,temp)
		new_element["count_tokens_final"] = count_tokens(tokenizer,new_element["text_final"])
		new_json_data.append(new_element)

	return new_json_data

#counts tokens of a str given as parameter
def count_tokens(tokenizer,element_to_tokenize):

	#encode the text
	inputs = tokenizer.encode(
	element_to_tokenize,
	return_tensors="pt",
	)

	#gets the number of tokens
	return inputs.shape[1]

if __name__=="__main__":
	#load the tokenizer
	tokenizer = AutoTokenizer.from_pretrained("openai/gpt-oss-20b", device_map="auto", torch_dtype="auto", local_files_only=True)

	#retrieve files to analyze
	files_to_analyze = retrieve_json_file(".")

	#parse all the files
	for file in files_to_analyze:
		#load the json, and apply the fct to split the text and count the tokens in these new sub parts of the text
		with open(file,"r") as f:
			json_data = json.load(f)
		new_json_data = apply_split_and_count_on_json(json_data,tokenizer)

		#save the file with another name (add _new.txt)
		new_file_name = file.replace(".txt","_new.txt")
		with open(new_file_name,"w") as nf:
			json.dump(new_json_data,nf,indent=4)
