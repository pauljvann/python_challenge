# Python Challenge RDAP and GEO IP Query Application

In order to setup this application, clone or download this project to your computer or system.  Then proceed to edit the config.py file to make the directory a file you would like created to save the data to.

The following dependencies are also required: Requests,
json,
joblib,
multiprocessing,
pickle,
os,
threading,
re,
Math,
Datetime,
dateutil.parser


There are three ways to run this application (the first two will prompt for IP text):

1) uploadNew.py

This program essentially allows you to submit a text file with IP addresses, pulls the GEO IP data in less than 10 seconds, pulls the RDAP data in approximately 10 minutes, then allows you to query the data.  This is suitable in some cases because it pulls all of the data at once which makes querying later much easier.

2) uploadNewQuery.py

https://youtu.be/7s-aC2dPfuk

This program, similar to the one above, allows you to submit a text file with IP addresses, pulls the GEO IP data in less than 10 seconds, starts a thread to pull the RDAP data, and instantly allows you to query the data.  One drawback to this is that you are querying data that isn't done being requested yet, and the RDAP data takes much longer to fully gather because it is done using multiprocessing.  This program is suitable in some cases though when instant queries are necessary.

3) existingData.py

This program essentially allows you to run queries on previously gathered RDAP data, such as if you ran uploadNew, waited a day, and ran existingData.  This is suitable for when all of your data has been gathered and you would simply like to query it.
