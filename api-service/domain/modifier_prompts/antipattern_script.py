# Importing necessary libraries
import nltk
import re

# Downloading necessary NLTK packages
nltk.download('averaged_perceptron_tagger')

# Function to tokenize and tag the input sentence
def tokenize_and_tag(sentence):
    # Tokenizing the sentence
    tokens = nltk.word_tokenize(sentence)
    # Tagging the tokens
    tagged_tokens = nltk.pos_tag(tokens)
    return tagged_tokens

# Function to create antipatterns
def create_antipattern(tagged_tokens):
    # Starting the antipattern
    antipattern = "<antipattern>\n"
    
    i = 0
    while i < len(tagged_tokens):
        token, tag = tagged_tokens[i]
        
        if tag =='.': tag = 'PCT' # punctuation mark

        # handling parentheses
        if tag == "(":
            antipattern += f'<token regexp="yes">'
            i += 1
            while i < len(tagged_tokens):
                token, tag = tagged_tokens[i]
                if tag == ")":
                    antipattern = antipattern[:-1] #remove |
                    antipattern += f"</token>\n"
                    break
                else:
                    antipattern += f"{token}|"
                i += 1
        
        
        # handling exceptions
        elif token == "!":
            # <exception regexp="yes">swim|run|walk</exception>
            i += 1  
            antipattern += f'<exception regexp="yes">'
            antipattern += tagged_tokens[i][0] + "|"
            i += 1
            while i < len(tagged_tokens):
                token, tag = tagged_tokens[i]
                if token == "!":
                    i += 1
                    antipattern += tagged_tokens[i][0] + "|"
                    i += 1
                else:
                    break
            
            antipattern = antipattern[:-1] #remove |
            antipattern += f"</exception>\n"

        
        
        
        else:
            antipattern += f'<token postag="{tag}">{token}</token>\n'
        i += 1
    
    # Closing the antipattern
    antipattern += "</antipattern>\n"
    return antipattern

# Testing the functions
# sentence = "And now for something completely different. I am the best, and better. one # !dslkfnj"

sentence = "There (is was) a fight. believes !hi !ho !jui"
tagged_tokens = tokenize_and_tag(sentence)
antipattern = create_antipattern(tagged_tokens)
print(antipattern)
