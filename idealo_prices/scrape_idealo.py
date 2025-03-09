from bs4 import BeautifulSoup
from idealo_scraper import extract_perfume_data, process_perfume_search

# Assuming your HTML is in a variable called html_content
''''''

results = extract_perfume_data(html_content, search_query="40 Knots", max_results=3)