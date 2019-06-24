import requests
import json
from config import directory
from joblib import Parallel, delayed
import multiprocessing
import pickle
import os
import threading

easyAccess = ['handle', 'startAddress', 'endAddress', 'ipVersion', 'name', 'parentHandle', 'type', 'country']
easyAccessEntity = ['handle', 'roles']

def getRDAP(ip):
    rdapRequest = 'https://rdap.arin.net/registry/ip/' + ip
    rdapResponse = requests.get(rdapRequest)
    rdapData = rdapResponse.json()
    return(rdapData)

def pullEntityData(start, saveTo):
    for entity in start:
        entityIndex = start.index(entity)
        entityDict = {}
        for entData in entity:

            for tag in easyAccessEntity:
                if entData == tag:
                    entityDict[tag] = start[entityIndex][tag]

            if entData == "links":
                for link in start[entityIndex]['links']:
                    linkIndex = start[entityIndex]['links'].index(link)
                    linkRel = start[entityIndex]['links'][linkIndex]['rel']
                    linkhref = start[entityIndex]['links'][linkIndex]['href']
                    if linkRel == "self":
                        entityDict['selfLink'] = linkhref
                    elif linkRel == "alternate":
                        entityDict['alternateLink'] = linkhref

            elif entData == "events":
                for event in start[entityIndex]['events']:
                    eventIndex = start[entityIndex]['events'].index(event)
                    eventAction = start[entityIndex]['events'][eventIndex]['eventAction']
                    eventDate = start[entityIndex]['events'][eventIndex]['eventDate']
                    if eventAction == 'last changed':
                        entityDict['lastChanged'] = eventDate
                    elif eventAction == 'registration':
                        entityDict['registered'] = eventDate

            elif entData == "vcardArray":
                for array in start[entityIndex]['vcardArray']:
                    for contactData in array:
                        if isinstance(contactData, list):
                            if contactData[0] == 'fn':
                                entityDict['fullName'] = contactData[3]
                            elif contactData[0] == 'kind':
                                entityDict['kind'] = contactData[3]
                            elif contactData[0] == 'adr':
                                try:
                                    entityDict['address'] = contactData[1]['label']
                                except:
                                    pass
                            elif contactData[0] == 'tel':
                                entityDict['phone'] = contactData[3]
                            elif contactData[0] == 'email':
                                entityDict['email'] = contactData[3]

        saveTo.append(entityDict)


def parseJSON(ip):

    ipData = getRDAP(ip)

    ipDataFormatted = {}

    for data in ipData:

        if data == 'events':
            for event in ipData['events']:
                eventIndex = ipData['events'].index(event)
                eventAction = ipData['events'][eventIndex]['eventAction']
                eventDate = ipData['events'][eventIndex]['eventDate']
                if eventAction == 'last changed':
                    ipDataFormatted['lastChanged'] = eventDate
                elif eventAction == 'registration':
                    ipDataFormatted['registered'] = eventDate

        elif data == 'cidr0_cidrs':
            ipDataFormatted['CIDRs'] = []
            for cidr in ipData['cidr0_cidrs']:
                cidrData =  str(cidr['v4prefix']) + '/' + str(cidr['length'])
                ipDataFormatted['CIDRs'].append(cidrData)

        elif data == 'links':
            for link in ipData['links']:
                linkIndex = ipData['links'].index(link)
                linkRel = ipData['links'][linkIndex]['rel']
                linkhref = ipData['links'][linkIndex]['href']
                if linkRel == "self":
                    ipDataFormatted['selfLink'] = linkhref
                elif linkRel == "alternate":
                    ipDataFormatted['alternateLink'] = linkhref

        elif data == 'remarks':
            for dict in ipData['remarks']:
                for text in dict:
                    if text == "description":
                        ipDataFormatted['description'] = []
                        for descrip in ipData['remarks'][0]['description']:
                            ipDataFormatted['description'].append(descrip)

        elif data == 'entities':
            ipDataFormatted['entities'] = []
            pullEntityData(ipData['entities'], ipDataFormatted['entities'])
            for entity in ipData['entities']:
                entityIndex = ipData['entities'].index(entity)
                for entData in entity:
                    if entData == 'entities':
                        ipDataFormatted['entities'][entityIndex]['entities'] = []
                        pullEntityData(ipData['entities'][entityIndex]['entities'], ipDataFormatted['entities'][entityIndex]['entities'])
                        for entity2 in ipData['entities'][entityIndex]['entities']:
                            entityIndex2 = ipData['entities'][entityIndex]['entities'].index(entity2)
                            for entData2 in entity2:
                                if entData2 == 'entities':
                                    ipDataFormatted['entities'][entityIndex]['entities'][entityIndex2]['entities'] = []
                                    pullEntityData(ipData['entities'][entityIndex]['entities'][entityIndex2]['entities'], ipDataFormatted['entities'][entityIndex]['entities'][entityIndex2]['entities'])

        for tag in easyAccess:
            if data == tag:
                ipDataFormatted[tag] = ipData[data]


    return(ipDataFormatted)

def processInput(ip, num):
    try:
        response = parseJSON(ip)
    except:
        response = 'no'

    return({ip : response})

def getRDAPtxt(ipArray):

    ipArrays = []

    for i in range(0, len(ipArray), 100):
         array = ipArray[i:i + 100]
         ipArrays.append(array)

    a = 0
    num_cores = multiprocessing.cpu_count()
    for array in ipArrays:

        results = Parallel(n_jobs=num_cores)(delayed(processInput)(i, array.index(i)) for i in array)

        if not os.path.exists(directory + '/RDAPfiles'):
            os.makedirs(directory + '/RDAPfiles')

        filename = directory + '/RDAPfiles/rdap' + str(a) + '.txt'
        with open(filename, 'w') as file:
            file.write(json.dumps(results))

        a = a + 1
