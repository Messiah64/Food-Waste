import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
import joblib

# 1. Load the dataset
data = {
    'id': [2, 3, 4, 17, 18, 19, 20],
    'created_at': ['2024-10-12T14:54:50.339122+00:00', '2024-10-12T14:56:06.65685+00:00', '2024-10-12T14:58:34.344574+00:00', 
                   '2024-10-16T06:09:10.876942+00:00', '2024-10-16T06:18:13.137054+00:00', '2024-10-16T06:19:11.83674+00:00', 
                   '2024-10-16T06:23:26.756113+00:00'],
    'stall': [1, 2, 3, 1, 6, 6, 6],
    'rice': [30, 50, 10, 20, None, None, 10],
    'meat': [0, 10, 0, 10, None, None, 5],
    'veggies': [50, 50, 100, 5, None, None, 5],
    'day': ['monday', 'tuesday', 'wednesday', 'Wednesday', 'Wednesday', 'Wednesday', 'Wednesday']
}

df = pd.DataFrame(data)

# 2. Data Preprocessing
# Fill missing values (for simplicity, we'll fill them with 0)
df['rice'].fillna(0, inplace=True)
df['meat'].fillna(0, inplace=True)
df['veggies'].fillna(0, inplace=True)

# Create a new column 'total_waste' (sum of rice, meat, veggies waste)
df['total_waste'] = df['rice'] + df['meat'] + df['veggies']

# Standardize the 'day' column (all lowercase)
df['day'] = df['day'].str.lower()

# 3. One-Hot Encode 'day'
encoder = OneHotEncoder(sparse_output=False, drop='first')  # Updated argument
day_encoded = encoder.fit_transform(df[['day']])

# Convert encoded days back to DataFrame and concatenate
day_encoded_df = pd.DataFrame(day_encoded, columns=encoder.get_feature_names_out(['day']))
df = pd.concat([df, day_encoded_df], axis=1)

# Drop unnecessary columns
df.drop(columns=['id', 'created_at', 'day'], inplace=True)

# 4. Separate features and target
X = df.drop(columns=['total_waste'])  # Features: everything except 'total_waste'
y = df['total_waste']  # Target: total food waste

# 5. Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train a simple Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# 7. Save the trained model to a .pkl file
joblib.dump(model, 'food_waste_prediction_model.pkl')

# 8. Save the encoder as well (since we need it to transform future data)
joblib.dump(encoder, 'day_encoder.pkl')

print("Model and encoder have been saved as 'food_waste_prediction_model.pkl' and 'day_encoder.pkl'.")
