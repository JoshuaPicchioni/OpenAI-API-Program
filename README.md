# OpenAI-API-Program
A program that allows interfacing with that OpenAI API with multiple extra features aimed at seeing the moderation API result of inputs and outputs.

# GROUP MEMBERS 
JOSHUA PICCHIONI

# INSTRUCTIONS FOR MAC 
First, you must have an OpenAI API key to run and use this program. Specifically on Mac after you have added it to your ~/.bash_profile. Then you must include it in the terminal window when running the program 

 `source ~/.bash_profile`

Then after, navigate to the directory where you have it stored and run:

`python GPTAPIPROGRAM.py`
or
`python3 GPTAPIPROGRAM.py`

# CAPABILITIES
-  Interface with the text-based models from OpenAI. By default, the model that will be interfaced with is GPT-3.5 however it can easily be changed in the code if desired.

- Auto saving your conversations you have in the ".json" format, allowing them to be reviewed and even continues by using "import".

-  Output the moderation result output data, which shows the scores for how likely the text inputted or outputted is to break the OpenAI usage policy guideliness.

- Generation of text files containing the input the user gives, the output the model gives, and the moderation API scores of the data.
