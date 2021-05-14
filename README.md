## 20BSP17 Group 2 - Sentiment Analysis

Compare and contrast the performance of different sentiment analysis libraries including TextBlob, VaderSentiment and Scikit-learn on a textual data set of COVID-19 vaccine related tweets, in doing so we will consider their relative merits and flaws as well as considering which libraries are more appropriate for different forms of data sets.  

### Installing dependencies

You need to install the required packages onto your computer first. You can simply follow the instruction below:

Firstly, locate the directory using cd like below
```
cd "C://path/to/directory"
```
#### Install using pip
```
python -m pip install -r requirements.txt
```
#### Install using Conda
```
conda create --name 20BSP17_Group2 --file environment.yaml 
```
### User guide

To run the visualisation dashboard for existing results, simply run the code below:
```
python main.py
```
Keep the terminal open otherwise the website will not be responsive as the server shuts down.

#### Optional parameters

There are also some other optional features that you could turn on before the dashboard runs

`--fetch`: Fetch new twitter data on launch (You will need to fill in the twitter API keys and secrets inside `config.ini`)

`--train`: Re-train all the model with randomized training and testing datasets. This will also re-analyze all models.

`--analyze`: Re-analyse all the models with the testing data.