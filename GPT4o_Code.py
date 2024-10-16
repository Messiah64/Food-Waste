import os
import cv2
import base64
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI 
import re
import asyncio
import websockets
import time


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)



async def handle_client(websocket, path):
    try:
        print(f"New client connected: {websocket.remote_address}")
        async for message in websocket:
            print(f"Received NFC data: {message}")
            time.sleep(2)
            if  message == "stall_one":
                text_response = capture_save_convert_upload_image()
                rice, veggies, meat = extract_portions_from_text(text_response)
                print("Rice: ", rice, "Veggies: ", veggies, "Meat: ", meat)
                upload_To_SupaBase(1, rice, veggies, meat)

            else:
                text_response = capture_save_convert_upload_image()
                rice, veggies, meat = extract_portions_from_text(text_response)
                print("Rice: ", rice, "Veggies: ", veggies, "Meat: ", meat)
                upload_To_SupaBase(6, rice, veggies, meat)


    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("WebSocket server started on port 8765")
    print("Waiting for NFC data...")
    await server.wait_closed()

# upload to Supabase
def upload_To_SupaBase(stall, rice, meat, veggies):
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

# Takes picture -> GPT4o 
def capture_save_convert_upload_image():
    # Folder to store captured images
    IMAGE_FOLDER = "captured_images"

    # Create the folder if it doesn't exist
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    camera = cv2.VideoCapture(1)


    # Capture image from the camera
    ret, frame = camera.read()
    if ret:
        # Generate a unique filename based on date and time
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{IMAGE_FOLDER}/image_{current_time}.jpg"

        # Save the captured image to the folder
        cv2.imwrite(filename, frame)
        print(f"Image saved as: {filename}")

        # Convert saved image to base64
        with open(filename, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

            MODEL="gpt-4o"
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # TO DO: EDIT HERE BELOW
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful food waste manager. I have a photo of a plate of food being thrown away. Please describe the amount of food leftover in the plate. The food initially came at a portion size of 50% Rice, 25% vegetables, and 25% meat, of the WHOLE plate. Estimate and describe the percentage of rice, veg and meat remaining (as shown by black squiggly lines and boundaries) compared to the initial portion sizes. Like, 15% rice remaining of initial 50% portion. so just give 15. Give your answers in this format: (rice, veggies, meat). an example: (15, 50, 10). DONT RETURN ANYTHING ELSE!! THIS IS VERY IMPORTANT"},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Here is my food plate: "},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"}
                        }
                    ]}
                ],
                temperature=0.4,
            )

            content = response.choices[0].message.content
            print(content)
        camera.release()
        return content
    else:
        print("Failed to capture image.")
        camera.release()
        return None

def get_day_of_week():
    current_date = datetime.datetime.now()
    return current_date.strftime("%A")

def extract_portions_from_text(text):
    # Find the start and end positions of the parentheses
    start = text.find('(')
    end = text.find(')')
    
    if start != -1 and end != -1:
        # Extract the portion inside the parentheses
        portions_string = text[start+1:end]
        
        # Split the string by commas, strip any extra spaces, and convert to integers
        portions = portions_string.split(',')
        if len(portions) == 3:  # Ensure there are exactly three values
            rice, veggies, meat = [int(p.strip()) for p in portions]
            return rice, veggies, meat
        else:
            print("Invalid number of portions in the parentheses.")
            return None, None, None
    else:
        print("No portions found in the text.")
        return None, None, None



if __name__ == "__main__":
    asyncio.run(main())