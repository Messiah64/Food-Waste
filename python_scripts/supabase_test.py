import os
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def get_day_of_week():
    current_date = datetime.datetime.now()
    day_of_week = current_date.strftime("%A")
    return day_of_week

def upload_data(stall, rice, meat, veggies):
    # Data to be inserted into the table
    data = {
        'stall': stall,
        'day':  get_day_of_week(),
        'rice': rice,
        'meat': meat,
        'veggies': veggies
    }

    # Insert data into the table (replace 'your_table_name' with the actual table name)
    response = supabase.table('food_wastage').insert(data).execute()

    # Check if the insertion was successful
    if response:
        print("Data inserted successfully!")
    else:
        print(f"Error: {response} - {response.json()}")

# Example usage
upload_data(1, 3, 2, 1)  # Upload data to the table (adjust the values as needed)