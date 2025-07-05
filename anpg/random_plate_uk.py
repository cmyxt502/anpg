import random
import string

import generate
import json

import os, sys
# Add the parent directory to the system path to allow importing local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Generate a random Great Britain plate number
def random_gb_plate_number(max_year):
    # Generate random area code (2 uppercase letters)
    area_code = ''.join(random.choices(string.ascii_uppercase, k=2))

    incl_second_half = False
    # Determine if we should include the second half of the year (September registrations)
    if max_year > 50:
        max_year -= 50
        incl_second_half = True
        
    # Generate a random year code for the first half (March registrations)
    year_code_a = random.randint(0, max_year)
    
    # Generate a random year code for the second half (September registrations)
    if incl_second_half:
        year_code_b = random.randint(51, max_year + 50)
    else:
        year_code_b = random.randint(51, max_year + 49)
    
    # Randomly choose between first half or second half year code
    year_code_str = random.choice([f"{year_code_a:02d}", f"{year_code_b:02d}"])

    # Generate random letters for the last part of the plate (3 uppercase letters)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    # Combine all parts into the standard UK plate format
    plate_number = f"{area_code}{year_code_str} {random_letters}"
    return plate_number

# Generate a random Northern Ireland plate number
def random_ni_plate_number():
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    random_numbers = ''.join(str(random.randint(1000, 9999)))
    plate_number = f"{random_letters} {random_numbers}"
    return plate_number

if __name__ == "__main__":
    # Ask user for number of plates and current year
    style = input("Enter the plate region, GB or NI: ")
    i = int(input("Enter the number of random plates to generate: "))
    cyr = int(input("Enter the current year: "))
    for i in range(i):
        # Generate a random plate number
        if style == "GB":
            plate = random_gb_plate_number(cyr)
        elif style == "NI":
            plate = random_ni_plate_number()
        else:
            print("Fail")
        country = 'GB' # ISO 3166 irrespective of actual GB or NI
        # Load the ISO 3166 GB config file
        config_file = os.path.join(sys.path[0], 'anpg', 'configs', f'{country}.json')
        with open(config_file, 'r') as f:
            gb_config = json.load(f)
        # Randomly select a plate size and badge from the config
        random_size = random.choice(list(gb_config.get('plate_sizes', {}).keys()))
        random_badge = random.choice(list(gb_config.get('badges', {}).keys()))
        # Generate and validate a front plate
        generate.draw_and_validate('GB', plate, 'front', random_size, random_badge)
        # Generate and validate a rear plate with the same random parameters
        generate.draw_and_validate('GB', plate, 'rear', random_size, random_badge)