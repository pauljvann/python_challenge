import requests
import json
from config import directory

def getGeo(ipDict): #submits batch API request to below identified URL to pull GEO data
    data = json.dumps(ipDict)
    geoResponse = requests.post(url = 'http://ip-api.com/batch', data = data) #only 100 ip addresses allowed per batch
    geoData = geoResponse.json()
    return(geoData)

def jsonGEO(array):

    queries = []
    ipQuery = []
    responses = []
    geoDict = {}

    for index in range(1, 5001): #this for loop splits IP addresses into separate arrays with only 100 ip addresses in each to conform to batch API standards
        ipQuery.append({"query": array[index - 1]})
        if index % 100 == 0:
            queries.append(ipQuery)
            ipQuery = []

    for query in queries: #appends all responses to main response array
        response = getGeo(query)
        responses.append(response)

    for response in responses: 
        for ipReport in response:
            if ipReport['status'] == 'success':
                key = ipReport['query']
                
                #formats each piece of geolocation data into a neat dictionary to save to a text file and load using JSON later
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
            #responds if geo ip api failed
            
            elif ipReport['status'] == 'fail':

                key = ipReport['query']
                geoDict[key] = {
                'status' : ipReport['status'],
                'reason' : ipReport['message']
                }

    filename = directory  + '/geo.txt'
    with open(filename, 'w') as file:
         file.write(json.dumps(geoDict)) #writes geo ip file to text file to later be used by the query program

    return(filename)
