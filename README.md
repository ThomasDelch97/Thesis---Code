# Does context matters? 
## Predicting the future performances of NBA Prospects with Machine Learning

Those are the codes associated with my master thesis: "Does context matters?"

There are all the code (except many tests) that I used from the beginning to the end of my project.

This include:
* Scrapping to get data 
* Joinning the different databases (from the scrapping)
* Preprocessing steps
* Feature engineering
* Modelling
* Analysis/Description

In most of the cases, I used functions that were created to streamline the process, make smaller/cleaner files and to re-use if needed latter during the project. GenAI has been used to improve lines of code. 

## Explanations
### Analysis
Contains all the graphs and analysis from the Paper (such as Feature Selection comparison)

### Databases
Contains all the code associated with the creation of a database

**Creation** contain the scrapping for the NBA and NCAA part

**Database Update** contain functions to merge the data

### FunctionFolder
Contains all the functions used in other file

**config.py** 
Some configuration items

**preProcessingAuto.py**
Functions used to preprocess quickly the database (based on my analysis)

**OptimisationModel.py**
Function to select the features and to optimize the hyperparameters with BayesSearchCV

### Modelisation Finale
Contains the code and analysis with the finale models

### Archives
Other analysis not (directly) relevant for the final paper but was part of the construction of thoughts.