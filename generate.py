from PIL import Image, ImageDraw, ImageFont
import json
import os, sys

fail_header = "Fail: "
pass_header = "Pass: "
error_header = "Error: "

# Split a plate number into several sections, using a specified split character and number of parts.
def split_text(input_string, split_char, num_parts):
    # Split the input string by the specified character
    parts = input_string.split(split_char)

    # If the number of parts is greater than the number of splits, return the original string num_parts times in a list
    if num_parts > len(parts):
        return [input_string] * num_parts

    if not parts or num_parts <= 0:
        return []

    # If there are fewer parts than num_parts, pad with empty strings
    if len(parts) < num_parts:
        parts += [''] * (num_parts - len(parts))

    # Calculate how many parts per section (distribute as evenly as possible)
    avg = len(parts) // num_parts
    rem = len(parts) % num_parts

    result = []
    idx = 0
    for i in range(num_parts):
        # Distribute the remainder among the first 'rem' sections
        count = avg + (1 if i < rem else 0)
        section = parts[idx:idx+count]
        result.append(split_char.join(section))
        idx += count
    
    return result

# Function to add badge icon (e.g., flag) to the plate
def add_badge_icon(plate_image, badge_config, badge_on_plate_config):
    badge_width = badge_on_plate_config["width"]
    badge_height = badge_on_plate_config["height"]
    badge_starting_position = tuple(badge_on_plate_config["starting_position"])
    
    badge_icon_size = badge_on_plate_config["icon_size"]
    badge_icon_file = badge_config["icon"]["content"]
    # Build the path to the icon image file
    badge_icon_file = os.path.join(sys.path[0], 'badges', 'icons', f'{badge_icon_file}.png')

    # Only add the icon if the file exists
    if os.path.exists(badge_icon_file):
        badge_icon = Image.open(badge_icon_file).convert("RGBA")
        badge_icon_width = badge_icon_size
        badge_icon_height = int((badge_icon_width / badge_icon.size[0]) * badge_icon.size[1])
        badge_icon = badge_icon.resize((badge_icon_width, badge_icon_height))
        # Placement ratios from config
        badge_icon_placement_x = badge_config["icon"]["placement"][0]
        badge_icon_placement_y = badge_config["icon"]["placement"][1]
        # Calculate icon position within the badge rectangle
        badge_icon_x = int((badge_width - badge_icon_width) / badge_icon_placement_x + badge_starting_position[0])
        badge_icon_y = int((badge_height - badge_icon_height) / badge_icon_placement_y + badge_starting_position[1])
        # Paste the icon onto the plate image
        plate_image.paste(badge_icon, (badge_icon_x, badge_icon_y), badge_icon)
    
    return pass_header

# Function to add badge text (e.g., country code) to the plate
def add_badge_text(draw, badge_config, badge_on_plate_config):
    badge_width = badge_on_plate_config["width"]
    badge_height = badge_on_plate_config["height"]
    badge_starting_position = tuple(badge_on_plate_config["starting_position"])

    badge_text = badge_config["text"]["content"]
    badge_text_font = badge_on_plate_config["text_font"]
    badge_text_size = badge_on_plate_config["text_size"]

    # Path to the font file for badge text
    badge_font_path = os.path.join(sys.path[0], 'fonts', badge_text_font)
    if not os.path.exists(badge_font_path):
        msg = f"Font file '{badge_config['text']['font']}' not found."
        return msg
    badge_font = ImageFont.truetype(badge_font_path, badge_text_size)
    badge_text_dimension = badge_font.getbbox(badge_text)
    
    badge_text_colour = tuple(badge_config["text"]["colour"])
    # Placement ratios from config for fine-tuning text position
    badge_text_placement_x = badge_config["text"]["placement"][0]
    badge_text_placement_y = badge_config["text"]["placement"][1]
    # Calculate text position within the badge rectangle
    badge_text_x = int((badge_width - (badge_text_dimension[2] - badge_text_dimension[0])) / badge_text_placement_x + badge_starting_position[0])
    badge_text_y = int((badge_height - (badge_text_dimension[3] - badge_text_dimension[1])) / badge_text_placement_y + badge_starting_position[1])
    # Draw the badge text
    draw.text((badge_text_x, badge_text_y), badge_text, font=badge_font, fill=badge_text_colour)

    return pass_header

