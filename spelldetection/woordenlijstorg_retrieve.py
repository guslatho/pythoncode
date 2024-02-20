# * Woordenlijst.org Scrape Module *
# This module queries woordenlijst.org for a specific word and returns the
# respective orthographic hyphenated notation as written on the site.
#
# Requires internet access
# ! ~ Work in progress | non-definitive version ~ !

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


# MAIN FUNCTION
# Executes the 2 primary subfunctions, one for scraping from woordenlijst.org,
# second for extracting info
def get_wl_word(word):
    scraped_string = scrape_word(word)
    hyphenated_word = get_hyphenation(scraped_string, word)
    return hyphenated_word


# Scrapes a word from the woordenlijst.org site and outputs as string. Note that
# woordenlijst.org site employs javascript so the hyphenated version so words cannot
# be retrieved by simple html request. Instead an request XML-file input.
def scrape_word(word):
    target_word = word
    url = ('https://woordenlijst.org/MolexServe/lexicon/find_wordform?'
          + 'database=gig_pro_wrdlst&wordform=' + target_word
          + '&part_of_speech=&paradigm=true&diminutive=true&onlyvalid'
          + '=true&regex=false&dummy=1707823204791')
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="xml")
    soup_string = str(soup)
    return soup_string

# Takes the string, interprets it as XML and filters hyphenation pattern
def get_hyphenation(soup_string, word):
    root = ET.fromstring(str(soup_string))
    # Collapse the whole XML structure into 1 level since only interest is hyphenation
    # Look for the word that matches the original 1:1 and return that
    for elem in list(root.iter()):
        if elem.tag == 'hyphenation':
            returned_word = elem.text.replace('|','')
            if word == returned_word:
                return elem.text.replace('|','-')
    # If the word isn't in the woordenlijst.org library return None
    return None
