""" Creation of an object Model
    that will automate the modelling"""
class autoModel:
    def __init__(self, df, scale):
        self.df = df
        self.scale = scale

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import pandas as pd

class autoModel:
    def __init__(self, models, random_state, scaler):
        self.random_state = random_state
        self.models = models 
        self.scaler = scaler
        self.results = {}
        self.best_model = None
        
    
    def preprocess_data(self, X, y, test_size):
        """Split and scale data"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        self.X_train = self.scaler.fit_transform(X_train)
        self.X_test = self.scaler.transform(X_test)
        self.y_train = y_train
        self.y_test = y_test
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_models(self):
        """Train all models and store results"""
        for name, model in self.models.items():
            # Create pipeline with scaling and model
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', model)
            ])
            
            # Train and predict
            pipeline.fit(self.X_train, self.y_train)
            y_pred = pipeline.predict(self.X_test)
            
            # Store results
            self.results[name] = {
                'model': pipeline,
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred, average='weighted'),
                'recall': recall_score(self.y_test, y_pred, average='weighted'),
                'f1': f1_score(self.y_test, y_pred, average='weighted')
            }
        
        # Find best model
        self.best_model = max(
            self.results.items(), 
            key=lambda x: x[1]['accuracy']
        )
        return self.results
    
    def get_best_model(self):
        """Return the best performing model"""
        return self.best_model
    
    def add_model(self, name, model):
        """Add a custom model to the collection"""
        self.models[name] = model
    
    