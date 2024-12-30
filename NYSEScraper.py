from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd

def scrape_nyse_data(response):
    """
    Function Overview: Scrape the current NYSE listings for either stocks, ETFs, indices, or REITs.
    """
    # List of valid responses
    valid_responses = ['Stocks', 'ETFs', 'Indices', 'REITs']

    # Check if the response is valid
    if response not in valid_responses:
        print("Invalid response. Please enter one of the following options: Stocks, ETFs, Indices, or REITs")
        raise ValueError(f"Invalid response: {response}")
    
    # Base URL for the NYSE listings
    base_url = 'https://www.nyse.com/listings_directory/stock'

    # Open the browser
    driver = webdriver.Chrome() # Change this to whichever browser you prefer
    driver.get(base_url)

    # Lists to store the tickers and instrument names
    tickers = []
    instrument_names = []

    try:
        # Ensure that the table with the listings data is loaded
        table_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-data.w-full.table-border-rows'))
        )
        print("Table found!")

        # Select the instrument type from the dropdown menu on the webpage
        choices = driver.find_element(By.ID, 'instrumentType')
        select = Select(choices)
        select.select_by_visible_text(response)
        time.sleep(0.7)

        # Loop through the pages and scrape the listed instruments until the 'Next' button is nolonger clickable
        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.select_one('table.table-data.w-full.table-border-rows')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        ticker = cells[0].text.strip()
                        instrument_name = cells[1].text.strip()
                        tickers.append(ticker)
                        instrument_names.append(instrument_name)

            # Check if the 'Next' button is clickable and click it to move to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'li[class*="px-2"] a[rel="next"]')
                if next_button.get_attribute("href"):
                    next_button.click()
                    time.sleep(0.7)
                else:
                    print("'Next' button exists but is not clickable. Exiting loop.")
                    break
            except Exception:
                print("No 'Next' button found on this page. Exiting loop.")
                break
    finally:
        # Close the browser
        driver.quit()

    # Save and return the scraped data as a DataFrame
    df = pd.DataFrame({'Tickers': tickers, response: instrument_names})
    return df

def main():
    """
    Main function to run the NYSE scraper.
    """
    # Prompt user for one of the following options: Stocks, ETFs, Indices, or REITs
    response = input("Enter one of the following options (enter exactly as listed): Stocks, ETFs, Indices, or REITs: ")

    try:
        # Scrape NYSE data for the specified instument type
        nyse_data = scrape_nyse_data(response)

        # Save the data to a CSV file
        file_name = f'NYSE-{response}.csv'
        nyse_data.to_csv(file_name, index=False)
        print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()