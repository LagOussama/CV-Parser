import re


def get_soundex_code(word):
    '''
    Generates the Soundex code for a given word
    Parameters:
      word (string): word for which the Soundex code is to be generated
    Returns: Soundex code
    '''
    # Define the Soundex consonant mappings
    soundex_mappings = {'1': ['b', 'f', 'p', 'v'], 
                        '2': ['c', 'g', 'j', 'k', 'q', 's', 'x', 'z'], 
                        '3': ['d', 't'], 
                        '4': ['l'], 
                        '5': ['m', 'n'], 
                        '6': ['r']}
    
    # Transpose the mappings to create a lookup table for convenience   
    soundex_mapping_table = {}
    for val,ch_list in soundex_mappings.items():
        for ch in ch_list:
            soundex_mapping_table[ch] = val
    # Convert the word to lower case for consistent lookups
    word = word.lower()
    # Save the first letter of the word
    first_letter = word[0]
    # Remove all occurrences of 'h' and 'w' except first letter
    code = first_letter + re.sub(r'[hw]*', '', word[1:])
    # Replace all consonants (include the first letter) with digits based on Soundex mapping table
    code = ''.join([soundex_mapping_table.get(ch, ch) for ch in code])
    # Replace all adjacent same digits with one digit
    code = re.sub(r'([1-6])\1+', r'\1', code)
    # Remove all occurrences of a, e, i, o, u, y except first letter
    code = code[0] + re.sub(r'[aeiouy]*', '', code[1:])
    # If first symbol is a digit replace it with the saved first letter
    code = re.sub(r'[1-6]', first_letter, code[0]) + code[1:]
    # Append 3 zeros if result contains less than 3 digits
    code = code + '000' if len(code) <= 3 else code
    # Retain the first 4 characters
    code = code[:4]
    # Convert to upper case and return
    return code.upper()