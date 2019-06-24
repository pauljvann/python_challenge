from identify import getIPs
from geoIP import jsonGEO
from RDAP import getRDAPtxt
from config import directory
import json

ipArray = []

fileName = input('Input path to text file: ')
ipText = getIPs(fileName)

with open(ipText, 'r') as file:
    lineArray = file.readlines()

for line in lineArray:
    jsonLine = json.loads(line)
    for ip in jsonLine:
        ipArray.append(ip)

geoFile = jsonGEO(ipArray)

rdapFile = getRDAPtxt(ipArray)

import existingData
