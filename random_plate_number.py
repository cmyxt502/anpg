import random
import string

def random_uk_plate_number(max_year):
    # Generate random area code (2 uppercase letters)
    area_code = ''.join(random.choices(string.ascii_uppercase, k=2))

    incl_second_half = False
    # Generate random year code (2 digits)
    if max_year > 50:
        max_year -= 50
        incl_second_half = True
        
    year_code_a = random.randint(0, max_year)
    
    if incl_second_half:
        year_code_b = random.randint(51, max_year + 50)
    else:
        year_code_b = random.randint(51, max_year + 49)
    
    year_code_str = random.choice([f"{year_code_a:02d}", f"{year_code_b:02d}"])

    # Generate random random letters (3 uppercase letters)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))

    # Combine into plate format
    plate_number = f"{area_code}{year_code_str} {random_letters}"
    return plate_number
