import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load postcodes from CSV
postcodes = pd.read_csv('postcodes.csv')

# Limit the scraper to the second 10,000 rows
postcodes = postcodes.iloc[10000:20000]

# Function to sanitize suburb and state names for URLs
def sanitize_input(suburb, state):
    suburb = suburb.lower().replace(' ', '-')
    state = state.lower()
    return suburb, state

# Function to scrape data from a valid URL
def scrape_data(postcode, suburb, state):
    suburb, state = sanitize_input(suburb, state)
    url = f"https://www.yellowpages.com.au/find/restaurants/{suburb}-{state}-{postcode}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to scrape {url}: HTTP {response.status_code}")
        return [], url  # Return an empty list and the failed URL

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract data
    data = []
    for entry in soup.find_all('div', class_='search-result'):
        name = entry.find('a', class_='listing-name')
        address = entry.find('p', class_='listing-address')
        phone = entry.find('p', class_='contact-phone')
        data.append({
            'Name': name.text.strip() if name else None,
            'Address': address.text.strip() if address else None,
            'Phone': phone.text.strip() if phone else None,
            'Postcode': postcode,
            'Suburb': suburb,
            'State': state
        })
    return data, None  # Return the data and no failed URL

# Fixed batch size for a single run
BATCH_SIZE = 10000  # Adjust as needed
output_file = 'restaurants.csv'  # Output file name

# Initialize storage for failed URLs
failed_urls = []

# Process the batch
batch_data = []

print(f"Processing a fixed batch from row 10,000 to 20,000 {BATCH_SIZE}...")

for _, row in postcodes.iterrows():
    print(f"Scraping data for {row['Suburb']} ({row['Postcode']})...")
    try:
        data, failed_url = scrape_data(row['Postcode'], row['Suburb'], row['State'])
        batch_data.extend(data)
        if failed_url:
            failed_urls.append({
                'Suburb': row['Suburb'],
                'Postcode': row['Postcode'],
                'State': row['State'],
                'URL': failed_url
            })
    except Exception as e:
        print(f"Error scraping data for {row['Suburb']} ({row['Postcode']}): {e}")
        failed_urls.append({
            'Suburb': row['Suburb'],
            'Postcode': row['Postcode'],
            'State': row['State'],
            'URL': f"https://www.yellowpages.com.au/find/restaurants/{row['Suburb']}-{row['State']}-{row['Postcode']}"
        })

# Save the data to the CSV file
pd.DataFrame(batch_data).to_csv(output_file, index=False)
print(f"Batch completed. Data saved to {output_file}")

# Save failed URLs to a separate file
if failed_urls:
    failed_urls_file = 'failed_urls.csv'
    pd.DataFrame(failed_urls).to_csv(failed_urls_file, index=False)
    print(f"Failed URLs saved to {failed_urls_file}")

print("Scraping completed.")
