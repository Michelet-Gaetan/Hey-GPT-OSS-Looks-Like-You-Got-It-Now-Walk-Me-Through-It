#import required modules
import os
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.utils import logging
import sys
import json

#ensures no connexion to internet is made (in our run the cluster is directly disconnected)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

#set transformers verbosity to information
logging.set_verbosity_info()

#print a given message and add the current timestamp
def custom_log(message):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - {message}")


#Generate text based on the parameters given:
#model_name: name of the model used
#model: the model object itself
#tokenizer: the tokenizer object itself
#task: the name of the task tested
#role: the role given to the model
#prompt: the prompt used to generate the text
#reasoning: the level of reason used by the model
#temperature: the temperature used for inferences generated with sampling activated
#iterations: the number of iterations done when sampling is activated
def use_model(model_name,model,tokenizer,task,role,prompt,reasoning,temperatures,iterations,max_new_tokens):

	#setup the prompt
	messages = [{"role": "user", "content": prompt},]

	#structure the user prompt with the chat template
	#Here the role the model will take and the reasoning level are set
	inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	return_tensors="pt",
	return_dict=True,
	reasoning_effort=reasoning,
	model_identity=role,
	).to(model.device)

	tok_before = inputs["input_ids"].shape[1]

	#prepare the datastructure that will store the inferences and metadata
	inferences_and_metadata = []

	#iter over the different temperatures (in our case there is only 0.7)
	for temperature in temperatures:

		#does it for each required iteration
		for index in range(iterations):

			#time before inference
			before = datetime.now()

			#inference of the model
			#here the sampling is activated and the temperature is set
			outputs = model.generate(
			**inputs,
			max_new_tokens=max_new_tokens,
			do_sample=True,
			temperature=temperature
			)

			#time after the inference and then compute the inference time
			after = datetime.now()
			duration = (after-before).total_seconds()

			tok_after = outputs.shape[1]
			tok_generated = tok_after-tok_before
			#determines if the generation was finished due to a stop token or due to the limit of token accepted / retrieves the last token id
			is_finished = (outputs[0][-1].item()==tokenizer.eos_token_id)
			last_token_id = outputs[0][-1].item()

			#decode the output in readable format
			out = tokenizer.decode(outputs[0])

			#store the inference and the related metadata
			json_temp={"task": task,"model_name": model_name, "prompt": prompt,"reasoning": reasoning,"temperature": temperature, "do_sample": True, "index": index+1, "text": out, "last_token_id":last_token_id, "is_finished":is_finished, "duration":duration,"tokens_before":tok_before,"tokens_after":tok_after,"tokens_generated":tok_generated}

			#add it to the data structure
			inferences_and_metadata.append(json_temp)

	for i in range(2):
		#time before inference
		before = datetime.now()

		#inference of the model
		#here the sampling is deactivated
		outputs = model.generate(
		**inputs,
		max_new_tokens=max_new_tokens,
		do_sample=False,
		)

		#time after the inference and then compute the inference time
		after = datetime.now()
		duration = (after-before).total_seconds()

		#determines if the generation was finished due to a stop token or due to the limit of token accepted / retrieves the last token id
		is_finished = (outputs[0][-1].item()==tokenizer.eos_token_id)
		last_token_id = outputs[0][-1].item()

		tok_after = outputs.shape[1]
		tok_generated = tok_after-tok_before

		#decode the output in readable format
		out = tokenizer.decode(outputs[0])

		#store the inference and the related metadata
		json_temp={"task": task,"model_name": model_name, "prompt": prompt,"reasoning": reasoning,"temperature": 0, "do_sample": False, "index": i+1, "text": out, "last_token_id":last_token_id, "is_finished":is_finished, "duration" : duration,"tokens_before":tok_before,"tokens_after":tok_after,"tokens_generated":tok_generated}

		#add it to the data structure
		inferences_and_metadata.append(json_temp)

	return inferences_and_metadata

#iter over the different parameters, load the model and tokenizer, and generate the text
def iter_over_var_and_use_model(task,role,prompt,model_names,reasonings,temperatures,iterations, file_path,max_new_tokens):
	inferences_and_metadata = []

	for model_name in model_names:
		#for each model load the tokenizer and the model
		tokenizer = AutoTokenizer.from_pretrained(model_name, device_map="auto", torch_dtype="auto", local_files_only=True)
		model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype="auto", local_files_only=True)

		for reasoning in reasonings:
			#run the inference and store the results (inference and related metadata)
			inferences_and_metadata += use_model(model_name,model,tokenizer,task,role,prompt,reasoning,temperatures,iterations,max_new_tokens)

			custom_log(f"generation finished for: {task} - {model_name} - {reasoning}")

			#stores it in a temp file for monitoring
			with open(f"{file_path}_{task}_temp.txt","w",encoding='utf-8') as f:
				json.dump(inferences_and_metadata,f,indent=4)

	#stores it in a file in its final form, add the datetime to distinguish between different runs
	now = datetime.now()
	timestamp = now.strftime("%Y_%m_%d__%H_%M_%S")
	with open(f"{file_path}_{task}_{timestamp}.txt","w",encoding='utf-8') as f:
		json.dump(inferences_and_metadata,f,indent=4)


#retrieve the pieces of the prompt that are stored in txt files
def get_prompt_components(base_path):
	with open(f"{base_path}/role.txt","r") as f:
		role = f.read()
	with open(f"{base_path}/input.txt","r") as f:
		input = f.read()
	with open(f"{base_path}/context.txt","r") as f:
		context = f.read()
	with open(f"{base_path}/instruction.txt","r") as f:
		instruction = f.read()
	with open(f"{base_path}/output_format.txt","r") as f:
		output_format = f.read()
	return (role,context,input,instruction,output_format)

#takes elements given in parameters and builds a prompt
def generate_prompt_from_components(role,context,input,instruction,output_format):
	prompt = f"{context}\n{input}\n{instruction}\n{output_format}"
	return (role, prompt)

if __name__=="__main__":

	#log the start of the actual script
	custom_log("Modules loaded, let's proceed")

	#generate the prompts
	#log-file-analysis  methodology-generation  suspicious-message-detection  timeline-analysis
	base_paths = ["./data/timeline-analysis","./data/suspicious-message-detection","./data/methodology-generation","./data/log-file-analysis"]
	tasks_roles_prompts = []

	for base_path in base_paths:

		#retrieve the prompt components and build the prompt
		data = get_prompt_components(base_path)
		role_prompt = generate_prompt_from_components(data[0],data[1],data[2],data[3],data[4])

		#retrieve the elements of interest: task / role / prompt
		task = base_path.split("/")[-1]
		role = role_prompt[0]
		prompt = role_prompt[1]

		#stores it for the future computations
		task_role_prompt = {"task":task,"role": role,"prompt":prompt}
		tasks_roles_prompts.append(task_role_prompt)

		#write it down for documentation purposes
		with open(f"output/final/prompt_{task}.txt","w",encoding='utf-8') as f:
                	json.dump(task_role_prompt,f,indent=4)


	#static elements
	model_names=["openai/gpt-oss-20b"]
	reasonings=["low","medium","high"]
	temperatures=[0.7]
	iterations = 4
	file_path = "output/final/output"
	max_new_tokens=12500

	#elements that vary for each task
	for trp in tasks_roles_prompts:

		task = trp["task"]
		role = trp["role"]
		prompt = trp["prompt"]

		#run the function that will run the inferences for each combination of parameters
		iter_over_var_and_use_model(task,role,prompt,model_names,reasonings,temperatures,iterations,file_path,max_new_tokens)

	custom_log("Finished!")
