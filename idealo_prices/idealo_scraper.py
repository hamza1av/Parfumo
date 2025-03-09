import re
from bs4 import BeautifulSoup

def extract_perfume_data(html_content, search_query=None, max_results=5):
    """
    Extract perfume data from HTML content, including price and bottle size.
    
    Parameters:
    - html_content (str): The HTML content containing perfume search results
    - search_query (str, optional): Query string that must be contained in the item title
    - max_results (int, optional): Maximum number of results to return, defaults to 5
    
    Returns:
    - list: List of dictionaries containing extracted perfume data
    """
    # Add debug print to check if HTML is being received properly
    print(f"Received HTML content of length: {len(html_content)}")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all result items - using a more general approach
    result_items = soup.find_all('div', {'data-testid': 'resultItem'})
    print(f"Found {len(result_items)} result items")
    
    perfumes = []
    count = 0
    
    for item in result_items:
        # Debug the current item
        print(f"\nProcessing item {count + 1}")
        
        # Extract product title - using a more flexible approach
        title_element = item.select_one('[data-testid="productSummary__title"]')
        if not title_element:
            print("No title element found, skipping")
            continue
            
        title = title_element.text.strip()
        print(f"Found title: {title}")
        
        # If search query is provided, check if it's in the title
        if search_query and search_query.lower() not in title.lower():
            print(f"Search query '{search_query}' not in title, skipping")
            continue
        
        # Extract description for bottle size
        desc_element = item.select_one('p.sr-productSummary__mainDetailsExpander_BZ5P5')
        if not desc_element:
            desc_element = item.select_one('.sr-productSummary__description_Okjc5 span')
        
        description = desc_element.text.strip() if desc_element else ""
        print(f"Description: {description}")
        
        # Extract bottle size using regex
        bottle_size = None
        size_match = re.search(r'Inhalt in ml\s*(\d+(?:\.\d+)?)\s*ml', description)
        if size_match:
            bottle_size = size_match.group(1) + " ml"
        print(f"Bottle size: {bottle_size}")
        
        # Extract price
        price_element = item.select_one('[data-testid="detailedPriceInfo__price"]')
        price = None
        if price_element:
            price_text = price_element.text.strip()
            price_match = re.search(r'(\d+(?:\.\d+)?(?:,\d+)?)\s*€', price_text)
            if price_match:
                price = price_match.group(1) + " €"
        print(f"Price: {price}")
        
        # Extract base price per liter (if available)
        base_price_element = item.select_one('[data-testid="detailedPriceInfo__basePrice"]')
        base_price = None
        if base_price_element:
            base_price_text = base_price_element.text.strip()
            base_price_match = re.search(r'\((\d+(?:\.\d+)?(?:,\d+)?)\s*€/Liter\)', base_price_text)
            if base_price_match:
                base_price = base_price_match.group(1) + " €/Liter"
        
        # Get image URL
        img_element = item.select_one('img')
        image_url = img_element.get('src') if img_element else None
        
        # Get product URL
        link_element = item.select_one('a[href]')
        product_url = link_element.get('href') if link_element else None
        
        # Extract number of offers
        offers_element = item.select_one('.sr-detailedPriceInfo__offerCount_PJByo')
        offers_count = offers_element.text.strip() if offers_element else None
        
        # Create a structured data dictionary
        perfume_data = {
            'title': title,
            'bottle_size': bottle_size,
            'price': price,
            'base_price': base_price,
            'offers_count': offers_count,
            'image_url': image_url,
            'product_url': product_url,
            'description': description
        }
        
        perfumes.append(perfume_data)
        print(f"Added perfume data: {title}")
        
        count += 1
        if count >= max_results:
            break
    
    print(f"Total perfumes found: {len(perfumes)}")
    return perfumes

def debug_html_structure(html_content):
    """
    Helper function to debug the HTML structure
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check what data-testid attributes exist in the document
    testids = soup.select('[data-testid]')
    print(f"Found {len(testids)} elements with data-testid attribute")
    testid_values = set()
    for element in testids:
        testid_values.add(element.get('data-testid'))
    print(f"Unique data-testid values: {testid_values}")
    
    # Check for product tiles specifically
    product_tiles = soup.select('[data-testid="product-tile"]')
    print(f"Found {len(product_tiles)} product tiles")
    
    # Check for result items
    result_items = soup.select('[data-testid="resultItem"]')
    print(f"Found {len(result_items)} result items")
    
    # Check what classes exist for product listing items
    return testid_values

def extract_perfume_data_alternative(html_content, search_query=None, max_results=5):
    """
    Alternative extraction method using direct HTML parsing
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    perfumes = []
    count = 0
    
    # Find all result item links
    result_items = soup.select('div[data-testid="resultItemLink"]')
    print(f"Found {len(result_items)} result items with alternative method")
    
    for item in result_items:
        if count >= max_results:
            break
            
        link = item.select_one('a')
        if not link:
            continue
            
        # Extract product title
        title_element = link.select_one('[data-testid="productSummary__title"]')
        if not title_element:
            continue
            
        title = title_element.text.strip()
        
        # If search query is provided, check if it's in the title
        if search_query and search_query.lower() not in title.lower():
            continue
        
        # Extract description
        description = ""
        desc_element = link.select_one('.sr-productSummary__mainDetailsExpander_BZ5P5')
        if desc_element:
            description = desc_element.text.strip()
        
        # Extract bottle size using regex
        bottle_size = None
        size_match = re.search(r'Inhalt in ml\s*(\d+(?:\.\d+)?)\s*ml', description)
        if size_match:
            bottle_size = size_match.group(1) + " ml"
        elif "(100ml)" in title:
            bottle_size = "100 ml"
        elif "(50ml)" in title:
            bottle_size = "50 ml"
        
        # Extract price
        price_element = link.select_one('[data-testid="detailedPriceInfo__price"]')
        price = None
        if price_element:
            price_text = price_element.text.strip()
            price_match = re.search(r'(\d+(?:\.\d+)?(?:,\d+)?)\s*€', price_text)
            if price_match:
                price = price_match.group(1) + " €"
        
        # Create a structured data dictionary
        perfume_data = {
            'title': title,
            'bottle_size': bottle_size,
            'price': price,
            'url': link.get('href'),
        }
        
        perfumes.append(perfume_data)
        count += 1
    
    return perfumes

def process_perfume_search(html_content, search_query=None, max_results=5):
    """
    Process perfume search results and print them in a readable format.
    """
    # Debug HTML structure first
    print("Debugging HTML structure:")
    debug_html_structure(html_content)
    
    # Try both extraction methods
    print("\nTrying primary extraction method:")
    perfumes = extract_perfume_data(html_content, search_query, max_results)
    
    if not perfumes:
        print("\nPrimary method returned no results. Trying alternative method:")
        perfumes = extract_perfume_data_alternative(html_content, search_query, max_results)
    
    if not perfumes:
        print("No matching perfumes found with either method.")
        return []
    
    print(f"\nFinal results: Found {len(perfumes)} matching perfumes:")
    for i, perfume in enumerate(perfumes, 1):
        print(f"\n--- Perfume #{i} ---")
        print(f"Title: {perfume['title']}")
        print(f"Size: {perfume['bottle_size'] or 'Not specified'}")
        print(f"Price: {perfume['price'] or 'Not available'}")
        if 'base_price' in perfume and perfume['base_price']:
            print(f"Base Price: {perfume['base_price']}")
        if 'offers_count' in perfume and perfume['offers_count']:
            print(f"Offers: {perfume['offers_count']}")
    
    return perfumes