from identify import getIPs
from geoIP import jsonGEO
from RDAP import getRDAPtxt
from config import directory
import json
import threading
from multiprocessing import Process

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
print(geoFile)

def pullRDAP():
    rdapFile = getRDAPtxt(ipArray)
    return(rdapFile)

i = 0

thread = threading.Thread(target=pullRDAP, args=())
thread.daemon = True
thread.start()

print(' ')

from query import queryValidator, queryDataValidator


def userQueryFunc(userType, userQuery):

    if userType == 'd':
        response = queryDataValidator(userQuery)
        print(response)
        print(' ')
    elif userType == 'i':
        response = queryValidator(userQuery)
        print(response)
        print(' ')
    else:
        print('Type not supported! Try again!')
        print(' ')


i = 0
while i < 1:
    userType = input("Would you like to pull data or IPs with your query? (d or i)")
    userQuery = input('Insert Query Here: ')
    userQueryFunc(userType, userQuery)
