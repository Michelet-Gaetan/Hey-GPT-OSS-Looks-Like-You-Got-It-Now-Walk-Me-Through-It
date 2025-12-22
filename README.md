# Hey GPT-OSS, Looks Like You Got It – Now Walk Me Through It!

This GitHub page hosts all the codes and data used for the experiment described in the paper "Hey GPT-OSS, Looks Like You Got It – Now Walk Me Through It! An Assessment of the Reasoning Language Models Chain of Thought Mechanism for Digital Forensics". You can the pre-print of the paper here: [Hey GPT-OSS, Looks Like You Got It – Now Walk Me Through It! An Assessment of the Reasoning Language Models Chain of Thought Mechanism for Digital Forensics](https://arxiv.org/abs/2512.04254). The link will be uploaded once the paper is published.


The experiment can be divided in three steps: [The text generation](https://github.com/Michelet-Gaetan/Hey-GPT-OSS-Looks-Like-You-Got-It-Now-Walk-Me-Through-It/tree/main/01-text_generation), [The evaluation](https://github.com/Michelet-Gaetan/Hey-GPT-OSS-Looks-Like-You-Got-It-Now-Walk-Me-Through-It/tree/main/02-evaluation), and [The results analysis](https://github.com/Michelet-Gaetan/Hey-GPT-OSS-Looks-Like-You-Got-It-Now-Walk-Me-Through-It/tree/main/03-results_analysis).


In each folder you will find another README.md detailing important elements for a given step.


Appendices were moved from the paper to this README file.

## Appendix - Digital Forensics Tasks

This section lists the details of the digital forensic tasks that we have instructed the RLM to solve. The tasks are sorted by complexity.

### Suspicious Message Detection (SMD)

***Description:*** The model is provided with information about a case investigated and messages extracted from a chat conversation. It must then determine whether the chat is relevant to the investigation or not.

***Justification:*** This task is time-consuming and very common during digital forensic investigations. A reasoning process is required to successfully determine if the chat is relevant to the investigation.

***Context and instruction:***  The context in this scenario is a drug-related investigation in which Alex, a fictional character, is suspected of dealing. A long chat conversation involving Alex was secured and is provided as input data. The model is instructed to determine whether the chat is relevant to the ongoing investigation or not. The answer needs to be justified.

***Input data:*** The chat was generated using GPT-5 mini. The discussion revolves around the Breaking Bad TV show, with the two participants commenting on implications related to the show. Given the popularity of ``Breaking Bad'', information regarding the TV show was likely present in the gpt-oss training data. This could have led to better results than with a discussion topic that was never seen by the model during its training. Our goal when designing this task was to create an ambiguity between chatting about drugs and chatting about a drug-related TV show. In the initial chat, direct mentions of the show's name were present and manually removed to complicate the task. The text was manually adjusted to remain coherent without mentioning the show. Note that the names of certain characters from the show were not removed.

***Expected answer:*** The model is supposed to indicate that the chat is irrelevant for the investigation and provide a justification.

### Bash History Analysis (BHA)


***Description:*** The model is provided with the bash history extracted from the laptop belonging to someone suspected of trying to attack a server. It must determine if an attack was undertaken from that laptop and, if so, who was the target.

***Justification:*** This task is time-consuming and requires reasoning to determine whether some commands are potentially harmful and who could be targeted.

***Context and instruction:*** This scenario involves investigating a person suspected of possibly attempting a server attack. The computer was seized, the disk was imaged, and the bash history was extracted from the seized Linux system. The model is tasked to determine if an attack was undertaken from the computer, and if so, who the target of that attack was. It must also justify the answers.

***Input data:*** The input data is a bash history generated using GPT-5 mini. We decided to generate it synthetically for simplicity (i.e. no need to simulate normal behavior and an attack). After the initial generation, the bash history was manually reviewed to remove repetitive elements and rename overly obvious test and example file and website names. In addition, some of the commands were adjusted.

***Expected answer:*** The model should acknowledge that an attack could have been undertaken from that computer, that the server with IP 100.200.30.40 was the target, and justify these answers.

### Methodology Generation (MG)

***Description:*** The model receives information about a case under investigation and the associated investigative questions. It must then design a methodology that can be used to answer these questions.

***Justification:*** This is a prevalent task during investigations where a methodology must be established according to the questions asked by the investigator. The creation of such a targeted methodology requires reasoning.

***Context and instruction:*** The scenario centers on an investigation related to a murder. The suspect's Samsung S23 was seized and sent to the forensic lab for analysis. Investigators are tasked with determining the suspect's location on January 15, 2024, following the NIST four-phase framework (Collection, Examination, Analysis, Reporting). These two elements serve as the input data. Based on the NIST four-phase framework, the model is then required to outline a methodology that enables investigators to answer the question regarding the suspect's whereabouts on the day of the murder. For each step, the model should also justify and recommend appropriate tools to carry out the procedures.

***Input data:*** For this task, the input data consists of the question posed by the investigators: ``Can you determine the suspect's location on January 15, 2024, the day of the murder?'' and the investigation model employed by the institution (the NIST four-phase framework).

***Expected answer:*** The model must provide the draft of a methodology following the NIST four-phase framework that can help determine the suspect's location on the date of interest. Each step must be justified, and tools should be suggested whenever possible.

### Timeline Analysis (TA)

***Description:*** The model is provided with information about a suspected data theft and a timeline obtained from a forensic image. It must then determine whether the timeline data can confirm the theft.

***Justification:*** This task is particularly time-consuming. Moreover, intense reasoning is required in order to be undertaken. This makes timeline analysis a good fit for this experiment.

***Context and instruction:*** The context in this scenario is an investigation requested by a company named `Out-of-Date GmbH'. This company assumes that one of its employees stole its world-famous secret recipe. They assume the employee got access to a mainframe server (which is not connected to the Internet) and copied the secret recipe to another device. They think it probably happened during maintenance on 04/19/2017. A timeline of the mainframe server filtered on the date of interest is provided as input data. The model is tasked to determine if something suspicious happened, and if so, what? It must also determine if the Internet connection was actually deactivated and justify all the answers.

***Input data:*** The input data is a modified version of a timeline manually generated for an exercise on digital forensics in 2017. Given the gpt-oss context window and GPU memory limit, we decided to remove some irrelevant events and fields from that timeline in order to reduce the number of tokens in the prompt provided to the model. The events were first filtered based on the date of interest (04/19/2017). Afterward, Eric Zimmerman's timeline explorer was used to filter out events that were not highlighted by the tool. Highlighted and therefore essential events are: file opening, web history, deleted data, execution, device or USB usage, folder opening, and log file.

***Expected answer:*** The model must answer that a USB drive has been plugged into the machine, that the secret recipe can indeed be found on the machine, and that the data is insufficient to prove that the recipe has been stolen. Additionally, it must indicate that the Internet connection was likely active at some point and justify all these answers. The challenge with this task is that the data is actually insufficient to answer the investigative questions clearly. Nevertheless, the model is asked to answer with yes or no. This is intended to simulate a situation in which a user forces the model to decide on an answer even though the available data is actually insufficient for this.
