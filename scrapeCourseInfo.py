from bs4 import BeautifulSoup
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import os

# Define the range of possible inputs
inputs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
          'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def scrape(input):
    # Create an empty list to store the scraped data for this input
    input_scraped_data = []

    page_num = 0
    while True:
        # Print a debugging message
        print(f"Scraping input '{input}', page {page_num}")

        # Construct the URL for the autocomplete request
        url = f"https://mytimetable.mcmaster.ca/add_suggest.jsp?term=3202340&cams=MCMSTiCON_MCMSTiMHK_MCMSTiSNPOL_MCMSTiMCMST_MCMSTiOFF&course_add={input}&page_num={page_num}&sco=0&sio=1&already=&_=1690952585649"

        # Send the request and parse the response
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        # Check if there are any results on this page
        results = soup.find_all('rs')
        if not results:
            break

        # Extract the data from the response
        for result in results:
            info = result['info']
            text = result.text

            # Skip results that include the text '_more_'
            if '_more_' in text:
                continue

            # Only use results with reason="CODE"
            if result['reason'] == "CODE":
                # Replace spaces in text with hyphens
                text = text.replace(' ', '-')

                # Add the extracted data to the list of scraped data for this input
                input_scraped_data.append({'Info': info, 'Text': text})

        # Increment the page number and continue to the next page
        page_num += 1

    # Write the scraped data for this input to a separate file
    with open(f'scraped_{input}.json', 'w') as f:
        json.dump(input_scraped_data, f, indent=4)


# Use a ThreadPoolExecutor to scrape multiple inputs concurrently
with ThreadPoolExecutor() as executor:
    executor.map(scrape, inputs)


# Merge all the scraped data into a single list
scraped_data = []
for input in inputs:
    with open(f'scraped_{input}.json') as f:
        input_scraped_data = json.load(f)
        scraped_data.extend(input_scraped_data)
    # Delete the individual scraped file
    os.remove(f'scraped_{input}.json')

# Write all the scraped data to a single file
with open('scraped.json', 'w') as f:
    json.dump(scraped_data, f, indent=4)


print("\nRemoving duplicates now...")
# Load the scraped data from the JSON file
with open('scraped.json', 'r') as f:
    scraped_data = json.load(f)

# Create a new list to store the unique entries
unique_data = []

# Iterate over the scraped data
for entry in scraped_data:
    # Check if the entry is already in the list of unique entries
    if entry not in unique_data:
        # If not, add it to the list of unique entries
        unique_data.append(entry)

# Save the unique data back to the JSON file
with open('scraped.json', 'w') as f:
    # Replace <br/> tags with spaces
    for entry in unique_data:
        entry['Info'] = entry['Info'].replace('<br/>', ' ')
    json.dump(unique_data, f, indent=4)
