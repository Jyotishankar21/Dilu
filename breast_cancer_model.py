import numpy as np
import pandas as pd
import sklearn.datasets
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load dataset
breast_cancer_dataset = sklearn.datasets.load_breast_cancer()
data_frame = pd.DataFrame(breast_cancer_dataset.data, columns=breast_cancer_dataset.feature_names)
data_frame['label'] = breast_cancer_dataset.target

X = data_frame.drop(columns='label', axis=1)
Y = data_frame['label']

# Train model
model = LogisticRegression(max_iter=10000)
model.fit(X, Y)

def predict_breast_cancer(input_data):
    input_df = pd.DataFrame([input_data], columns=breast_cancer_dataset.feature_names)
    prediction = model.predict(input_df)
    return 'Malignant' if prediction[0] == 0 else 'Benign'
