#Split a plate number into several sections, using a specified split character and number of parts.
def split(input_string, split_char, num_parts):
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


# Example usage
print(split("GX-999-X-23-D", "-", 3))
print(split("BX25 AEY", " ", 1))
print(split("AB 123CD", " ", 1))