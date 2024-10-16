import streamlit as st
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 1. Load the trained model and encoder
model = joblib.load('food_waste_prediction_model.pkl')
encoder = joblib.load('day_encoder.pkl')

# 2. Streamlit app title
st.title("Food Waste Prediction App")

# 3. User input section
st.subheader("Input Day and Food Wastage Data")

# Day selection
day = st.selectbox("Select the Day", ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])

# Optional stall number (useful for further customization)
stall = st.number_input("Stall Number", min_value=1, max_value=10, value=1)

# Optional inputs for rice, meat, veggies wastage (in percentages)
rice = st.slider("Rice Wastage (%)", 0, 100, 30)
meat = st.slider("Meat Wastage (%)", 0, 100, 10)
veggies = st.slider("Veggies Wastage (%)", 0, 100, 50)

# Button to trigger prediction
if st.button("Predict Food Waste"):
    
    # 4. Prepare data for prediction
    input_data = pd.DataFrame([[stall, rice, meat, veggies]], columns=['stall', 'rice', 'meat', 'veggies'])
    
    # One-hot encode the 'day' input
    day_encoded = encoder.transform([[day]])
    day_encoded_df = pd.DataFrame(day_encoded, columns=encoder.get_feature_names_out(['day']))
    
    # Concatenate day encoding with input_data
    input_data = pd.concat([input_data, day_encoded_df], axis=1)
    
    # Make prediction
    predicted_waste = model.predict(input_data)[0]
    
    # Display prediction result
    st.subheader(f"Predicted Total Food Waste: {predicted_waste:.2f}%")
    
    # 5. Plot the input and prediction
    fig, ax = plt.subplots()
    categories = ['Rice', 'Meat', 'Veggies', 'Predicted Waste']
    values = [rice, meat, veggies, predicted_waste]
    
    ax.bar(categories, values, color=['blue', 'orange', 'green', 'red'])
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Food Waste Breakdown")
    
    st.pyplot(fig)

# 6. Historical data (if available) for visualization
# Example of a historical data dataframe
historical_data = pd.DataFrame({
    'day': ['monday', 'tuesday', 'wednesday', 'thursday'],
    'total_waste': [60, 45, 70, 55]
})

st.subheader("Historical Food Waste Data")
st.bar_chart(historical_data.set_index('day')['total_waste'])

# Explanation of the prediction
st.markdown("""
### How it Works:
- **Input Day and Wastage Values**: You can provide the day of the week and wastage values for rice, meat, and veggies.
- **Model Prediction**: The app uses a trained machine learning model to predict the total food wastage based on these inputs.
- **Visualization**: The predicted value is displayed along with the breakdown of the input wastage data.
""")
