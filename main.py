import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import lxml
import json

# All books information will be stored in a list all_books
all_books = []


# This function will return our downloaded page as an soup object
def get_page(url):
    # Download the page using requests
    downloaded_page = requests.get(page_url)
    # Check for status code if the link exists (we only have 50 pages, we will get 404 error at page 51)
    status = downloaded_page.status_code
    # Create soup object
    soup = bs(downloaded_page.text, "lxml")
    return [soup, status]


# This function will return all the link of the books from the entire page
def get_page_links(soup):
    # Get all books links
    books_links = []
    listings = soup.find_all(class_='product_pod')
    for listing in listings:
        book_link = listing.find('h3').a.get('href')
        # Define base url to have a complete link of the book
        base_url = 'https://books.toscrape.com/catalogue/'
        full_link = base_url + book_link
        # Append the links to our book_links list
        books_links.append(full_link)
    return books_links


# This function will extract all product information for a book
def extract_product_info(books_links):
    # Extract product information from each book link
    for link in books_links:
        # Download the book link
        result = requests.get(link).text
        # Create soup object for the link
        book_soup = bs(result, 'lxml')
        # Get book title
        book_title = book_soup.find(class_='col-sm-6 product_main').h1.text.strip()
        # Get book price
        book_price = book_soup.find(class_='col-sm-6 product_main').p.text.strip()

        # GET INFORMATION FROM PRODUCT INFORMATION TABLE
        # Create soup object
        product_info_table = book_soup.find(class_='table table-striped').find_all('tr')
        # Get UPC code formatted
        upc = product_info_table[0].text.strip()
        # Get product type formatted
        product_type = product_info_table[1].text.strip().replace('Product Type', '')
        # Get price excluding vat formatted
        price_excl_vat = product_info_table[2].text.strip().replace('Price (excl. tax)Â', '')
        # Get price included vat formatted
        price_incl_vat = product_info_table[3].text.strip().replace('Price (incl. tax)Â', '')
        # Get tax amount formatted
        tax = product_info_table[4].text.strip().replace('TaxÂ', '')
        # How many books are available, returns the number as integer
        availability = int(
            product_info_table[5].text.strip().replace(' available)', '').replace('Availability\nIn stock (', ''))
        # Returns the number of reviews as integer
        number_of_reviews = int(product_info_table[6].text.strip().replace('Number of reviews', ''))

        # Store the information of each book
        book = {'title': book_title,
                'price': book_price.replace('Â', ''),
                'UPC': upc,
                'product type': product_type,
                'price_excl_vat': price_excl_vat,
                'price_incl_vat': price_incl_vat,
                'tax': tax,
                'stock': availability,
                'number_of_reviews': number_of_reviews
                }

        # Append the book information to the list of books we created
        all_books.append(book)


# Pagination
page_number = 49
while True:
    page_url = f'https://books.toscrape.com/catalogue/page-{page_number}.html'
    soup_status = get_page(url=page_url)
    # If page has been loaded successfully:
    if soup_status[1] == 200:
        print(f"Scrapping page {page_number}")
        extract_product_info(get_page_links(soup_status[0]))
        # Go to next page
        page_number += 1
    # Else, we have reached the end of the pages
    else:
        print('No more page to be scrapped')
        break
    print(f"{len(all_books)} books scrapped")

# Save data as Data Frame
data_f = pd.DataFrame(all_books)
# Save data as CSV
data_f.to_csv('books_scrapped.csv', encoding='utf-8')
