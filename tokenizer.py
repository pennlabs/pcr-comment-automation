# Checks if a character is alphanumeric or an ampersand. The latter is included
# as an exception because we do not want to tokenize phrases like "M&T" as 3
# separate tokens.

def isWordCharacter(c):
    return str.isalnum(c) or c == "&"
 
 # Main tokenizer function.
def tokenize(s):
    tokens = []
    charIndex = 0
 
    # Short-circuit the function if the input string is empty.
    if s == "":
        return tokens
 
    # Use try to iterate through characters and build a list of tokens, then
    # use except to output the tokens when the loops cause an IndexError
    # due to arriving at the end of the string.


    try:
        while charIndex < len(s):
            wordToken = ""
            if isWordCharacter(s[charIndex]):
                while isWordCharacter(s[charIndex]):
                    wordToken = wordToken + s[charIndex]
                    charIndex = charIndex + 1
                tokens.append(wordToken)
            else:
                while not isWordCharacter(s[charIndex]):
                    wordToken = wordToken + s[charIndex]
                    charIndex = charIndex + 1
                tokens.append(wordToken)
    except IndexError as e:
        tokens.append(wordToken)
        return tokens
    return tokens