# gmail_extract
Exports few main email fields from the GMail account for the analysis purposes. My intention was to clean up the mailbox.
Steps to make it work:
1. First you need to Turn on the Gmail API, as it is described by [this link](https://developers.google.com/gmail/api/quickstart/python). Just push the **Enable Gmail API** button and place `credentials.json` into the working directory.
2. Then run `python gexport.py`
It will ask your approval to connect the app to the GMail
