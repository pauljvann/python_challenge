from identify import getIPs
from geoIP import jsonGEO
from RDAP import getRDAPtxt
from config import directory
import json

ipArray = []

fileName = input('Input path to text file: ') 
ipText = getIPs(fileName) # takes text file of ip's and random text as input

with open(ipText, 'r') as file:
    lineArray = file.readlines()

for line in lineArray:
    jsonLine = json.loads(line)
    for ip in jsonLine:
        ipArray.append(ip) #appends IP's in text file to ip Array

geoFile = jsonGEO(ipArray) #pulls geo data

rdapFile = getRDAPtxt(ipArray) #pulls RDAP data

import existingData #allows users to run queries on data
