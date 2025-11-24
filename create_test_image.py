from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(text, filename):
    # Create white image
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # Load a font that supports Korean if possible, otherwise just use default and hope for the best
    # or just draw simple shapes if text is hard.
    # macOS usually has AppleGothic
    try:
        font = ImageFont.truetype("/System/Library/Fonts/AppleGothic.ttf", 40)
    except:
        print("Korean font not found, using default.")
        font = ImageFont.load_default()
        
    # Draw text
    d.text((50, 80), text, fill=(0, 0, 0), font=font)
    
    img.save(filename)
    print(f"Saved {filename}")

if __name__ == "__main__":
    create_test_image("활명수", "test_drug.jpg")
