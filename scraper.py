import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load postcodes from CSV
postcodes = pd.read_csv('postcodes.csv')

def scrape_data(postcode, suburb, state):
    url = f"https://www.yellowpages.com.au/find/restaurants/{suburb.lower().replace(' ', '-')}-{state.lower()}-{postcode}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to scrape {url}: {response.status_code}")
        return []

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
    return data

# Loop through postcodes and scrape
all_data = []
for _, row in postcodes.iterrows():
    print(f"Scraping data for {row['Suburb']} ({row['Postcode']})...")
    all_data.extend(scrape_data(row['Postcode'], row['Suburb'], row['State']))

# Save results to CSV
output_file = 'restaurants.csv'
pd.DataFrame(all_data).to_csv(output_file, index=False)
print(f"Scraping completed. Data saved to {output_file}")
