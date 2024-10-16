import asyncio
import websockets
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime
from openai import OpenAI
import base64
import cv2

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# OpenAI setup
MODEL = "gpt-4o"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Camera setup
camera = cv2.VideoCapture(1)  # Use 0 for default camera

def get_day_of_week():
    current_date = datetime.datetime.now()
    return current_date.strftime("%A")

def capture_image():
    ret, frame = camera.read()
    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        print(_, buffer)
        return base64.b64encode(buffer).decode('utf-8')
    return None

async def process_image(base64_image):
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful food waste manager. I have a photo of a plate of food being thrown away. Please describe the amount of food leftover in the plate. The food initially came at a portion size of 50% Rice, 25% vegetables, and 25% meat, of the WHOLE plate. Estimate and describe the percentage of rice, veg and meat remaining (as shown by black squiggly lines and boundaries) compared to the initial portion sizes. Like, 15% rice remaining of initial 50% portion. so just give 15. Give your answers in this format: (rice, veggies, meat). an example: (15, 50, 10)."},
        {"role": "user", "content": [
            {"type": "text", "text": "Here is my food plate: "},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.5,
)
    return response.choices[0].message.content

def upload_data(stall, rice, meat, veggies):
    data = {
        'stall': stall,
        'day': get_day_of_week(),
        'rice': rice,
        'meat': meat,
        'veggies': veggies
    }
    response = supabase.table('food_wastage').insert(data).execute()
    if response:
        print("Data inserted successfully!")
    else:
        print(f"Error: {response}")

async def handle_client(websocket, path):
    try:
        print(f"New client connected: {websocket.remote_address}")
        async for message in websocket:
            print(f"Received NFC data (stall number): {message}")
            
            # Capture image
            base64_image = capture_image()
            if base64_image:
                # Process image with GPT-4 Vision
                gpt_response = await process_image(base64_image)
                print(f"GPT-4 Vision response: {gpt_response}")
                
                # Parse GPT-4 Vision response
                try:
                    rice, veggies, meat = eval(gpt_response)
                    
                    # Upload data to Supabase
                    upload_data(int(message), rice, meat, veggies)
                except:
                    print("Error parsing GPT-4 Vision response")
            else:
                print("Error capturing image")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("WebSocket server started on port 8765")
    print("Waiting for NFC data...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())