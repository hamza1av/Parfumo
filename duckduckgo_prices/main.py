# Install the necessary package
# pip install duckduckgo-search requests beautifulsoup4

from duckduckgo_search import DDGS
import pandas as pd
import re
import time
from random import randint
from bs4 import BeautifulSoup
import requests

# Initialize the DuckDuckGo search
ddgs = DDGS()

def search_perfume_prices(perfume_name, brand=None, size=None, max_results=5):
    """
    Search for perfume prices using DuckDuckGo.
    
    Args:
        perfume_name (str): Name of the perfume
        brand (str, optional): Brand name
        size (str, optional): Bottle size (e.g., "50ml", "100ml")
        max_results (int, optional): Maximum number of results to return
        
    Returns:
        list: A list of dictionaries containing price information
    """
    # Construct the search query
    query = f"{brand + ' ' if brand else ''}{perfume_name} perfume"
    if size:
        query += f" {size}"
    query += " price"
    
    results = []
    try:
        # Get search results from DuckDuckGo
        search_results = ddgs.text(query, max_results=max_results*3)  # Request more to filter later
        
        # Process results
        for result in search_results:
            # Skip irrelevant sites like Pinterest, Instagram, etc.
            if any(site in result['href'].lower() for site in ['pinterest', 'instagram', 'twitter', 'facebook']):
                continue
                
            # Extract info
            results.append({
                'perfume': perfume_name,
                'brand': brand,
                'size': size,
                'title': result['title'],
                'description': result['body'],
                'source': result['href']
            })
            
            if len(results) >= max_results:
                break
                
        return results
    except Exception as e:
        print(f"Error searching for {perfume_name}: {str(e)}")
        return []
    

def extract_prices_from_description(description):
    """Extract potential prices from text using regex"""
    # Look for price patterns like $50, $50.99, 50€, etc.
    price_patterns = [
        r'\$\s*(\d+(?:\.\d{1,2})?)',  # $50, $50.99
        r'(\d+(?:\.\d{1,2})?)\s*\$',  # 50$, 50.99$
        r'€\s*(\d+(?:,\d{1,2})?)',    # €50, €50,99
        r'(\d+(?:,\d{1,2})?)\s*€',    # 50€, 50,99€
        r'£\s*(\d+(?:\.\d{1,2})?)',   # £50, £50.99
        r'(\d+(?:\.\d{1,2})?)\s*£'    # 50£, 50.99£
    ]
    
    found_prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, description)
        for match in matches:
            # Replace comma with dot for standardization
            price = match.replace(',', '.')
            try:
                found_prices.append(float(price))
            except ValueError:
                continue
    
    return found_prices

def scrape_price_from_website(url, timeout=10):
    """Attempt to scrape prices directly from the website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common price selectors
            possible_selectors = [
                '.price', '#price', '[itemprop="price"]', '.product-price',
                '.current-price', '.sale-price', '.offer-price', '.regular-price'
            ]
            
            for selector in possible_selectors:
                elements = soup.select(selector)
                if elements:
                    prices = []
                    for element in elements:
                        # Get the text and clean it
                        price_text = element.get_text().strip()
                        # Extract numbers using regex
                        extracted = extract_prices_from_description(price_text)
                        if extracted:
                            prices.extend(extracted)
                    if prices:
                        return prices
            
            # If no prices found via selectors, try to find in the entire page
            page_text = soup.get_text()
            return extract_prices_from_description(page_text)
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
    
    return []

def get_perfume_prices(perfume_df, standardize_sizes=True):
    """
    Process a dataframe of perfumes and get price information.
    
    Args:
        perfume_df (pandas.DataFrame): DataFrame with perfume information
        standardize_sizes (bool): Whether to standardize sizes to ml
        
    Returns:
        pandas.DataFrame: Original dataframe with added price information
    """
    # Create columns for results
    perfume_df['price_results'] = None
    perfume_df['min_price'] = None
    perfume_df['max_price'] = None
    perfume_df['avg_price'] = None
    perfume_df['price_per_ml'] = None
    
    # Function to standardize size to ml
    def standardize_size_to_ml(size_str):
        if not size_str or not isinstance(size_str, str):
            return None
        
        # Convert to lowercase and remove spaces
        size_str = size_str.lower().strip()
        
        # Extract the numeric part and unit
        match = re.match(r'(\d+(?:\.\d+)?)\s*(ml|oz|fl\.?\s*oz)', size_str)
        if not match:
            return None
            
        amount, unit = match.groups()
        amount = float(amount)
        
        # Convert to ml
        if 'oz' in unit:
            # 1 fl oz ≈ 29.57 ml
            return amount * 29.57
        return amount
    
    for idx, row in perfume_df.iterrows():
        perfume_name = row.get('perfume_name', '')
        brand = row.get('brand', '')
        size = row.get('size', '')
        
        # Standardize size if requested
        size_ml = None
        if standardize_sizes and size:
            size_ml = standardize_size_to_ml(size)
            
        # Search for prices
        print(f"Searching for {brand} {perfume_name} {size}")
        search_results = search_perfume_prices(perfume_name, brand, size)
        
        all_prices = []
        
        # Process each search result
        for result in search_results:
            # Try to extract prices from description
            description_prices = extract_prices_from_description(result['description'])
            if description_prices:
                all_prices.extend(description_prices)
            
            # Try to scrape the website directly
            website_prices = scrape_price_from_website(result['source'])
            if website_prices:
                all_prices.extend(website_prices)
                
            # Add delay to avoid overwhelming servers
            time.sleep(randint(1, 3))
        
        # Remove outliers (prices that are too high or too low)
        if all_prices:
            # Remove prices that are more than 3 std deviations from the mean
            mean_price = sum(all_prices) / len(all_prices)
            std_dev = (sum((x - mean_price) ** 2 for x in all_prices) / len(all_prices)) ** 0.5
            
            filtered_prices = [p for p in all_prices if abs(p - mean_price) <= 3 * std_dev]
            
            if filtered_prices:
                perfume_df.at[idx, 'price_results'] = filtered_prices
                perfume_df.at[idx, 'min_price'] = min(filtered_prices)
                perfume_df.at[idx, 'max_price'] = max(filtered_prices)
                perfume_df.at[idx, 'avg_price'] = sum(filtered_prices) / len(filtered_prices)
                
                # Calculate price per ml if size was standardized
                if size_ml and size_ml > 0:
                    perfume_df.at[idx, 'price_per_ml'] = perfume_df.at[idx, 'avg_price'] / size_ml
        
        # Add delay between perfumes
        time.sleep(randint(2, 5))
    
    return perfume_df

# Sample dataset
data = {
    'perfume_name': ['Light Blue', 'Sauvage', 'Black Opium', 'Coco Mademoiselle'],
    'brand': ['Dolce & Gabbana', 'Dior', 'Yves Saint Laurent', 'Chanel'],
    'size': ['100ml', '3.4 oz', '50ml', '1.7 fl oz']
}

perfume_df = pd.DataFrame(data)

# Get prices
result_df = get_perfume_prices(perfume_df)

# Display results
print(result_df[['perfume_name', 'brand', 'size', 'avg_price', 'price_per_ml']])

# Export to CSV
result_df.to_csv('perfume_prices.csv', index=False)