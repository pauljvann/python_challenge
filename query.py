import json
import os
from math import radians, cos, sin, asin, sqrt
import datetime
import dateutil.parser
import re
from config import directory


def haversine(lon1, lat1, lon2, lat2):

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956
    return c * r



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

def getQuery(query):

    queryComp = []

    query = query.replace("get ip where: ", "")
    query = query.replace(" ", "")

    result = [x.strip() for x in query.split('AND')]

    for res in result:
        type = ''
        tag = ''

        if res[0:3] == '(g)':
            type = 'geo'
        elif res[0:3] == '(r)':
            type='rdap'

        if res[0:3] == '(g)' or res[0:3] == '(r)':

            updatedString =  res[3:len(res)]
            stringArray = updatedString.split('=')
            tag = stringArray[0]
            value = stringArray[1]

            queryComp.append({'type' : type, 'tag' : tag, 'value' : value})

        elif res[0:3] == '(d)':

            type = 'distance'
            updatedString = res[3:len(res)]
            updatedString = updatedString.replace('[', '')
            updatedString= updatedString.replace(']', '')
            #updatedString = updatedString.replace(' ', '')
            valueArray = updatedString.split(':')
            latInput  = valueArray[0]
            longInput = valueArray[1]
            mile = valueArray[2]

            queryComp.append({'type' : type, 'lat' : latInput, 'long' : longInput, 'mile' : mile})

        elif res[0:3] == '(t)':

            type='time'
            updatedString = res[3:len(res)]
            updatedString = updatedString.replace('[', '')
            updatedString= updatedString.replace(']', '')
            valueArray = updatedString.split('/')

            timeRelation = valueArray[0]
            dateTime = valueArray[1]

            queryComp.append({'type' : type, 'timeRel' : timeRelation, 'dateTime' : dateTime})


    results = []
    for query in queryComp:
        queryIndex = queryComp.index(query)
        willUpdate = 0
        if query['type'] == 'geo':
            resultsUpdated = []
            for ip in geoIPData:
                try:
                    queryValue = query['value'].replace("'","")
                    if (geoIPData[ip][query['tag']].replace(" ","")) == queryValue:
                        if queryIndex == 0:
                            results.append(ip)
                        else:
                            willUpdate = 1
                            if ip in results:
                                resultsUpdated.append(ip)
                    else:
                        if queryIndex != 0:
                            if ip in results:
                                results.remove(ip)

                except:
                    pass

            if willUpdate == 1:
                results = resultsUpdated

        elif query['type'] == 'rdap':
            resultsUpdated = []
            for ip in rdapData:
                try:
                    queryValue = query['value'].replace("'","")
                    if (rdapData[ip][query['tag']].replace(" ","")) == queryValue:
                        if queryIndex == 0:
                            results.append(ip)
                        else:
                            willUpdate = 1
                            if ip in results:
                                resultsUpdated.append(ip)

                    else:
                        if queryIndex != 0:
                            if ip in results:
                                results.remove(ip)

                except:
                    pass
            if willUpdate == 1:
                results = resultsUpdated

        elif query['type'] == 'distance':
            resultsUpdated = []
            for ip in geoIPData:
                try:

                    distance = haversine(float(query['long']), float(query['lat']), float(geoIPData[ip]['long']), float(geoIPData[ip]['lat']))

                    if distance <= int(query['mile']):
                        if queryIndex == 0:
                            results.append(ip)
                        else:
                            willUpdate = 1
                            if ip in results:
                                resultsUpdated.append(ip)

                    else:
                        if queryIndex != 0:
                            if ip in results:
                                results.remove(ip)
                except:
                    pass

            if willUpdate == 1:
                results = resultsUpdated

        elif query['type'] == 'time':

            resultsUpdated = []

            timeRelation = query['timeRel']
            queryRoughDate = query['dateTime']
            queryDate = datetime.datetime.strptime(queryRoughDate, '%Y-%m-%dT%H:%M:%SZ')

            #registeredDate = ''
            #changedDate = ''

            for ip in rdapData:

                try:

                    oldRegisteredDate = rdapData[ip]['registered'][0:19]
                    oldRegisteredDate = oldRegisteredDate + 'Z'
                    registeredDate = datetime.datetime.strptime(oldRegisteredDate, '%Y-%m-%dT%H:%M:%SZ')

                    oldChangedDate = rdapData[ip]['lastChanged'][0:19]
                    oldChangedDate = oldChangedDate + 'Z'
                    changedDate = datetime.datetime.strptime(oldChangedDate, '%Y-%m-%dT%H:%M:%SZ')
                    #changedDate = pytz.utc.localize(changedNaive)

                    if timeRelation.lower() == 'rb':

                        duration = queryDate - registeredDate
                        durationSec = duration.total_seconds()

                        if durationSec < 0:

                            if queryIndex == 0:
                                results.append(ip)
                            else:
                                willUpdate = 1
                                if ip in results:
                                    resultsUpdated.append(ip)

                        else:
                            if queryIndex != 0:
                                if ip in results:
                                    results.remove(ip)


                    elif timeRelation.lower() == 'cb':

                        duration = queryDate - registeredDate
                        durationSec = duration.total_seconds()

                        if durationSec < 0:

                            if queryIndex == 0:
                                results.append(ip)
                            else:
                                willUpdate = 1
                                if ip in results:
                                    resultsUpdated.append(ip)

                        else:
                            if queryIndex != 0:
                                if ip in results:
                                    results.remove(ip)

                    elif timeRelation.lower() == 'ra':

                        duration = queryDate - registeredDate
                        durationSec = duration.total_seconds()

                        if durationSec < 0:

                            if queryIndex == 0:
                                results.append(ip)
                            else:
                                willUpdate = 1
                                if ip in results:
                                    resultsUpdated.append(ip)

                        else:
                            if queryIndex != 0:
                                if ip in results:
                                    results.remove(ip)


                    elif timeRelation.lower() == 'ca':

                        duration = queryDate - registeredDate
                        durationSec = duration.total_seconds()

                        if durationSec < 0:

                            if queryIndex == 0:
                                results.append(ip)
                            else:
                                willUpdate = 1
                                if ip in results:
                                    resultsUpdated.append(ip)

                        else:
                            if queryIndex != 0:
                                if ip in results:
                                    results.remove(ip)


                except:
                    pass

        if willUpdate == 1:
            results = resultsUpdated


    return(results)

