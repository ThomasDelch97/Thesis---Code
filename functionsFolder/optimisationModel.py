#Necessary packages for the functions
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from time import time
from imblearn.combine import SMOTETomek
from imblearn.pipeline import Pipeline as ImbPipeline
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer
import joblib

## Base pipeline
base_pipeline = ImbPipeline([
    ('scaler', StandardScaler()),
    ('resampler', SMOTETomek(random_state=143)),
    ('classifier', None)
])


def select_features(X_train, X_test, y_train, 
                    selector='randomforest', 
                    max_features_range=(1, 50), 
                    n_iter=10):
    
    print(f"Optimisation de max_features avec {selector}") #Keep track of where we are since we optimise two features store
    
    pipeline = ImbPipeline([
        ('scaler', StandardScaler()),
        ('resampler', SMOTETomek(random_state=42, sampling_strategy=0.5)),
        ('selector', SelectFromModel(
            estimator=RandomForestClassifier(random_state=42, class_weight='balanced', 
                                         )
        )),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000, 
                                          class_weight='balanced'))  #Use of logistic regression as reference since it is quicker to train
    ])
    
    #Research space for max_features
    search_spaces = {
        'selector__max_features': Integer(max_features_range[0], min(max_features_range[1], X_train.shape[1]))
    }
    
    #BayesSearchCV optimisation of features selection
    search = BayesSearchCV(
        estimator=pipeline,
        search_spaces=search_spaces,
        n_iter=n_iter, 
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42), #Equal distribution of classes
        scoring='roc_auc', #Optimisation of the AUC 
        n_jobs=-1,
        verbose=0,
        random_state=42 #Reproducability
    )
    
    search.fit(X_train, y_train)
    best_max_features = search.best_params_['selector__max_features']
    
    #Pipeline for Feature selector RF because best average results
    feature_selector = ImbPipeline([
        ('scaler', StandardScaler()),
        ('resampler', SMOTETomek(random_state=42, sampling_strategy=0.5)),
        ('selector', SelectFromModel(
            estimator=RandomForestClassifier(random_state=42, class_weight='balanced'),
            max_features=best_max_features
        ))
    ])
    
    feature_selector.fit(X_train, y_train) 
    X_train_selected = feature_selector.transform(X_train) #Train set with only the selected features
    X_test_selected = feature_selector.transform(X_test) #Test set with only the selecte features
    
    #Get the selected features in a list
    selected_ = feature_selector.named_steps['selector'].get_support()
    selected_features = X_train.columns[selected_].tolist() #Features selected in a list
    
    print(f"Optimal number of features: {best_max_features}")
    print(f"Number of features selected: {len(selected_features)}")
    print(f"Features selected: {selected_features}")
        
    return X_train_selected, X_test_selected, selected_features, best_max_features




def optimized_training(X_train, X_test, 
                       y_train, y_test,
                       classifiers, config,
                       selector, search_spaces,
                       features_set_name
                    ):
    
    results = [] #list to save the results from the models optimized
    for model_name in classifiers:
        pipeline = base_pipeline.set_params(classifier=classifiers[model_name])

        search = BayesSearchCV(
            estimator=pipeline,
            search_spaces=search_spaces[model_name],
            n_iter=config['n_iter'],
            cv=StratifiedKFold(config['n_folds']), #See above
            scoring=config['scoring'],
            n_jobs=-1,
            verbose=0,
            random_state=42
        )

        start_time = time()
        search.fit(X_train, y_train)
        training_time = (time() - start_time)/60  #Time to optimize the model (min)
        
        #Best parameters for that model
        best_params = search.best_params_

        #Refit the model with the best parameters 
        best_pipeline = base_pipeline.set_params(classifier=classifiers[model_name])
        best_pipeline.set_params(**best_params)
        best_pipeline.fit(X_train, y_train)  

        #Save the best models in a pkl doc if needed after
        joblib.dump(best_pipeline, f"with_cond_best_model_retrained_{features_set_name}_{model_name.replace(' ', '_')}_{selector}.pkl")

        #Results
        train_pred = best_pipeline.predict(X_train)
        test_pred = best_pipeline.predict(X_test)
        train_proba = best_pipeline.predict_proba(X_train)[:, 1]
        test_proba = best_pipeline.predict_proba(X_test)[:, 1]

        #Save the results
        results.append({
            'Features Set': features_set_name,
            'Model': model_name,
            'Train Accuracy': accuracy_score(y_train, train_pred),
            'Test Accuracy': accuracy_score(y_test, test_pred),
            'F1': f1_score(y_test, test_pred),
            'Best AUC': roc_auc_score(y_test, test_proba),
            'Training Time (min)': round(training_time, 1),
            'Nb features' : X_train.shape[1],
            'Best Params': best_params
        })
    
    return pd.DataFrame(results) #return a dataframe with the results of the refit model