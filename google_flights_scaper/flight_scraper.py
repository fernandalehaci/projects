from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import os
import psycopg2

# Create variables for scraping 
url = 'https://www.google.com/travel/flights/search?tfs=CBwQAhoqEgoyMDI1LTA2LTExKAFqDAgCEggvbS8wM2wybnIMCAMSCC9tLzBwMmdxGioSCjIwMjUtMDYtMTcoAWoMCAMSCC9tLzBwMmdxcgwIAhIIL20vMDNsMm5AAUgBcAGCAQsI____________AZgBAQ&hl=en&gl=us&curr=USD'
flightSelectors = {
    'duration' : "div.hF6lYb.sSHqwe.ogfYpf.tPgKwe span.qeoz6e.HKHSfd + span",
    'price' : "div.BVAVmf.tPgKwe",
    'airline' : "div.hF6lYb.sSHqwe.ogfYpf.tPgKwe span.h1fkLb",
    'stops' : "span.VG3hNb",
    'departing_airport' : "div.G2WY5c.sSHqwe.ogfYpf.tPgKwe",
    'departing_time' : 'div[aria-label^="Departure time"]',
    'arrival_airport' : 'div.c8rWCd.sSHqwe.ogfYpf.tPgKwe',
    'arrival_time': 'div[aria-label^="Arrival time"]',
}
# Create variables for storing scraped flight data downstream:  
query_placeholder = ['%s'] * (len(flightSelectors)+1)
query = f"""
        INSERT INTO google_flights_scraper (flight_result, {', '.join(flightSelectors.keys())} )
        VALUES ({', '.join(query_placeholder)}) 
    """
flight_result = 0

# Database connection. Future iteration plan to move this to a separate module 
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True
    print(f"Successfully connected to {db_name}!")
    cur = conn.cursor()
except Exception as e:
    print(f"Error connecting to the database: {e}")

# Scrape URL: 
with sync_playwright() as p:
    browser = p.chromium.launch(headless= True)
    page = browser.new_page()
    # stealth_sync(page) -- results actually worstened 

    page.goto(url)
    page.wait_for_selector("li.pIav2d")  # Wait for flight results 
    page.wait_for_timeout(10000)  # Wait for additional seconds to ensure all prices load
    print("Done waiting")

    flights = page.locator("div[jsname='YdtKid'] ul.Rk10dc li.pIav2d").all()
    print("Located selector")

    for flight in flights:
        # Initiate dict per each flight result: 
        flight_result += 1 
        flightDetails = {"flight_result": flight_result}

        # Append scraped flight details to dict per flight result: 
        for key, selector in flightSelectors.items():
            flightDetails[key] = flight.locator(selector).text_content() 
        print(flightDetails)

        # Insert row into DB per flight result: 
        cur.execute(query, tuple(flightDetails.values()))
        print("Flight ", flight_result, " successfully stored to DB")
    browser.close()
cur.close()
conn.close()