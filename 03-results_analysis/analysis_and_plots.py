import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import seaborn as sns

#extract all json files and concatenate them
def extract_and_concat_json(file_names):
    full_json = []
    for file in file_names:
        with open(file,"r",encoding="utf-8") as f:
            full_json += json.load(f)

    return full_json

#create the dataframe with all the data
def create_df_from_json(json):
    #read the json and creates the dataframe
    df = pd.json_normalize(json)
    #exclude some useless columns and remove the sample that must be discarded
    df = df.drop(columns=['prompt', 'text', 'last_token_id','text_prompt','text_cot','text_final'],axis=1)
    df = df[df.sample_discarded == False]

    return df

#normalize each metrics value by the number of steps
#also invert it so that the higher the score the better (easier to read)
def normalize_metrics(dataframe):
    dataframe['factuality'] = dataframe.apply(lambda row: 1 - (row.factual_erors / row.steps), axis=1)
    dataframe['validity'] = dataframe.apply(lambda row: 1-(row.logical_errors / row.steps), axis=1)
    dataframe['coherence'] = dataframe.apply(lambda row: 1 - (row.incoherences / row.steps), axis=1)
    dataframe['utility'] = dataframe.apply(lambda row: 1 - (row.useless_steps / row.steps), axis=1)
    dataframe['general'] = dataframe.apply(lambda row: "general",axis=1)
    dataframe['correctness_before'] = dataframe.apply(lambda row: row.correctness,axis=1)

    dataframe = dataframe.drop(columns=['correctness'], axis=1)


    #correctness adjusted based on the maximum correctness achievable
    dataframe['correctness'] = dataframe.apply(lambda row: row.correctness_before / 8 if row.task=="methodology-generation"
                                                else row.correctness_before / 3 if row.task=="timeline-analysis"
                                                else row.correctness_before / 2 if row.task=="log-file-analysis"
                                                else row.correctness_before if row.task == "suspicious-message-detection"
    else np.nan, axis=1)

    dataframe['justification'] = dataframe.apply(lambda row: 1 if row.justified==True else 0, axis=1)

    dataframe['task_name'] = dataframe.apply(lambda row: "MG" if row.task == "methodology-generation"
    else "TA" if row.task == "timeline-analysis"
    else "BHA" if row.task == "log-file-analysis"
    else "SMD" if row.task == "suspicious-message-detection"
    else np.nan, axis=1)

    #score computed by splitting it between correctness (half) and justification (half)
    dataframe['final_score'] = dataframe.apply(lambda row: ((0.75*row.correctness) + (0.25*row.justification)), axis=1)
    dataframe['cot_score'] = dataframe.apply(lambda row: (0.25*row.factuality) + (0.25*row.validity) + (0.25*row.coherence) + (0.25*row.utility), axis=1)
    return dataframe

def plot_cot_final(df,task=None):
    if task == None:
        task_name = "general"
    else:
        df = df[df.task_name == task]
        task_name = task

    df = df[['cot_score','final_score']]
    plt.scatter(df['cot_score'], df['final_score'], color='blue')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title(f'Scatter Plot for task {task_name}')
    plt.xlabel('cot_score')
    plt.ylabel('final_score')
    plt.savefig(f"./plot_output/cot_final_{task_name}.pdf", format="pdf")
    plt.close()

    return None

def display_mean_every_metric(df):
    df_general = df[['general', 'factuality', 'validity', 'coherence', 'utility', 'correctness', 'justification', 'final_score', 'cot_score', 'steps', 'count_tokens_cot', 'count_tokens_final','repetitions']]
    df_task = df[['task_name', 'factuality', 'validity', 'coherence', 'utility', 'correctness', 'justification', 'final_score', 'cot_score', 'steps', 'count_tokens_cot', 'count_tokens_final','repetitions']]

    df_general = df_general.groupby(['general']).mean()
    df_task = df_task.groupby(['task_name']).mean()

    df_merged = pd.concat([df_general, df_task], ignore_index=False, sort=False)

    print('mean_every_metric_every_task all')

    print(tabulate(df_merged, headers='keys', tablefmt='psql'))

    df_merged = df_merged.drop(columns=['steps', 'count_tokens_cot', 'count_tokens_final','repetitions'],axis=1)

    print('mean_every_metric_every_task essential')

    print(tabulate(df_merged, headers='keys', tablefmt='psql'))

    fs = 22
    plt.figure(figsize=(16, 8))
    #plt.title(f'Heatmap for mean of metrics')
    ax = sns.heatmap(df_merged, fmt=".3f", annot=True, annot_kws={"size": fs}, cmap='Greens', xticklabels=True,
                     yticklabels=df_merged.index)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('top')  # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False)  # Disable bottom ticks
    plt.xticks(rotation=45, ha='left', fontsize=fs)
    plt.yticks(rotation=0, fontsize=fs)  # Rotate labels if needed for clarity

    # Adjust the layout to add more space at the top (increase padding)
    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the rect parameter to give more space

    plt.savefig(f"./plot_output/mean_every_metric_every_task.pdf",format="pdf")

    plt.close()
    return None

