# Import necessary libraries and modules
from playwright.sync_api import sync_playwright
import time
import csv
from dataclasses import dataclass

# Define a data class to store notary information
@dataclass
class NotaryData:
    name: str
    address: str
    phone_one: str
    phone_two: str
    email: str
    website: str

# Function to clean text by removing unwanted characters
def clean_text(text):
    cleaned_text = ''.join(text).strip().replace('\n', '').replace('[', '').replace(']', '')
    cleaned_text = cleaned_text if cleaned_text else "non"
    return cleaned_text

# Function to click the "Next page" link
def click_next_page(page):
    next_page_link = page.query_selector('li.pager__item.pager__item--arrow--right')
    if next_page_link:
        next_page_link.click()
        page.wait_for_load_state('networkidle')
        return True
    else:
        return False

# Function to extract notary data from a page
def extract_notary_data(page, notary_data_list):
    # Find all elements with the class 'label' on the page
    job_elements = page.query_selector_all('span.label')
    for job_element in job_elements:
        # Simulate a Ctrl+Click to open the details in a new tab
        page.keyboard.down('Control')
        job_element.click()
        page.keyboard.up('Control')
        time.sleep(3)

        # Switch to the newly opened tab
        new_page = page.context.pages[-1]

        # Find all elements with the class 'notary-office-info-wrapper' on the new tab
        data_elements = new_page.locator("div.notary-office-info-wrapper").all()
        for data_element in data_elements:
            # Extract and clean the notary data
            name_nota = clean_text(data_element.locator('div.title').inner_text())
            nota_address = clean_text(data_element.locator('div.info-with-icon.address').inner_text())
            nota_phone_one = clean_text(data_element.locator('div.info-with-icon.phone').all_text_contents())
            nota_phone_two = clean_text(data_element.locator('div.info-with-icon.fax').all_text_contents())
            nota_email = clean_text(data_element.locator('div.info-with-icon.link-redirect.mail').all_text_contents())
            nota_website = clean_text(data_element.locator('a.info-with-icon.link-redirect.link-site').all_text_contents())
            
            # Create a NotaryData instance and append it to the list
            notary_instance = NotaryData(name=name_nota, address=nota_address, phone_one=nota_phone_one, phone_two=nota_phone_two, email=nota_email, website=nota_website)
            notary_data_list.append(notary_instance)

# Function to save notary data to a CSV file
def save_to_csv(notary_data_list, filename='notary_dataone.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'address', 'phone_one', 'phone_two', 'email', 'website']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for notary_data in notary_data_list:
            writer.writerow(notary_data.__dict__)

# Main execution block
if __name__ == '__main__':
    # Initialize the list to store notary data
    notary_data_list = []
    
    # URL to process
    urls_to_process = [
        "# Add URL"
       
    ]
    
    # Launch the Playwright browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Iterate through each URL
        for url in urls_to_process:
            # Create a new page for the current URL
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            
            # Iterate through 10 pages (adjust as needed)
            for page_number in range(1, 11):
                print(f"Processing page {page_number}")
                extract_notary_data(page, notary_data_list)
                
                # Check if there is a "Next page" link and click it
                if not click_next_page(page):
                    break  # Break the loop if there is no "Next page" link

            # Close the page after processing
            page.close()

        # Close the browser after processing all URLs
        browser.close()

    # Save the notary data to CSV
    save_to_csv(notary_data_list)
    print("Notary data saved to CSV.")