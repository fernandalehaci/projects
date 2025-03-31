from google.oauth2.service_account import Credentials
import gspread
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from placekey.api import PlacekeyAPI
import pandas as pd
import json
import os
from dotenv import load_dotenv

# LOAD ENV VARIABLES
load_dotenv()
api_key = os.getenv("PLACEKEY_API_KEY")
# STORE PLACELEY API KEY:  
pk_api = PlacekeyAPI(api_key=api_key)
# STORE SPREADSHEET TO READ/WRITE: 
spreadsheet_id = '10_WYNU6WQ0s0KGgxvEbgcQ-RIb8ggfU4rxK51XKfoNI'


def authenticate_gsheet():
    try: 
        secret_file = 'credentials.json'
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        creds = Credentials.from_service_account_file(secret_file,scopes=scopes)
        client = gspread.authorize(creds)
        service = build("sheets", "v4", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_values_as_df():
    range_name = 'sheet1!A2:D1000'
    header_range = 'sheet1!A1:D1'

    # Note that .get() returns list of list 
    vals = (
        service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
    )
    
    headers = (
        service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=header_range
        ).execute()
    )

    rows = vals.get("values", [])
    headers = headers.get("values", [])

    df = pd.DataFrame(rows)
    df.columns = headers[0] # TO DO: clean: lowercase , remove white space 
    df['iso_country_code'] = 'US'
    return df

    
def write_placekey_to_sheet(df):

    column_mappings  = {
        "street_address": "Street Address",
        "city": "City ",
        "region": "State Abbr.",
        "postal_code": "Zipcode",
        "iso_country_code": "iso_country_code",
    }
    # APPEND PLACEKEY TO DF: 
    df_with_placekeys  =  pk_api._placekey_pandas_df(df, column_mappings, fields=['address_placekey', 'address_confidence_score'])

    # WRITE PLACEKEYS INTO SHEETS: 
    placekey_range = 'sheet1!E2'
    placekey_vals = df_with_placekeys[['address_placekey', 'address_confidence_score']].to_numpy(na_value="na").tolist()

    body = {"values": placekey_vals}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=placekey_range,
            valueInputOption='RAW',
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")



if __name__ == "__main__":
    service = authenticate_gsheet()
    addresses = get_values_as_df()
    if not addresses.empty:
        write_placekey_to_sheet(addresses) 
    else: print("No addresses in sheet")
    

    






