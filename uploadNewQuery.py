from identify import getIPs
from geoIP import jsonGEO
from RDAP import getRDAPtxt
from config import directory
import json
import threading
from multiprocessing import Process

ipArray = []

fileName = input('Input path to text file: ') #takes text file of IP's and random text as input
ipText = getIPs(fileName)

with open(ipText, 'r') as file:
    lineArray = file.readlines()

for line in lineArray:
    jsonLine = json.loads(line)
    for ip in jsonLine:
        ipArray.append(ip) #identifies IP addresses in text file and appends them to array

geoFile = jsonGEO(ipArray) #pulls GEO data
print(geoFile)

def pullRDAP():
    rdapFile = getRDAPtxt(ipArray)  #pulls RDAP Data
    return(rdapFile)

i = 0

thread = threading.Thread(target=pullRDAP, args=()) #threads RDAP data to pull data while also allowing for queries
thread.daemon = True
thread.start()

print(' ')

from query import queryValidator, queryDataValidator 


def userQueryFunc(userType, userQuery): #query function to allow users to run queries

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
    userType = input("Would you like to pull data or IPs with your query? (d or i)") #takes user query type input
    userQuery = input('Insert Query Here: ') #takes user query content input
    userQueryFunc(userType, userQuery)
