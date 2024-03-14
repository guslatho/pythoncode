import xml.etree.ElementTree as ET
from csv import writer
import time

context = ET.iterparse('molex_22.xml',events=["start", "end"])

def write_to_csv(output_list):
    with open('output.csv', 'a', encoding="utf-8", newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(output_list)
        f_object.close()  

counter = 0
preceding_ele = 'x'
written = False
word_array = []
word_type = '' 

for event in context:
    event_type, element = event
    # If tag = entry: start stop determinator of word.
    if element.tag == '{http://www.tei-c.org/ns/1.0}entry':
        if written == False:
            for word in word_array:
                write_to_csv([word[0],word[1],word_type])
                #flub
            word_array = []
            written = True


    # Tag for normally written version of word
    if element.tag == '{http://www.tei-c.org/ns/1.0}orth':
        orthographic = element.text
        written = False

    # Tag for hyphenated version
    if element.tag == '{http://www.tei-c.org/ns/1.0}hyph':
        hyphenation = element.text
        if (hyphenation != None and
            [orthographic, hyphenation] not in word_array):
            word_array.append ([orthographic, hyphenation])
            if str(counter)[-4:]=='0000':
                print(counter)
                    counter += 1
        written = False
        preceding_ele = element


    if str(element.attrib) == "{'type': 'pos'}":
        word_type = element.text
        written = False
        #print(element.attrib)

    

    



    
    




