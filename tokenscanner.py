


def isWordCharacter(c):
    return str.isalnum(c) or c == '\'' or c == "&"

def tokenize(s):
    tokens = []
    charIndex = 0
    if s == "" or s == "&":
        return tokens
    while charIndex < len(s):
        wordToken = ""
        if isWordCharacter(s[charIndex]):
            while isWordCharacter(s[charIndex]):
                wordToken = wordToken + s[charIndex]
                charIndex = charIndex + 1
            tokens.append(wordToken)
            wordToken = ""
        else:
            while not isWordCharacter(s[charIndex]):
                wordToken = wordToken + s[charIndex]
                charIndex = charIndex + 1
            tokens.append(wordToken)
            wordToken = ""
        charIndex = charIndex + 1
    return tokens

  #
  # def next():
  #   comment = ""
  #   if (c == -1) throw new NoSuchElementException
  #     if isWordCharacter(c):
  #       while isWordCharacter(c):
  #         buf.write(c)
  #         c = r.read()
  #     else:
  #       while !isWordCharacter(c) and c != -1:
  #         buf.write(c)
  #         c = r.read()
  #     buf.close()
  #   return buf.toString()
  #
  #
