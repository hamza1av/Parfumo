import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from random import randint
import random
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse

class PerfumePriceScraper:
    def __init__(self, checkpoint_dir="checkpoints", checkpoint_interval=10, max_results=5):
        """
        Initialize the perfume price scraper.
        
        Args:
            checkpoint_dir (str): Directory to store checkpoint files
            checkpoint_interval (int): Save progress after this many perfumes
        """
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_interval = checkpoint_interval
        self.sleep_timer = 3
        self.verbose_output = False
        
        # Create checkpoint directory if it doesn't exist
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
            
        # Load processing history if it exists
        self.history_file = os.path.join(checkpoint_dir, "processing_history.json")
        self.processing_history = self._load_history()

        self.max_results = max_results
        
        # User agent rotation list
        self.headers_list = [
            # Firefox on macOS
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://duckduckgo.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Priority": "u=0, i",
                "TE": "trailers",
            }
            # },
            # # Chrome on Windows 10
            # {
            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.7",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.google.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Priority": "u=1, i",
            # },
            # # Edge on Windows 11
            # {
            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.bing.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "cross-site",
            #     "Priority": "u=0, i",
            # },
            # # Mobile Safari on iOS
            # {
            #     "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.google.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Priority": "u=1, i",
            # },
            # # Mobile Chrome on Android
            # {
            #     "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.170 Mobile Safari/537.36",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.duckduckgo.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Priority": "u=1, i",
            # },
            # # Opera on Windows
            # {
            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/96.0.4664.45",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.google.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Priority": "u=1, i",
            # },
            # # Safari on macOS
            # {
            #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.170 Safari/537.36",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Referer": "https://www.google.com/",
            #     "Connection": "keep-alive",
            #     "Upgrade-Insecure-Requests": "1",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Priority": "u=1, i",
            # },
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
    
    def _get_random_headers(self):
        """Return a randomly selected header from the list"""
        return random.choice(self.headers_list)

    def clean_perfume_name(self, perfume_name: str, brand: str = None) -> str:
        if brand:
            # Remove brand name if it appears at the beginning
            pattern = re.compile(rf"^{re.escape(brand)}\s*", re.IGNORECASE)
            perfume_name = pattern.sub("", perfume_name)

        # Remove years (4-digit numbers)
        perfume_name = re.sub(r"\b\d{4}\b", "", perfume_name).strip()

        return perfume_name

    def search_perfume(self, perfume_name, brand=None):

        # cleaned_name = self.clean_perfume_name(perfume_name, brand)
        # query = f'{brand} {cleaned_name}' if brand else cleaned_name
        query = f'{brand} {perfume_name}' 
        base_url = 'https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q='
        formatted_query = urllib.parse.quote_plus(query)
        url = base_url + formatted_query

        response = requests.get(url, headers=self._get_random_headers())

        return response, query 

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
            
        # Search for the perfume
        response, query = self.search_perfume(perfume_name, brand) 

        if response.status_code == 200:
            result = self.process_perfume_search(response.text, brand, perfume_name, max_results=self.max_results)
            if len(result) ==0:
                print(f"\033[38;5;214mFailed to scrape nr. {perfume_id} {query}\033[0m")
            else:
                print(f"\033[32mSuccesfully scraped nr. {perfume_id} {query}\033[0m")  # Green text
                self.mark_as_processed(perfume_id=perfume_id, data=result)

        else:
            print(f"\033[31mFAILED TO PROCESS nr. {perfume_id} {query}\033[0m")  # Red text
            result = []

        return result 
    
    def process_perfume_dataset(self, df, name_col='name', brand_col='brand', id_col=None):
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
                time.sleep(random.randint(2,5))
            
            # Store results
            result_df.at[i, 'sizes_and_prices'] = data
            
            # Save checkpoint at regular intervals
            if (i + 1) % self.checkpoint_interval == 0:
                print(f"Saving checkpoint after processing {i+1} perfumes")
                self._save_history()
                
                # Save intermediate results to CSV
                checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint.csv")
                result_df.to_csv(checkpoint_file, index=False)
            
            # Add delay between perfumes
            time.sleep(self.sleep_timer)
        
        # Save final history
        self._save_history()
        
        # expanded_df = pd.DataFrame(data)
        
        return result_df

    def extract_perfume_data(self, html_content, brand=None, perfume_name=None, max_results=5):
        """
        Extract perfume data from HTML content, including price and bottle size.
        
        Parameters:
        - html_content (str): The HTML content containing perfume search results
        - brand (str, optional): Brand name that must be contained in the item title
        - perfume_name (str, optional): Perfume name that must be contained in the item title
        - max_results (int, optional): Maximum number of results to return, defaults to 5
        
        Returns:
        - list: List of dictionaries containing extracted perfume data
        """
        print(f"Received HTML content of length: {len(html_content)}")
        print(f"Searching for brand: {brand}, perfume_name: {perfume_name}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all result items - using a more general approach
        result_items = soup.find_all('div', {'data-testid': 'resultItem'})
        print(f"Found {len(result_items)} result items")
        
        perfumes = []
        count = 0
        
        for item in result_items:
            print(f"\nProcessing item {count + 1}")
            
            # Extract product title - using a more flexible approach
            title_element = item.select_one('[data-testid="productSummary__title"]')
            if not title_element:
                print("No title element found, skipping")
                continue
                
            title = title_element.text.strip()
            print(f"Found title: {title}")
            
            # # Check if both brand and perfume name are in the title (case insensitive)
            # title_lower = title.lower()
            # brand_match = True if brand is None else brand.lower() in title_lower
            # perfume_match = True if perfume_name is None else perfume_name.lower() in title_lower
            
            # if not (brand_match and perfume_match):
            #     print(f"Brand or perfume name not in title, skipping")
            #     continue
            
            # Extract description for bottle size
            desc_element = item.select_one('p.sr-productSummary__mainDetailsExpander_BZ5P5')
            if not desc_element:
                desc_element = item.select_one('.sr-productSummary__description_Okjc5 span')
            
            description = desc_element.text.strip() if desc_element else ""
            print(f"Description: {description}")
            
            # Extract bottle size using regex or from title
            bottle_size = None
            # First try to find size in description

            # Extract bottle size using regex or from title
            bottle_size = None

            # First try to find size in description
            size_match = None  # Ensure it's always defined
            size_match = re.search(r'Inhalt in ml\s*(\d+(?:\.\d+)?)\s*ml', description)

            if size_match:
                bottle_size = size_match.group(1) + " ml"
            else:
                # Try to extract from title if it's in parentheses
                size_match_title = re.search(r'\((\d+(?:\.\d+)?)ml\)', title)
                if size_match_title:
                    bottle_size = size_match_title.group(1) + " ml"
                        
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

    def extract_perfume_data_alternative(self, html_content, brand=None, perfume_name=None, max_results=5):
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
            
            # Check if both brand and perfume name are in the title (case insensitive)
            title_lower = title.lower()
            brand_match = True if brand is None else brand.lower() in title_lower
            perfume_match = True if perfume_name is None else perfume_name.lower() in title_lower
            
            if not (brand_match and perfume_match):
                continue
            
            # Extract description
            description = ""
            desc_element = link.select_one('.sr-productSummary__mainDetailsExpander_BZ5P5')
            if desc_element:
                description = desc_element.text.strip()
            
            # Extract bottle size using regex or from title
            bottle_size = None
            # First try to find size in description
            size_match = re.search(r'Inhalt in ml\s*(\d+(?:\.\d+)?)\s*ml', description)
            if size_match:
                bottle_size = size_match.group(1) + " ml"
            else:
                # Try to extract from title if it's in parentheses
                size_match_title = re.search(r'\((\d+(?:\.\d+)?)ml\)', title)
                if size_match_title:
                    bottle_size = size_match_title.group(1) + " ml"
            
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

    def process_perfume_search(self, html_content, brand=None, perfume_name=None, max_results=5, debug=False):
        """
        Process perfume search results and print them in a readable format.
        
        Parameters:
        - html_content (str): The HTML content containing perfume search results
        - brand (str, optional): Brand name that must be contained in the item title
        - perfume_name (str, optional): Perfume name that must be contained in the item title
        - max_results (int, optional): Maximum number of results to return, defaults to 5
        - debug (bool, optional): Whether to print debug information, defaults to False
        
        Returns:
        - list: List of dictionaries containing extracted perfume data
        """
        # Make sure at least brand or perfume_name is provided
        if not brand and not perfume_name:
            print("Warning: Neither brand nor perfume_name provided. Will return all results up to max_results.")
        
        # Turn off print statements if debug is False
        if not debug:
            import contextlib
            import io
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                perfumes = self.extract_perfume_data(html_content, brand, perfume_name, max_results)
                
                if not perfumes:
                    perfumes = self.extract_perfume_data_alternative(html_content, brand, perfume_name, max_results)
        else:
            # Debug mode - show all print statements
            perfumes = self.extract_perfume_data(html_content, brand, perfume_name, max_results)
            
            if not perfumes:
                perfumes = self.extract_perfume_data_alternative(html_content, brand, perfume_name, max_results)
        
        # Always print the final results
        if not perfumes:
            print("No matching perfumes found.")
            return []
        
        print(f"Found {len(perfumes)} matching perfumes:")
        if self.verbose_output == True:
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