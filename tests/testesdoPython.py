# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 19:19:26 2023

@author: bmaro
"""

#import lxml
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

with open('Vandelli.xml', 'r', encoding=("utf8")) as f:
    mytree = ET.parse(f)
myroot = mytree.getroot()
#print(myroot.tag)
#print(myroot[0].tag)

for x in myroot.findall(".//term[@senseNumber='2']"):
    print(x.text)



#    soup = BeautifulSoup(f, "xml")

#print(soup)
#tag = soup.term
