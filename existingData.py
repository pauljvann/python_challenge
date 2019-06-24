import json
import os
from math import radians, cos, sin, asin, sqrt
import datetime
import dateutil.parser
import re
from config import directory
from query import queryValidator, queryDataValidator


def getGeoIpData():

    geoIPData = {}

    with open(directory + '/geo.txt', 'r') as file:
        lineArray = file.readlines()

    for line in lineArray:
        jsonLine = json.loads(line)
        for ip in jsonLine:
            geoIPData[str(ip)] = jsonLine[str(ip)]

    return(geoIPData)

geoIPData = getGeoIpData()



def getRdapData():

    rdapData = {}

    path = directory + '/RDAPfiles'
    rdapFiles = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                rdapFiles.append(os.path.join(r, file))

    numRDAPFiles = len(rdapFiles)
    if numRDAPFiles == 50:
        print('RDAP data gathering complete')
    else:
        print('RDAP data gathering is ' + str((numRDAPFiles/50) * 100) + '% complete.  While you wait, you can still query the RDAP data that already exists and the Geo IP data')

    for rdapFile in rdapFiles:

        with open(rdapFile, 'r') as file:
            lineArray = file.readlines()

        for line in lineArray:
            jsonLine = json.loads(line)
            for data in jsonLine:
                for ip in data:
                    rdapData[ip] = data[ip]
    return(rdapData)

rdapData = getRdapData()


rdapTags = []
geoTags = []


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
