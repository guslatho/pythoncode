# * Wiktionary Export Module *
# Takes a Dutch wiktionary image file and converts it to a cvs database file.
# See https://dumps.wikimedia.org/nlwiktionary
# Example input:'nlwiktionary-20240201-pages-articles.xml'
# ! ~ Work in progress | non-definitive version ~ !

import xml.etree.ElementTree as ET
from csv import writer

# Main function to retrieve a hyphenated word from a word page.
def retrieve_hyphenated_version(word_text):
    pos = word_text.find('{{-syll-}}') + 12  # Add 12 to byass the '{{-syll-}}' tag 
    start_pos = pos 
    
    if '{{syll' in word_text[pos:pos+6]:
        pattern = 1
        pos += 7 
        start_pos += 7
    elif word_text[pos] == '[':
        pattern = 2
        pos += 3 
        start_pos += 3
    else:
        pattern = 0

    # Sometimes a word entry is shifted one to the left, check and compensate
    if ((word_text[pos-1].isalpha() == True)
        or (word_text[pos-1] in '0123456789')):
        print('SHIFT EXECUTED!: ' + repr(word_text[pos-1:pos+99]))
        pos -= 1
        start_pos -= 1    

    word_end = False
    word_end_two = False  
    # Cycle through each character to check whether word has ended
    while word_end == False:
        current_char = word_text[pos:pos+1]
        if ((current_char.isalpha() == True)
            or (current_char in '1234567890·|/ -!<>.\'')):
            pos += 1            
        else:
            full_word = word_info[start_pos:pos]
            word_end = True
            # In pattern 1 syllables are seperated by '|' instead of '·'
            if pattern == 1:
                full_word = full_word.replace('|','·')

    # For words with 2 hyphenation versions, if not set to ''
    if pattern == 2:
        pos += 6
        start_pos = pos      
        while word_end_two == False:
            current_char = word_text[pos:pos+1]
            if ((current_char.isalpha() == True)
                or (current_char in '1234567890·|/ -!<>.\'')):
                pos += 1                
            else:
                full_word_two = word_info[start_pos:pos]
                word_end_two = True
                if pattern == 1:
                    full_word_two = full_word.replace('|','·')
    else:
        full_word_two = ''
        
    return [full_word,full_word_two]

# Identifies whether a given word is a loan-word.
def is_loanword(word_text):
    loanword_string = ''
    # (Exclude the l from leenwoord in case it non-capitalized (unnecessary??))
    if 'eenwoord uit het Frans' in word_text:
        loanword_string += 'F'
    if 'eenwoord uit het Duits' in word_text:
        loanword_string += 'G'
    if 'eenwoord uit het Engels' in word_text:
        loanword_string += 'E'
    if 'eenwoord uit het Latijn' in word_text:
        loanword_string += 'L'
    if 'eenwoord uit het Arabisch' in word_text:
        loanword_string += 'A'
    if 'eenwoord uit het Italiaa' in word_text:
        loanword_string += 'I'
    if 'eenworod uit het Spaans' in word_text:
        loanword_string += 'S'
    return loanword_string

# Identifies whether a given word is found in the original Dutch dictionary.
def is_dictionary_word(word_text):
    if '{{wel-GB}}' in word_text:
        return 'Y'
    # '{{niet-GB' instead of '{{niet-GB}}', sometimes it's listed as '{{niet-GB|0'
    elif '{{niet-GB' in word_text:
        return 'N'
    else:
        return 'NA'

# Scan to check whether word is a noun etc., see instructions for coding legend
def word_type(word_text):
    word_type_string = ''
    if ('{{-verb-|nld}}' in word_text) or ('{{-verb-|0}}' in word_text):
        word_type_string += 'v'
    if ('{{-noun-|nld}}' in word_text) or ('{{-noun-|0}}' in word_text):
        word_type_string += 'n'
    if '{{-name-|nld}}' in word_text:
        word_type_string += 'p'
    if '{{-nlpronom-pers-}}' in word_text:
        word_type_string += 'r'
    if ('{{-adjc-|nld}}' in word_text) or (('{{-adjc-|0}}' in word_text)):
        word_type_string += 'a'
    if '{{-adverb-|nld}}' in word_text:
        word_type_string += 'd'
    if '{{-art-|nld}}' in word_text:
        word_type_string += 't'
    if '{{-num-|nld}}' in word_text:
        word_type_string += 'u'
    if '{{-conj-|nld}}' in word_text:
        word_type_string += 'c'
    if '{{-prep-|nld}}' in word_text:
        word_type_string += 'o'
    if '{{-interj-|nld}}' in word_text:
        word_type_string += 'i'
    if '{{-abbr-|nld}}' in word_text:
        word_type_string += 'b'
    return word_type_string

# Clean a retrieved word: remove unnecessary spaces, character etc.
def clean_word(word):
    if word[-1:] == '\n':
        word = word[:-1]

    # For words with space at the start
    if (word != '') and (word[0] == ' '):
        word = word[1:]

    # For words with umlaut ("mais")
    if (word != '') and (',' in word):
        word = word.replace(',','')

    # For words with hyphenation in the middle (New - Jersey)
    if ' - ' in word:
        word = word.replace(' - ','-')

    # For Hebrew words (p<u>oo</u>rsjen)
    if '<u>' in word:
        word = word.replace('<u>','')
        word = word.replace('</u>','')

    return word

# Remove hyphenated characters from word (outputs original)
def remove_hyph_characters(word):   
    return word.replace('·','')

def write_to_csv(output_list):
    with open('output.csv', 'a', encoding="utf-8", newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(output_list)
        f_object.close()    

# Main loop. Use iterparse because of large file size
context = ET.iterparse('nlwikt.xml',events=["start", "end"])

# last_word_info to prevent duplicate processing, counter for processing progress
last_word_info = 'x'
counter=0

for event in context:
    event_type, element = event
    if element.tag == '{http://www.mediawiki.org/xml/export-0.10/}text':
        if '{{=nld=}}' in str(element.text):  # '{{=nld=}}' signifies a word entry
            word_info = element.text
            if word_info == last_word_info:  # If same as last entry, skip (duplicate)
                continue
            else:
                last_word_info = word_info

            leenwoord = is_loanword(word_info)
            woordenlijst = is_dictionary_word(word_info)
            woordtype = word_type(word_info)

            hyphenated_word_one, hyphenated_word_two = retrieve_hyphenated_version(word_info)
            hyphenated_word_one = clean_word(hyphenated_word_one)           

            original = remove_hyph_characters(hyphenated_word_one)
            
            output_list = [original, hyphenated_word_one, hyphenated_word_two,
                           woordtype, leenwoord, woordenlijst]

            # Filter empty words/words starting or ending with syllable symbol
            if (hyphenated_word_one != ''
                and hyphenated_word_one[0] != '·'
                and hyphenated_word_one[-1] != '·'
                and len(hyphenated_word_one)>1):
                write_to_csv(output_list)
                        
            counter += 1
            if str(counter)[-4:] == '0000':
                print(counter)

    if event_type == "end":
        element.clear()
