from PIL import Image, ImageDraw, ImageFont
import json
import os, sys

# Function to add badge icon to the plate
def add_badge_icon(plate_image, badge_config, badge_on_plate_config):
    badge_width = badge_on_plate_config["width"]
    badge_height = badge_on_plate_config["height"]
    badge_starting_position = tuple(badge_on_plate_config["starting_position"])
    
    badge_icon_size = badge_on_plate_config["icon_size"]
    badge_icon_file = badge_config["icon"]["content"]
    badge_icon_file = os.path.join(sys.path[0], 'badges', 'icons', f'{badge_icon_file}.png')

    if os.path.exists(badge_icon_file):
        badge_icon = Image.open(badge_icon_file).convert("RGBA")
        badge_icon = badge_icon.resize((badge_icon_size, badge_icon_size))
        badge_icon_placement_x = badge_config["icon"]["placement"][0]
        badge_icon_placement_y = badge_config["icon"]["placement"][1]
        badge_icon_x = int((badge_width - badge_icon_size) / badge_icon_placement_x + badge_starting_position[0])
        badge_icon_y = int((badge_height - badge_icon_size) / badge_icon_placement_y + badge_starting_position[1])
        plate_image.paste(badge_icon, (badge_icon_x, badge_icon_y), badge_icon)

# Function to add badge text to the plate
def add_badge_text(draw, badge_config, badge_on_plate_config):
    badge_width = badge_on_plate_config["width"]
    badge_height = badge_on_plate_config["height"]
    badge_starting_position = tuple(badge_on_plate_config["starting_position"])

    badge_text = badge_config["text"]["content"]
    badge_text_font = badge_config["text"]["font"]
    badge_text_size = badge_on_plate_config["text_size"]

    badge_font_path = os.path.join(sys.path[0], 'fonts', badge_text_font) # TODO: allocate a font path for the badge text
    if not os.path.exists(badge_font_path):
        print(f"Font file '{badge_config['text']['font']}' not found.") # TODO: change error message
        return None
    badge_font = ImageFont.truetype(badge_font_path, badge_text_size)
    badge_text_dimension = badge_font.getbbox(badge_text)
    
    badge_text_colour = tuple(badge_config["text"]["colour"])
    badge_text_placement_x = badge_config["text"]["placement"][0]
    badge_text_placement_y = badge_config["text"]["placement"][1]
    badge_text_x = int((badge_width - (badge_text_dimension[2] - badge_text_dimension[0])) / badge_text_placement_x + badge_starting_position[0])
    badge_text_y = int((badge_height - (badge_text_dimension[3] - badge_text_dimension[1])) / badge_text_placement_y + badge_starting_position[1])
    draw.text((badge_text_x, badge_text_y), badge_text, font=badge_font, fill=badge_text_colour)

# Function to add badge to the plate
def add_badge(draw, plate_image, config, size, badge):
    # Load badge config
    if badge not in config['badges']:
        print(f"Badge '{badge}' not found in configurations.")
        return None
    else:
        badge_on_plate_config = config['plate_sizes'][size]["badge"]
        badge_width = badge_on_plate_config["width"]
        badge_height = badge_on_plate_config["height"]
        badge_starting_position = tuple(badge_on_plate_config["starting_position"])

        badge_config = config['badges'][badge]
        badge_background_colour = tuple(badge_config["background_colour"])

        # Draw badge
        draw.rectangle([badge_starting_position, (badge_width + badge_starting_position[0], badge_height + badge_starting_position[1])], fill=badge_background_colour)

        # Draw text (country identifier)
        add_badge_text(draw, badge_config, badge_on_plate_config)

        # Draw icon (flag)
        add_badge_icon(plate_image, badge_config, badge_on_plate_config)

