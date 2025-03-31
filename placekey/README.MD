# placekey_gsheet 
The main script takes the addresses input into a [google sheet](https://docs.google.com/spreadsheets/d/10_WYNU6WQ0s0KGgxvEbgcQ-RIb8ggfU4rxK51XKfoNI/edit?gid=0#gid=0) , and writes the associated Placekey and Placekey Confidence in columns E and F. Note that address, zipcode, and state are required fields to request a placekey (while city is optional).  
See more details on the concept of"Placekeying" and the API here: https://docs.placekey.io/documentation  
Script can currently only be run using a specific gserviceaccount (credentials.json files was added to .gitignore), however this can be used as a reference by others.  
See helpful Google Sheets API documentation here: [Google Sheets API Guide ](https://developers.google.com/workspace/sheets/api/guides/values)
