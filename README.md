# Does context matters? 
## Predicting the future performances of NBA Prospects with Machine Learning

Those are the codes associated with my master thesis: "Does context matters?"

There are all the code (except all the different test codes) that I used from the beginning to the end of my project.

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

* **Creation** contain the scrapping for the NBA and NCAA part

* **Database Update** contain functions to merge the data

### FunctionFolder
Contains all the functions used in other file

* **config.py** 
Some configuration items

* **preProcessingAuto.py**
Functions used to preprocess quickly the database (based on my analysis)

* **OptimisationModel.py**
Function to select the features and to optimize the hyperparameters with BayesSearchCV

### Modelisation Finale
Contains the code and analysis with the finale models

### ArchivesTests
Other analysis not (directly) relevant for the final paper but was part of the construction of thoughts.

### Data
The most important data only and the PBP data for the interest ones.

# Sources
* https://www.sports-reference.com: Team and player’s past statistics
* https://www.nbadraft.net: Scouting report and evaluation
* https://basketball.realgm.com: Team and player’s past statistics
* https://basketball-reference.com: Player’s future statistics 
* https://github.com/sportsdataverse: PBP Data

# LICENSE

ML Application to predict draft prospects future performances
    Copyright (C) <2025>  <DELCHAMBRE Thomas>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