def queryValidator(query):

    geoTags = ['country', 'countryCode', 'lat', 'long', 'AS', 'ISP', 'org', 'region', 'regionName', 'status', 'timezone', 'status']
    rdapTags = ['handle', 'startAddress', 'endAddress', 'ipVersion', 'name', 'description', 'lastChanged', 'selfLink', 'alternateLink', 'entities', 'CIDRs']

    queryComp = []
    if 'get ip where' in query:

        query = query.replace("get ip where: ", "")
        query = query.replace(" ", "")

        result = [x.strip() for x in query.split('AND')]

        for res in result:
            type = ''
            updatedString =  res[3:len(res)]
            stringArray = updatedString.split('=')
            tag = stringArray[0]

            if res[0:3] == '(g)':
                type = 'geo'
                if tag in geoTags:
                    pass
                else:
                    return('Sorry: ' + tag + ' is not a valid piece of rdap IP data, consult our query docs to see valid tags')
            elif res[0:3] == '(r)':
                type='rdap'
                if tag in rdapTags:
                    pass
                else:
                    return('Sorry: ' + tag + ' is not a valid piece of rdap IP data, consult our query docs to see valid tags')

            elif res[0:3] == '(t)':
                pass

            elif res[0:3] == '(d)':
                pass

            else:
                return('Sorry, we do not understand what format data you would like to query.  We were expecting either (g) for geolocation IP or (r) for RDAP.  If you need help consult our query docs!')

            response = getQuery(query)
            return(response)
    else:
        return('Sorry, this query does not meet documentation standards.  See QueryDocs.txt on how to write a proper query!')


def queryData(query):
    queryComp = []

    query = query.replace('GET', '')
    query = query.replace(' ', '')

    result = [x.strip() for x in query.split('AND')]
    where= result[len(result) - 1].split('WHERE')
    whereTo = where[1]
    whereTo = whereTo.replace('[', '')
    whereTo = whereTo.replace(']', '')
    whereTo = whereTo.replace('ip=', '')
    ipResArray = [x.strip() for x in whereTo.split(',')]
    result.remove(result[len(result) - 1])
    result.append(where[0])

    for res in result:
        type = ''
        tag = ''
        if res[0:3] == '(g)':
            type = 'geo'
        elif res[0:3] == '(r)':
            type='rdap'

        tag =  res[3:len(res)]
        queryComp.append({type : tag})

    queryResults = []

    for ip in ipResArray:
        results = {'ip' : ip}
        for q in queryComp:
            for type in q:
                if type == 'geo':
                    try:
                        data = geoIPData[ip][q[type]]
                    except:
                        data = 'data does not exist in Database'

                elif type == 'rdap':
                    try:
                        data = rdapData[ip][q[type]]
                    except:
                        data = 'data does not exist in Database'


                results[q[type]] = data

        queryResults.append(results)

    return(queryResults)




def queryDataValidator(query):

    geoTags = ['country', 'countryCode', 'lat', 'long', 'AS', 'ISP', 'org', 'region', 'regionName', 'status', 'timezone', 'status']
    rdapTags = ['handle', 'startAddress', 'endAddress', 'ipVersion', 'name', 'description', 'lastChanged', 'selfLink', 'alternateLink', 'entities', 'CIDRs']

    if "GET" in query:
        query = query.replace('GET', '')
        query = query.replace(' ', '')

        result = [x.strip() for x in query.split('AND')]
        where= result[len(result) - 1].split('WHERE')
        whereTo = where[1]
        whereTo = whereTo.replace('[', '')
        whereTo = whereTo.replace(']', '')
        whereTo = whereTo.replace('ip=', '')
        ipResArray = [x.strip() for x in whereTo.split(',')]
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', whereTo)

        if len(ips) != len(ipResArray):
            return('Sorry, one or more of your query IP addresses is not a legitimate IP address. Go back and make sure you used the correct IP!')

        result.remove(result[len(result) - 1])
        result.append(where[0])

        for res in result:
            type = ''
            tag = res[3:len(res)]

            if res[0:3] == '(g)':
                type = 'geo'
                if tag in geoTags:
                    pass
                else:
                    return('Sorry: ' + tag + ' is not a valid piece of geo IP data, consult our query docs to see valid tags')
            elif res[0:3] == '(r)':
                type='rdap'

                if tag in rdapTags:
                    pass
                else:
                    return('Sorry: ' + tag + ' is not a valid piece of rdap IP data, consult our query docs to see valid tags')

            else:
                return('Sorry, we do not understand what format data you would like to query.  We were expecting either (g) for geolocation IP or (r) for RDAP.  If you need help consult our query docs!')

            response = queryData(query)
            return(response)

    else:
        return('Sorry, this query does not meet documentation standards.  See QueryDocs.txt on how to write a proper query!')
