#Split a plate number into two halves
#Thanks ChatGPT:)
def splitText(input_string):
    # Find the index of the first space character
    space_index = input_string.find(" ")
    
    # Split the string at the space index
    first_half = input_string[:space_index]
    second_half = input_string[space_index+1:]
    
    # Calculate the length of each half
    half_length = len(input_string) // 2
    
    # If the second half is longer than the first half and is splitable, adjust the split point
    while len(second_half) > half_length and " " in second_half:
        space_index = second_half.rfind(" ", 0, half_length)
        first_half += " " + second_half[:space_index]
        second_half = second_half[space_index+1:]
    
    # Strip leading and trailing spaces from the first and second halves
    first_half = first_half.strip()
    second_half = second_half.strip()

    # Return the two halves as a tuple
    return (first_half, second_half)