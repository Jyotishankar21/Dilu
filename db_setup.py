import sqlite3
import pandas as pd
from sklearn.datasets import load_breast_cancer

# Load dataset
dataset = load_breast_cancer()
df = pd.DataFrame(dataset.data, columns=dataset.feature_names)
df.insert(0, 'id', range(1, 1 + len(df)))

# Connect to SQLite
db = sqlite3.connect("cancer_data.db")
cursor = db.cursor()

# Create cancer_data table
fields = ", ".join([f"'{col}' REAL" for col in df.columns if col != 'id'])
cursor.execute(f'''
CREATE TABLE IF NOT EXISTS cancer_data (
    id INTEGER PRIMARY KEY,
    {fields}
)
''')

# Create diagnoses table
cursor.execute('''
CREATE TABLE IF NOT EXISTS diagnoses (
    id INTEGER,
    diagnosis TEXT,
    timestamp TEXT,
    FOREIGN KEY(id) REFERENCES cancer_data(id)
)
''')

# Insert dataset
df.to_sql('cancer_data', db, if_exists='replace', index=False)

db.commit()
db.close()
print("✅ Database setup complete with cancer_data and diagnoses table.")
