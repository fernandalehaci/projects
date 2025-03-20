# g-flight-scraper
Script to scrape flight details for a specific google flights URL which is defined in the script. 


## Current Limitations + future enhancement opportunities: 
1. The script is susceptible to breaking if the URL page code were to change where the flightSelectors need to be updated. Should look into a more flexible way to script, but it is likely we can't avoid this fully. 
2. Would like to modularize some of the steps that will likely be reused in other scripts in this repository such as connecting to the DB. 
3. Depending on future usage, could create functions and create arguments such as URL to run script instead. 