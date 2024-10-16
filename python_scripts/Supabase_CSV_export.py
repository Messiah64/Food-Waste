import os
import cv2
import base64
import datetime
import csv
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI 
import re

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


def export_supabase_to_csv(table_name, output_folder):
    # Fetch all data from the specified table
    response = supabase.table(table_name).select("*").execute()
    
    # Check if the fetch was successful
    if not response.data:
        print(f"Error: Unable to fetch data from {table_name}")
        return
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate a unique filename based on date and time
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_folder}/{table_name}_export_{current_time}.csv"
    
    # Write the data to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        # Assuming all rows have the same structure, use the keys from the first row as fieldnames
        fieldnames = response.data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write the data rows
        for row in response.data:
            writer.writerow(row)
    
    print(f"Data exported successfully to {filename}")

export_supabase_to_csv('food_wastage', 'exports')