def add_text(draw, plate_image, config, size, plate_num, badge, side):
    text_font_path = os.path.join(sys.path[0], 'fonts', config['text']['font'])
    if not os.path.exists(text_font_path):
        print(f"Font file '{config['text']['font']}' not found.")
        return None
    text_font = ImageFont.truetype(text_font_path, config["plate_sizes"][size]['text_size'])
    text_dimension = text_font.getbbox(plate_num) # Result (left, top, right, bottom) bounding box

        # If no badge is chosen, draw the plate number at the centre of image
    if badge == "none":
        text_colour = tuple(config['text']['colour'][side])
        text_x = int(plate_image.width / 2 - (text_dimension[2] - text_dimension[0]) / 2)
        text_y = int(plate_image.height / 2 - (text_dimension[3] - text_dimension[1]) / 2)
        draw.text((text_x, text_y), plate_num, font=text_font, fill=text_colour)

    # If a badge is chosen, draw the plate number with badge offset
    else:
        badge_width = config['plate_sizes'][size]["badge"]["width"]
        # Draw text
        text_colour = tuple(config['text']['colour'][side])
        text_x = int(badge_width + (plate_image.width - badge_width) / 2 - (text_dimension[2] - text_dimension[0]) / 2) # Including offset for badge
        text_y = int(plate_image.height / 2 - (text_dimension[3] - text_dimension[1]) / 2)
        draw.text((text_x, text_y), plate_num, font=text_font, fill=text_colour)

def add_watermark(draw, plate_image, config):
    watermark_text = "BRITEM GRAPHICS"
    watermark_size = 10
    watermark_offset = 15
    watermark_font = "Arial Bold.ttf"
    watermark_font_path = os.path.join(sys.path[0], 'fonts', watermark_font)
    if not os.path.exists(watermark_font_path):
        print(f"Font file '{watermark_font}' not found.")
        return None
    watermark_font = ImageFont.truetype(watermark_font_path, watermark_size)
    watermark_dimension = watermark_font.getbbox(watermark_text) # Result (left, top, right, bottom) bounding box

    watermark_colour = tuple([0, 0, 0])
    watermark_x = int(plate_image.width / 2 - (watermark_dimension[2] - watermark_dimension[0]) / 2)
    watermark_y = int(plate_image.height - watermark_offset)
    draw.text((watermark_x, watermark_y), watermark_text, font=watermark_font, fill=watermark_colour)

# Import JSON configuration from config folder
def draw(country, plate_num, side, size, badge):
    watermark = True  # Set to False if you don't want a watermark

    # Load configuration from /config folder
    config_file = os.path.join(sys.path[0], 'configs', f'{country}.json')
    if not os.path.exists(config_file):
        print(f"configuration file for {country} not found.")
        return None
    
    with open(config_file, 'r') as file:
        config = json.load(file)
    
    # Get plate size from configuration
    if size not in config['plate_sizes']:
        print(f"Size '{size}' not found in configuration.")
        return None

    plate_size = config['plate_sizes'][size]

    plate_background_colour = config['background']['colour'][side]
    plate_background_colour = tuple(plate_background_colour)

    # Create a new image for the plate
    plate_width = plate_size['width']
    plate_height = plate_size['height']

    # Create a new image with the specified background colour
    plate_image = Image.new('RGBA', (plate_width, plate_height), plate_background_colour)
    draw = ImageDraw.Draw(plate_image)

    # Add text to the plate
    add_text(draw, plate_image, config, size, plate_num, badge, side)
    if watermark:
        add_watermark(draw, plate_image, config)

    # Add badge to the plate
    if badge != "none":
        add_badge(draw, plate_image, config, size, badge)

    # Save the image to file
    plate_image_path = os.path.join(sys.path[0], 'output', f'{country}_{plate_num}_{side}.png')
    os.makedirs(os.path.dirname(plate_image_path), exist_ok=True)
    plate_image.save(plate_image_path)

    return plate_image_path

# Sample usage
draw('GB', 'BX22 BEM', 'rear', 'oblong', 'ev')
draw('GB', 'BX25 BEM', 'front', 'oblong', 'pre_brexit_gb')
draw('GB', 'BX24 BEM', 'rear', 'square_lowerbadge', 'pre_brexit_gb')
draw('GB', 'BX73 BEM', 'front', 'oblong', 'none')
draw('GB', 'BX72 BEM', 'rear', 'square_fullbadge', 'pre_brexit_gb')
draw('NL', '99-BEM-9', 'rear', 'oblong', 'eu')
draw('NL', '99-BEM-9', 'front', 'oblong', 'eu')