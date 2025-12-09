import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

try:
    print("Loading test_drug.jpg...")
    if not os.path.exists("test_drug.jpg"):
        print("Error: test_drug.jpg not found")
        exit(1)
        
    image = Image.open("test_drug.jpg")
    
    print("Sending request to Gemini...")
    prompt = "Extract the exact product name (제품명) from this medicine image. Return ONLY the name. Do not include '제품명:' or other text."
    
    response = model.generate_content([prompt, image])
    
    print("-" * 20)
    print(f"Response Feedback: {response.prompt_feedback}")
    
    try:
        print(f"Response Text: {response.text}")
    except ValueError:
        print("Response blocked by safety filters.")
        print(f"Candidates: {response.candidates}")

except Exception as e:
    print(f"Error: {e}")