# Function to add the badge (background, text, and icon) to the plate
def add_badge(draw, plate_image, config, size, badge):
    # Check if badge exists in config
    if badge not in config['badges']:
        msg = f"Badge '{badge}' not found in configurations."
        return msg
    else:
        badge_on_plate_config = config['plate_sizes'][size]["badge"]
        badge_width = badge_on_plate_config["width"]
        badge_height = badge_on_plate_config["height"]
        badge_starting_position = tuple(badge_on_plate_config["starting_position"])

        badge_config = config['badges'][badge]
        badge_background_colour = tuple(badge_config["background_colour"])

        # Draw badge background rectangle
        draw.rectangle([badge_starting_position, (badge_width + badge_starting_position[0], badge_height + badge_starting_position[1])], fill=badge_background_colour)

        # Draw badge text (e.g., country code)
        add_badge_text(draw, badge_config, badge_on_plate_config)

        # Draw badge icon (e.g., flag)
        add_badge_icon(plate_image, badge_config, badge_on_plate_config)
    
    return pass_header

# Function to add the main plate number text to the plate
def add_text(draw, plate_image, config, plate_config, size, plate_num, badge, side):
    # Path to the font file for plate text
    text_font_path = os.path.join(sys.path[0], 'fonts', config['text']['font'])
    if not os.path.exists(text_font_path):
        msg = f"{fail_header} Font file '{config['text']['font']}' not found."
        return msg
    text_font = ImageFont.truetype(text_font_path, plate_config['text_size'])
    text_dimension = text_font.getbbox(plate_num) # (left, top, right, bottom) bounding box

    text_rows = plate_config["rows"]
    split_char = config["text"]["split_char"]
    if text_rows > 1:
        # Split the plate number into multiple rows
        text_split = split_text(plate_num, split_char, text_rows)
        text_space_height = 0
        count = 0
        for row in text_split:
            row_dimension = text_font.getbbox(row)
            text_space_height += row_dimension[3] - row_dimension[1]
            count += 1
        text_space_height += plate_config["row_spacing"] * (count - 1)
        current_y = (plate_config['height'] - text_space_height) / 2

        for row in text_split:
            row_dimension = text_font.getbbox(row)
            if row_dimension[2] - row_dimension[0] > plate_image.width:
                msg = f"{fail_header} '{row}' exceeds plate width. Please adjust the plate number or configuration."
                return msg

            # If no badge is chosen, draw the plate number at the centre of image
            if badge == "none":
                text_colour = tuple(config['text']['colour'][side])
                text_x = int(plate_image.width / 2 - (row_dimension[2] - row_dimension[0]) / 2)
                text_y = current_y
                current_y += row_dimension[3] - row_dimension[1] + plate_config["row_spacing"]
                draw.text((text_x, text_y), row, font=text_font, fill=text_colour)

            # If a badge is chosen, draw the plate number with badge offset
            else:
                badge_width = config['plate_sizes'][size]["badge"]["width"]
                # Draw text with horizontal offset for badge
                text_colour = tuple(config['text']['colour'][side])
                text_x = int(badge_width + (plate_image.width - badge_width) / 2 - (row_dimension[2] - row_dimension[0]) / 2)
                text_y = current_y
                current_y += row_dimension[3] - row_dimension[1] + plate_config["row_spacing"]
                draw.text((text_x, text_y), row, font=text_font, fill=text_colour)

    else:
        # If no badge is chosen, draw the plate number at the centre of image
        if badge == "none":
            text_colour = tuple(config['text']['colour'][side])
            text_x = int(plate_image.width / 2 - (text_dimension[2] - text_dimension[0]) / 2)
            text_y = int(plate_image.height / 2 - (text_dimension[3] - text_dimension[1]) / 2)
            draw.text((text_x, text_y), plate_num, font=text_font, fill=text_colour)

        # If a badge is chosen, draw the plate number with badge offset
        else:
            badge_width = config['plate_sizes'][size]["badge"]["width"]
            # Draw text with horizontal offset for badge
            text_colour = tuple(config['text']['colour'][side])
            text_x = int(badge_width + (plate_image.width - badge_width) / 2 - (text_dimension[2] - text_dimension[0]) / 2)
            text_y = int(plate_image.height / 2 - (text_dimension[3] - text_dimension[1]) / 2)
            draw.text((text_x, text_y), plate_num, font=text_font, fill=text_colour)

    return pass_header

