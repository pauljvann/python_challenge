import json
import os
from config import directory
from query import queryValidator, queryDataValidator

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
