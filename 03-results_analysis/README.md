# Results analysis
This steps takes the evaluated samples and then computes different statistics to answer the research questions.

## Data

### ./data_with_eval_values/
This contains all the files with the evaluated samples. It is the output from previous step.

### ./plot_output/
This contains all the plots that are generated via the python code.

## Code

### ./analysis_and_plots.py
This python file starts by concatenating the 4 json files that serves as input. It then loads it as a pandas dataframe, makes a few computations to adjust the metrics (e.g. change the task name to their acronym, compute the factuality by doing 1-nb_factual_errors/nb_steps...). It also computes the global score for the reasoning and for the final answer. It then aggregates relevant elements togtether using their average to answer the research questions. First it show how each task performed for each metric, then how the reasoning influences the metrics, then how the generation methods impacts the results... It also plot the reasoning and final score to see if they are related.

The input are the files in ./data_with_eval_values/ and the output are the plots in ./plot_output/. More elements are printed when executing the code.