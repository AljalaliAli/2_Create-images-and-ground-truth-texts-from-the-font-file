from PIL import Image, ImageDraw, ImageFont
import os
import configparser

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

input_text_file = config['Paths']['input_text_file']
output_dir = config['Paths']['output_dir']
font_path = config['Paths']['font_path']

char_spacing = config.getint('Settings', 'char_spacing')
text_alignment = config['Settings']['text_alignment']
padding = config.getint('Settings', 'padding')
font_size = config.getint('Settings', 'font_size')
background_color = config.getint('Settings', 'background_color')
text_color = config.getint('Settings', 'text_color')
dpi = config.getint('Settings', 'dpi')

def create_text_file(text, index, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    text_file_path = os.path.join(output_dir, f"{index}.gt.txt")
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return text_file_path

def create_image_from_text(text, font_path, index, output_dir, font_size=60, background_color=1, text_color=0, dpi=300, char_spacing=10, text_alignment="center", padding=10):
    try:
        # Check if the font file exists
        if not os.path.exists(font_path):
            print(f"Font file not found at: {font_path}")
            return
        
        # Load the font
        print(f"Loading font from: {font_path}")
        font = ImageFont.truetype(font_path, font_size)
        # Create a temporary image to calculate text size
        temp_image = Image.new('1', (1, 1), color=background_color)
        draw = ImageDraw.Draw(temp_image)
        
        # Initialize variables for calculating text size
        total_text_width = 0
        text_height = 0
        
        for char in text:
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            total_text_width += char_width + char_spacing
            text_height = max(text_height, char_height)
        
        # Adjust for extra spacing added after the last character
        total_text_width -= char_spacing
        
        # Calculate the image size with some padding
        image_width = int(total_text_width + 2 * padding)  # Add padding to both sides
        image_height = int(text_height + 2 * padding)     # Add padding to both top and bottom
        
        # Create a new binary image with the specified background color
        image = Image.new('1', (image_width, image_height), color=background_color)  # '1' mode creates a binary image
        draw = ImageDraw.Draw(image)
        
        # Positioning based on text alignment
        if text_alignment == "center":
            x = (image_width - total_text_width) // 2
        elif text_alignment == "left":
            x = padding  # Add some left padding
        elif text_alignment == "right":
            x = image_width - total_text_width - padding  # Add some right padding
        else:
            raise ValueError("text_alignment must be 'center', 'left', or 'right'.")
        
        y = (image_height - text_height) // 2
        
        # Draw each character with the specified spacing
        for char in text:
            bbox = draw.textbbox((x, y), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            draw.text((x, y), char, font=font, fill=text_color)
            x += char_width + char_spacing
        
        # Save the image to the specified output path with the specified DPI
        img_name = f'{index}.tif'
        output_img_path = os.path.join(output_dir, img_name)
        image.save(output_img_path, dpi=(dpi, dpi))
        print(f"Image saved to: {output_img_path} with DPI: {dpi}")

    except Exception as e:
        print(f"An error occurred: {e}")

def process_text_file(input_text_file, output_dir, font_path, char_spacing=10, text_alignment="center", padding=10):
    if not os.path.exists(input_text_file):
        print(f"Input text file not found at: {input_text_file}")
        return
    
    try:
        # Open the text file with utf-8 encoding to avoid UnicodeDecodeError
        with open(input_text_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"UnicodeDecodeError: Cannot read file '{input_text_file}' with UTF-8 encoding.")
        print("Try using a different encoding or check the file for special characters.")
        return
    
    for i, line in enumerate(lines):
        text = line.strip()
        if not text:
            continue
        
        # Create text file with a numeric name based on the index
        create_text_file(text, i, output_dir)
        
        create_image_from_text(text, font_path, i, output_dir, font_size, background_color, text_color, dpi, char_spacing, text_alignment, padding)

# Usage example
process_text_file(input_text_file, output_dir, font_path, char_spacing=char_spacing, text_alignment=text_alignment, padding=padding)
