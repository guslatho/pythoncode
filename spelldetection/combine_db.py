# Combines the wiktionary and molex database into one (priority given to molex)

from csv import writer
import pandas as pd
import numpy as np

molex = pd.read_csv('molex_db.csv', header=None)
wikt = pd.read_csv('wikt_db.csv', header=None)

found_count = 0
notfound_count = 0
count = 169384

def write_to_csv(output_list):
    with open('molex_modif_db.csv', 'a', encoding="utf-8", newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(output_list)
        f_object.close()  

for word in range(1,len(wikt.iloc[:,0])):
    current_word = wikt.iloc[word,0]
    found = molex.iloc[:,1][molex.iloc[:,0]==current_word]
    if len(found) > 0:
        found_count += 1
    else:
        notfound_count += 1
        #print(current_word)
        hyphenated_word = wikt.iloc[word,1]
        hyphenated_word = hyphenated_word.replace('·','|')
        word_type = wikt.iloc[word,3]
        if 'n' in str(word_type):
            molex_type = 'NOU-C'
        elif 'p' in str(word_type):
            molex_type = 'NOU-P'
        elif 'v' in str(word_type):
            molex_type = 'VRB'
        word_output = [current_word,hyphenated_word,'',molex_type]
        write_to_csv(word_output)
    count += 1
    if str(count)[-3:] == '000':
        print(count)
        
        
