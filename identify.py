import re
import json
from config import directory

def getIPs(fileName):

    with open(fileName, 'r') as file:
        lineArray = file.readlines()

    ipAddresses = [] #array of all identified ip addresses

    for line in lineArray:
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line) #simple rejex pattern to find all ip addresses in each line
        for ip in ips:
            ipAddresses.append(ip)

    fileSave = directory + '/ipFinal.txt' 
    with open(fileSave, 'w') as file:
         file.write(json.dumps(ipAddresses)) #saves and writes new text file comprised of only the identified IP addresses

    return(fileSave) #returns filename of new text file
