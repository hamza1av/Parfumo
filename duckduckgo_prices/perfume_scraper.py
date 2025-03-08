# Install required packages
# pip install duckduckgo-search requests beautifulsoup4 pandas

from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from random import randint
import os
import json
from datetime import datetime

class PerfumePriceScraper:
    def __init__(self, checkpoint_dir="checkpoints", checkpoint_interval=10):
        """
        Initialize the perfume price scraper.
        
        Args:
            checkpoint_dir (str): Directory to store checkpoint files
            checkpoint_interval (int): Save progress after this many perfumes
        """
        self.ddgs = DDGS()
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_interval = checkpoint_interval
        
        # Create checkpoint directory if it doesn't exist
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
            
        # Load processing history if it exists
        self.history_file = os.path.join(checkpoint_dir, "processing_history.json")
        self.processing_history = self._load_history()
        
        # User agent rotation list
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
    def _load_history(self):
        """Load processing history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {str(e)}")
                return {}
        return {}
    
    def _save_history(self):
        """Save processing history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.processing_history, f)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
    
    def _get_random_user_agent(self):
        """Get a random user agent from the list"""
        return self.user_agents[randint(0, len(self.user_agents) - 1)]
    
    def search_perfume(self, perfume_name, brand=None, max_results=10):
        """
        Search for perfume information using DuckDuckGo.
        
        Args:
            perfume_name (str): Name of the perfume
            brand (str, optional): Brand name
            max_results (int, optional): Maximum number of results to return
            
        Returns:
            list: A list of search results
        """
        # Construct the search query
        query = f"{brand + ' ' if brand else ''}{perfume_name} perfume"
        
        results = []
        try:
            # Get search results from DuckDuckGo
            search_results = self.ddgs.text(query, max_results=max_results*2)
            
            # Process results
            for result in search_results:
                # Skip irrelevant sites
                if any(site in result['href'].lower() for site in ['pinterest', 'instagram', 'twitter', 'facebook', 'youtube']):
                    continue
                    
                # Skip sites that likely won't have useful information
                if any(ext in result['href'].lower() for ext in ['.pdf', '.doc', '.jpg', '.png']):
                    continue
                
                # Extract info
                results.append({
                    'title': result['title'],
                    'description': result['body'],
                    'url': result['href']
                })
                
                if len(results) >= max_results:
                    break
                    
            return results
        except Exception as e:
            print(f"Error searching for {perfume_name}: {str(e)}")
            return []

    def extract_sizes_from_text(self, text):
        """
        Extract potential perfume sizes from text.
        
        Args:
            text (str): Text to search for sizes
            
        Returns:
            list: List of standardized sizes in ml
        """
        # Regular expressions for common size formats
        size_patterns = [
            r'(\d+(?:\.\d+)?)\s*ml\b',  # 50ml, 100 ml
            r'(\d+(?:\.\d+)?)\s*(?:fl\.?\s*oz|oz)\b',  # 1.7 fl oz, 3.4oz
            r'(\d+(?:\.\d+)?)\s*milliliter\b',  # 50 milliliter
            r'(\d+(?:\.\d+)?)\s*ounce\b',  # 1 ounce
        ]
        
        found_sizes_ml = []
        for pattern in size_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    size_value = float(match)
                    # Convert to ml if needed
                    if 'oz' in pattern or 'ounce' in pattern:
                        size_value *= 29.57  # 1 fl oz ≈ 29.57 ml
                    found_sizes_ml.append(round(size_value, 2))
                except ValueError:
                    continue
        
        # Remove duplicates and sort
        return sorted(list(set(found_sizes_ml)))

    def extract_prices_from_text(self, text):
        """
        Extract potential prices from text.
        
        Args:
            text (str): Text to search for prices
            
        Returns:
            list: List of found prices
        """
        # Look for price patterns
        price_patterns = [
            r'\$\s*(\d+(?:\.\d{1,2})?)',  # $50, $50.99
            r'(\d+(?:\.\d{1,2})?)\s*\$',  # 50$, 50.99$
            r'€\s*(\d+(?:,\d{1,2})?)',    # €50, €50,99
            r'(\d+(?:,\d{1,2})?)\s*€',    # 50€, 50,99€
            r'£\s*(\d+(?:\.\d{1,2})?)',   # £50, £50.99
            r'(\d+(?:\.\d{1,2})?)\s*£',   # 50£, 50.99£
            r'(\d+(?:\.\d{1,2})?)\s*USD',  # 50 USD
            r'(\d+(?:\.\d{1,2})?)\s*EUR',  # 50 EUR
            r'(\d+(?:\.\d{1,2})?)\s*GBP'   # 50 GBP
        ]
        
        found_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Replace comma with dot for standardization
                price = match.replace(',', '.')
                try:
                    found_prices.append(float(price))
                except ValueError:
                    continue
        
        return found_prices

    def scrape_website(self, url, timeout=15):
        """
        Scrape website for perfume information.
        
        Args:
            url (str): Website URL to scrape
            timeout (int): Request timeout in seconds
            
        Returns:
            dict: Dictionary with extracted sizes and prices
        """
        try:
            headers = {'User-Agent': self._get_random_user_agent()}
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                return {'sizes_ml': [], 'prices': []}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all text from the page
            page_text = soup.get_text()
            
            # Find sizes
            sizes_ml = self.extract_sizes_from_text(page_text)
            
            # Find prices
            prices = self.extract_prices_from_text(page_text)
            
            # Look for size-price pairs in structured elements
            size_price_pairs = []
            
            # Common product option containers
            option_selectors = [
                '.product-options', '.variant-options', '.size-options',
                '.product-variants', '[data-product-variants]', '.swatch-options',
                '.product-form__options', '[data-option-name]'
            ]
            
            for selector in option_selectors:
                option_elements = soup.select(selector)
                for element in option_elements:
                    element_text = element.get_text()
                    element_sizes = self.extract_sizes_from_text(element_text)
                    element_prices = self.extract_prices_from_text(element_text)
                    
                    if element_sizes and element_prices:
                        size_price_pairs.append({
                            'sizes': element_sizes,
                            'prices': element_prices
                        })
            
            return {
                'sizes_ml': sizes_ml,
                'prices': prices,
                'size_price_pairs': size_price_pairs
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {'sizes_ml': [], 'prices': [], 'size_price_pairs': []}
    
    def map_sizes_to_prices(self, scrape_results):
        """
        Try to map sizes to corresponding prices.
        
        Args:
            scrape_results (list): List of scrape results from different websites
            
        Returns:
            dict: Dictionary mapping sizes to prices
        """
        # Aggregate all found sizes
        all_sizes = set()
        for result in scrape_results:
            all_sizes.update(result.get('sizes_ml', []))
        
        size_price_map = {size: [] for size in all_sizes}
        
        # First try to use direct size-price pairs
        for result in scrape_results:
            for pair in result.get('size_price_pairs', []):
                sizes = pair.get('sizes', [])
                prices = pair.get('prices', [])
                
                # If we have equal number of sizes and prices, assume direct mapping
                if len(sizes) == len(prices):
                    for i, size in enumerate(sizes):
                        if size in size_price_map:
                            size_price_map[size].append(prices[i])
        
        # For sizes without direct mapping, try to infer
        for size in size_price_map:
            if not size_price_map[size]:
                # Look for typical price relationships
                # e.g., if 100ml is $X, 50ml is often ~$X*0.6
                related_sizes = {
                    50: 100,   # 50ml is related to 100ml
                    30: 50,    # 30ml is related to 50ml
                    100: 200,  # 100ml is related to 200ml
                }
                
                if size in related_sizes and related_sizes[size] in size_price_map:
                    related_size = related_sizes[size]
                    related_prices = size_price_map[related_size]
                    
                    if related_prices:
                        # Estimate price based on size ratio and typical market patterns
                        size_ratio = size / related_size
                        
                        # Smaller sizes have higher price per ml
                        if size_ratio < 1:
                            price_ratio = 0.6 + (0.4 * size_ratio)  # Nonlinear relationship
                        else:
                            price_ratio = 0.9 + (0.1 * size_ratio)  # Larger sizes have slight discount
                            
                        for related_price in related_prices:
                            estimated_price = related_price * price_ratio
                            size_price_map[size].append(round(estimated_price, 2))
        
        return size_price_map
    
    def filter_outliers(self, prices):
        """
        Filter out price outliers.
        
        Args:
            prices (list): List of prices
            
        Returns:
            list: Filtered list of prices
        """
        if not prices or len(prices) < 3:
            return prices
            
        # Calculate mean and standard deviation
        mean_price = sum(prices) / len(prices)
        std_dev = (sum((x - mean_price) ** 2 for x in prices) / len(prices)) ** 0.5
        
        # Filter out prices that are more than 2 standard deviations from the mean
        return [p for p in prices if abs(p - mean_price) <= 2 * std_dev]
    
    def is_already_processed(self, perfume_id):
        """Check if a perfume has already been processed"""
        return str(perfume_id) in self.processing_history
    
    def mark_as_processed(self, perfume_id, data):
        """Mark a perfume as processed with timestamp and results"""
        self.processing_history[str(perfume_id)] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
    
    def get_perfume_sizes_and_prices(self, perfume_name, brand=None, perfume_id=None):
        """
        Get available sizes and prices for a perfume.
        
        Args:
            perfume_name (str): Name of the perfume
            brand (str, optional): Brand name
            perfume_id: Unique identifier for this perfume
            
        Returns:
            dict: Dictionary with sizes and prices
        """
        # Generate an ID if not provided
        if perfume_id is None:
            perfume_id = f"{brand}_{perfume_name}".replace(" ", "_").lower()
            
        # Check if already processed
        if self.is_already_processed(perfume_id):
            print(f"Using cached results for {brand} {perfume_name}")
            return self.processing_history[str(perfume_id)]['data']
            
        print(f"Processing {brand} {perfume_name}...")
        
        # Search for the perfume
        search_results = self.search_perfume(perfume_name, brand)
        
        if not search_results:
            print(f"No search results found for {brand} {perfume_name}")
            return {'sizes_and_prices': {}}
        
        # Scrape each website
        scrape_results = []
        for i, result in enumerate(search_results):
            print(f"  Scraping website {i+1}/{len(search_results)}: {result['url']}")
            site_data = self.scrape_website(result['url'])
            if site_data['sizes_ml'] or site_data['prices']:
                scrape_results.append(site_data)
            
            # Add delay between requests
            time.sleep(randint(2, 5))
        
        # Map sizes to prices
        size_price_map = self.map_sizes_to_prices(scrape_results)
        
        # Filter outliers and calculate statistics
        result = {}
        for size, prices in size_price_map.items():
            if prices:
                filtered_prices = self.filter_outliers(prices)
                if filtered_prices:
                    result[size] = {
                        'min_price': min(filtered_prices),
                        'max_price': max(filtered_prices),
                        'avg_price': round(sum(filtered_prices) / len(filtered_prices), 2),
                        'price_count': len(filtered_prices)
                    }
        
        # Store results
        data = {'sizes_and_prices': result}
        self.mark_as_processed(perfume_id, data)
        
        return data
    
    def process_perfume_dataset(self, df, name_col='perfume_name', brand_col='brand', id_col=None):
        """
        Process an entire dataset of perfumes.
        
        Args:
            df (pandas.DataFrame): DataFrame with perfume information
            name_col (str): Column name for perfume name
            brand_col (str): Column name for brand
            id_col (str, optional): Column name for perfume ID
            
        Returns:
            pandas.DataFrame: DataFrame with added size and price information
        """
        # Create a new dataframe to store results
        result_df = df.copy()
        result_df['sizes_and_prices'] = None
        
        # Process each perfume
        for i, row in df.iterrows():
            perfume_name = row[name_col]
            brand = row[brand_col] if brand_col in df.columns else None
            perfume_id = row[id_col] if id_col in df.columns else None
            
            # Skip if already processed
            if perfume_id and self.is_already_processed(perfume_id):
                data = self.processing_history[str(perfume_id)]['data']
            else:
                # Get sizes and prices
                data = self.get_perfume_sizes_and_prices(perfume_name, brand, perfume_id)
            
            # Store results
            result_df.at[i, 'sizes_and_prices'] = data['sizes_and_prices']
            
            # Save checkpoint at regular intervals
            if (i + 1) % self.checkpoint_interval == 0:
                print(f"Saving checkpoint after processing {i+1} perfumes")
                self._save_history()
                
                # Save intermediate results to CSV
                checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{i+1}.csv")
                result_df.to_csv(checkpoint_file, index=False)
            
            # Add delay between perfumes
            time.sleep(randint(2, 4))
        
        # Save final history
        self._save_history()
        
        # Explode the sizes_and_prices into separate rows
        expanded_rows = []
        for i, row in result_df.iterrows():
            base_row = row.to_dict()
            sizes_and_prices = base_row.pop('sizes_and_prices', {})
            
            if not sizes_and_prices:
                # Keep the original row with no size/price data
                expanded_rows.append(base_row)
            else:
                # Create a new row for each size
                for size_ml, price_data in sizes_and_prices.items():
                    new_row = base_row.copy()
                    new_row['size_ml'] = size_ml
                    new_row['min_price'] = price_data.get('min_price')
                    new_row['max_price'] = price_data.get('max_price')
                    new_row['avg_price'] = price_data.get('avg_price')
                    new_row['price_count'] = price_data.get('price_count')
                    expanded_rows.append(new_row)
        
        # Create the expanded dataframe
        expanded_df = pd.DataFrame(expanded_rows)
        
        return expanded_df