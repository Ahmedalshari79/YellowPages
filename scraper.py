import requests
from bs4 import BeautifulSoup
import pandas as pd

# Load postcodes from CSV
postcodes = pd.read_csv('postcodes.csv')

# Function to scrape data
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

# Batch processing parameters
BATCH_SIZE = 50  # Number of rows to process in each batch
output_file = 'restaurants.csv'  # Output file name

# Initialize storage for failed URLs
failed_urls = []

# Loop through postcodes in batches
for i in range(0, len(postcodes), BATCH_SIZE):
    batch = postcodes.iloc[i:i + BATCH_SIZE]
    batch_data = []

    print(f"Processing batch {i // BATCH_SIZE + 1} ({i} to {i + len(batch) - 1})...")

    for _, row in batch.iterrows():
        print(f"Scraping data for {row['Suburb']} ({row['Postcode']})...")
        try:
            batch_data.extend(scrape_data(row['Postcode'], row['Suburb'], row['State']))
        except Exception as e:
            print(f"Error scraping data for {row['Suburb']} ({row['Postcode']}): {e}")
            failed_urls.append({
                'Suburb': row['Suburb'],
                'Postcode': row['Postcode'],
                'State': row['State']
            })

    # Save batch data to the CSV file
    pd.DataFrame(batch_data).to_csv(output_file, mode='a', header=not pd.io.common.file_exists(output_file), index=False)
    print(f"Batch {i // BATCH_SIZE + 1} completed and saved.")

# Save failed URLs to a separate file
if failed_urls:
    failed_urls_file = 'failed_urls.csv'
    pd.DataFrame(failed_urls).to_csv(failed_urls_file, index=False)
    print(f"Failed URLs saved to {failed_urls_file}")

print("Scraping completed.")