# Function to add a watermark to the plate image
def add_watermark(draw, plate_image):
    watermark_text = "TEST"
    watermark_size = 10
    watermark_offset = 15
    watermark_font = "Arial Bold.ttf"
    watermark_font_path = os.path.join(sys.path[0], 'fonts', watermark_font)
    if not os.path.exists(watermark_font_path):
        msg = f"{fail_header} Font file '{watermark_font}' not found."
        return msg
    watermark_font = ImageFont.truetype(watermark_font_path, watermark_size)
    watermark_dimension = watermark_font.getbbox(watermark_text) # (left, top, right, bottom) bounding box

    watermark_colour = tuple([0, 0, 0])
    # Center watermark horizontally, place near bottom
    watermark_x = int(plate_image.width / 2 - (watermark_dimension[2] - watermark_dimension[0]) / 2)
    watermark_y = int(plate_image.height - watermark_offset)
    draw.text((watermark_x, watermark_y), watermark_text, font=watermark_font, fill=watermark_colour)

    return pass_header

# Main function to draw a plate image for a given country, plate number, side, size, and badge
def draw(country, plate_num, side, size, badge):
    watermark = True  # Set to False if you don't want a watermark

    # Load configuration from /config folder
    config_file = os.path.join(sys.path[0], 'configs', f'{country}.json')
    if not os.path.exists(config_file):
        msg = f"{fail_header} Configuration file for {country} not found."
        return msg

    with open(config_file, 'r') as file:
        config = json.load(file)
    
    # Get plate size from configuration
    if size not in config['plate_sizes']:
        msg = f"{fail_header} Size '{size}' not found in configuration."
        return msg

    plate_config = config['plate_sizes'][size]

    plate_background_colour = config['background']['colour'][side]
    plate_background_colour = tuple(plate_background_colour)

    # Create a new image for the plate
    plate_width = plate_config['width']
    plate_height = plate_config['height']

    # Create a new image with the specified background colour
    plate_image = Image.new('RGBA', (plate_width, plate_height), plate_background_colour)
    draw = ImageDraw.Draw(plate_image)

    # Add text to the plate
    add_text_result = add_text(draw, plate_image, config, plate_config, size, plate_num, badge, side)
    if add_text_result.startswith(fail_header):
        return add_text_result
    
    if watermark:
        add_watermark_result = add_watermark(draw, plate_image)
        if add_watermark_result.startswith(fail_header):
            return add_watermark_result

    # Add badge to the plate (if any)
    if badge != "none":
        add_badge_result = add_badge(draw, plate_image, config, size, badge)
        if add_badge_result.startswith(fail_header):
            return add_badge_result

    # Save the image to file
    plate_image_path = os.path.join(sys.path[0], 'output', f'{country}_{plate_num}_{side}.png')
    plate_image_path = plate_image_path.replace(' ', '_')  # Replace spaces with underscores in the filename
    os.makedirs(os.path.dirname(plate_image_path), exist_ok=True)
    plate_image.save(plate_image_path)

    return plate_image_path

def draw_and_validate(country, plate_num, side, size, badge):
    result = draw(country, plate_num, side, size, badge)
    if result.startswith(fail_header):
        print(f"Unable to generate plate image '{plate_num}' for the following reason:")
        print(result.strip(fail_header))
        plate_image_path = os.path.join(sys.path[0], 'output', f'{country}_{plate_num}_{side}.png')
        if os.path.exists(plate_image_path):
            os.remove(plate_image_path)
        print(f"Plate image file '{plate_image_path}' has been removed due to failure.")
        return "Fail"
    else:
        print(f"Plate image saved to: {result}")
        return "Pass"

# Sample usage (generates several example plates)

if __name__ == "__main__":
    country = input("Enter country code (e.g., 'GB'): ").strip()
    plate_num = input("Enter plate number: ").strip()
    side = input("Enter side ('front' or 'rear'): ").strip().lower()
    size = input("Enter plate size (e.g., 'oblong'): ").strip()
    badge = input("Enter badge (or 'none'): ").strip().lower()

    draw_and_validate(country, plate_num, side, size, badge)
    