def display_mean_for_reasoning(df, task=None):
    if task == None:
        task_name = "general"
    else:
        df = df[df.task_name == task]
        task_name = task

    df_reasoning = df[['reasoning', 'factuality', 'validity', 'coherence', 'utility', 'correctness', 'justification', 'final_score', 'cot_score', 'steps', 'count_tokens_cot', 'count_tokens_final','repetitions']]

    df_reasoning = df_reasoning.groupby(['reasoning']).mean()

    df_reasoning = df_reasoning.reindex(index=['low','medium','high'])

    print(f"reasoning_mean_every_metric_{task_name} all")

    print(tabulate(df_reasoning, headers='keys', tablefmt='psql'))

    print(f"reasoning_mean_every_metric_{task_name} essential")

    df_reasoning = df_reasoning.drop(columns=['steps','count_tokens_cot', 'count_tokens_final', 'repetitions'], axis=1)

    print(tabulate(df_reasoning, headers='keys', tablefmt='psql'))

    fs = 22
    plt.figure(figsize=(16, 8))
    #plt.title(f'heatmap for every metric and for task {task_name}')
    ax = sns.heatmap(df_reasoning, fmt=".3f", annot=True, annot_kws={"size": fs}, cmap='Greens', xticklabels=True,
                     yticklabels=df_reasoning.index)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('top')  # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False)  # Disable bottom ticks
    plt.xticks(rotation=45, ha='left', fontsize=fs)
    plt.yticks(rotation=0, fontsize=fs)  # Rotate labels if needed for clarity

    # Adjust the layout to add more space at the top (increase padding)
    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the rect parameter to give more space

    plt.savefig(f"./plot_output/reasoning_mean_every_metric_{task_name}.pdf", format="pdf")

    plt.close()
    return None

def display_mean_for_sampling(df, task=None):
    if task == None:
        task_name = "general"
    else:
        df = df[df.task_name == task]
        task_name = task

    df_temp = df[['temperature', 'factuality', 'validity', 'coherence', 'utility', 'correctness', 'justification', 'final_score', 'cot_score', 'steps', 'count_tokens_cot', 'count_tokens_final','repetitions']]

    df_temp = df_temp.groupby(['temperature']).mean()

    print(f"temperature_mean_every_metric_{task_name} all")

    print(tabulate(df_temp, headers='keys', tablefmt='psql'))

    df_temp = df_temp.drop(columns=['steps','count_tokens_cot', 'count_tokens_final', 'repetitions'], axis=1)

    print(f"temperature_mean_every_metric_{task_name} essential")

    print(tabulate(df_temp, headers='keys', tablefmt='psql'))


    fs = 22
    plt.figure(figsize=(16, 8))
    #plt.title(f'heatmap for every metric and for task {task_name}')
    ax = sns.heatmap(df_temp, fmt=".3f", annot=True, annot_kws={"size": fs}, cmap='Greens', xticklabels=True,
                     yticklabels=df_temp.index)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('top')  # Move x-axis labels to the top
    ax.tick_params(top=True, bottom=False)  # Disable bottom ticks
    plt.xticks(rotation=45, ha='left', fontsize=fs)
    plt.yticks(fontsize=fs)  # Rotate labels if needed for clarity

    # Adjust the layout to add more space at the top (increase padding)
    plt.tight_layout(rect=[0, 0, 1, 1])  # Adjust the rect parameter to give more space

    plt.savefig(f"./plot_output/temperature_mean_every_metric_{task_name}.pdf", format="pdf")

    plt.close()
    return None

def display_mean_for_sampling_reasoning(df, task=None):
    if task == None:
        task_name = "general"
    else:
        df = df[df.task_name == task]
        task_name = task

    df_temp = df[['temperature', 'reasoning', 'factuality', 'validity', 'coherence', 'utility', 'correctness', 'justification', 'final_score', 'cot_score', 'steps', 'count_tokens_cot', 'count_tokens_final','repetitions']]

    df_temp = df_temp.groupby(['temperature','reasoning']).mean()

    print(f"temperature_mean_every_metric_{task_name} all")

    print(tabulate(df_temp, headers='keys', tablefmt='psql'))

    df_temp = df_temp.drop(columns=['steps','count_tokens_cot', 'count_tokens_final', 'repetitions'], axis=1)

    print(f"temperature_mean_every_metric_{task_name} essential")

    print(tabulate(df_temp, headers='keys', tablefmt='psql'))

    return None

if __name__ == '__main__':
    file_names = ["./data_with_eval_values/output_methodology-generation_2025_09_29__18_25_44_new_with_eval.txt",
                  "./data_with_eval_values/output_log-file-analysis_2025_09_26__03_40_56_new_with_eval.txt",
                  "./data_with_eval_values/output_suspicious-message-detection_2025_09_29__16_22_56_new_with_eval.txt",
                  "./data_with_eval_values/output_timeline-analysis_2025_09_25__23_30_48_new_with_eval.txt"]
    tasks = ['methodology-generation',"timeline-analysis",'log-file-analysis','suspicious-message-detection']
    tasks_names = ["MG", "TA", "BHA", "SMD"]
    full_json = extract_and_concat_json(file_names)
    df = create_df_from_json(full_json)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    df_normalized = normalize_metrics(df)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    df_temp = df_normalized[['task', 'reasoning', 'steps', 'factual_erors', 'factuality', 'logical_errors', 'validity', 'incoherences', 'coherence', 'useless_steps', 'utility', 'cot_score']]
    df_temp_2 = df_normalized[['task', 'reasoning', 'steps', 'correctness', 'correctness', 'justified', 'final_score']]
    print(tabulate(df_temp, headers='keys', tablefmt='psql'))
    print(tabulate(df_temp_2, headers='keys', tablefmt='psql'))


    display_mean_every_metric(df_normalized)
    plot_cot_final(df_normalized)
    display_mean_for_reasoning(df_normalized)
    display_mean_for_sampling(df_normalized)
    for task in tasks_names:
        plot_cot_final(df_normalized,task)
        display_mean_for_reasoning(df_normalized,task)
        display_mean_for_sampling(df_normalized,task)

    display_mean_for_sampling_reasoning(df_normalized)
    for task in tasks_names:
        display_mean_for_sampling_reasoning(df_normalized,task)
