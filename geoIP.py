import requests
import json
from config import directory

def getGeo(ipDict):
    data = json.dumps(ipDict)
    geoResponse = requests.post(url = 'http://ip-api.com/batch', data = data)
    geoData = geoResponse.json()
    return(geoData)

def jsonGEO(array):

    queries = []
    ipQuery = []
    responses = []
    geoDict = {}

    for index in range(1, 5001):
        ipQuery.append({"query": array[index - 1]})
        if index % 100 == 0:
            queries.append(ipQuery)
            ipQuery = []

    for query in queries:
        response = getGeo(query)
        responses.append(response)

    for response in responses:
        for ipReport in response:
            if ipReport['status'] == 'success':
                key = ipReport['query']

                geoDict[key] = {
                'AS' : ipReport['as'],
                'city' : ipReport['city'],
                'country' : ipReport['country'],
                'countryCode' : ipReport['countryCode'],
                'ISP' : ipReport['isp'],
                'lat' : ipReport['lat'],
                'long' : ipReport['lon'],
                'org' : ipReport['org'],
                'region' : ipReport['region'],
                'regionName' : ipReport['regionName'],
                'status' : ipReport['status'],
                'timezone' : ipReport['timezone'],
                'zip' : ipReport['zip']

                }

            elif ipReport['status'] == 'fail':

                key = ipReport['query']
                geoDict[key] = {
                'status' : ipReport['status'],
                'reason' : ipReport['message']
                }

    filename = directory  + '/geo.txt'
    with open(filename, 'w') as file:
         file.write(json.dumps(geoDict))

    return(filename)
