import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ParfumoScraper:
    def __init__(self, cookie_file='cookies.json', header_file='headers.json', links_file='links.json'):
        self.cookie_file = cookie_file
        self.header_file = header_file
        self.links_file = links_file
        self.session = requests.Session()
        self.setup_session()

    def setup_session(self):
        """Set up requests session with custom headers"""
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
        
        try:
            with open(self.header_file, 'r') as f:
                headers = json.load(f)
        except FileNotFoundError:
            print("Using default headers.")
            headers = default_headers

        self.session.headers.update(headers)

    def get_soup(self, url):
        """Make request and return BeautifulSoup object"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_basic_info(self, soup):
        """Extract basic perfume information"""
        if not soup:
            return {}
            
        try:
            name_element = soup.select_one("h1.p_name_h1")
            brand_element = soup.select_one("span.p_brand_name span[itemprop='name']")
            year_element = soup.select_one("span.label_a")
            
            return {
                "name": name_element.text.strip() if name_element else None,
                "brand": brand_element.text.strip() if brand_element else None,
                "year": year_element.text.strip() if year_element else None
            }
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            return {}

    def get_ratings(self, soup):
        """Extract ratings information"""
        if not soup:
            return {}
            
        try:
            rating_section = soup.select_one("div.rating_summary")
            if rating_section:
                rating_spans = rating_section.select("span")
                if len(rating_spans) >= 2:
                    return {
                        "rating": rating_spans[0].text.strip(),
                        "number_of_ratings": rating_spans[1].text.strip().split(" ")[0]
                    }
            return {}
        except Exception as e:
            print(f"Error extracting ratings: {e}")
            return {}

    def extract_scent_notes(self, soup, category_class):
        """Extract scent notes for a specific category"""
        if not soup:
            return []
            
        try:
            category_block = soup.find(class_=category_class)
            if category_block:
                scent_note_elements = category_block.select('span.clickable_note_img span.nowrap.pointer')
                return [element.text.strip() for element in scent_note_elements if element.text.strip()]
            return []
        except Exception as e:
            print(f"Error extracting {category_class} notes: {e}")
            return []

    def get_scent_strength(self, soup):
        """Extract scent strength information"""
        if not soup:
            return {}
            
        try:
            scent_data = {}
            containers = soup.select(".s-circle-container")
            
            for container in containers:
                try:
                    scent_name = container.select_one(".text-xs.grey").text.strip()
                    circle = container.select_one(".s-circle")
                    if circle:
                        size_classes = [cls for cls in circle['class'] if "s-circle_" in cls]
                        if size_classes:
                            size = size_classes[0].split("_")[-1]
                            scent_data[scent_name] = size
                except Exception:
                    continue
                    
            return scent_data
        except Exception as e:
            print(f"Error extracting scent strength: {e}")
            return {}

    def get_detailed_ratings(self, soup):
        """Extract detailed ratings information"""
        if not soup:
            return {}
            
        try:
            detailed_ratings = {}
            rating_elements = soup.select(".barfiller_element")

            for element in rating_elements:
                try:
                    category = element.select_one(".text-xs.upper.grey").text.strip()
                    rating_value = element.select_one(".text-lg.bold").text.strip()
                    num_ratings_element = element.select_one(".lightgrey.text-2xs.upper")
                    num_ratings = num_ratings_element.text.strip().split()[0] if num_ratings_element else None

                    detailed_ratings[category] = {
                        "rating": rating_value,
                        "number_of_ratings": num_ratings,
                    }
                except Exception as e:
                    print(f"Error extracting ratings for category {category}: {e}")
                    continue

            return detailed_ratings
        except Exception as e:
            print(f"Error extracting detailed ratings: {e}")
            return {}

    # def get_scent_types(self, soup):
    #     """Extract scent types from diagram section"""
    #     if not soup:
    #         return {}
            
    #     try:
    #         scents = {}
    #         scent_elements = soup.select("svg tspan")
            
    #         for element in scent_elements:
    #             text = element.text.strip()
    #             if text and '%' in text:
    #                 try:
    #                     name, percentage = text.rsplit(' ', 1)
    #                     percentage = float(percentage.replace('%', ''))
    #                     scents[name] = percentage
    #                 except ValueError:
    #                     continue
                    
    #         return scents
    #     except Exception as e:
    #         print(f"Error extracting scent types: {e}")
    #         return {}

    def get_scent_types(self, soup):
        """Extract all fragrance characteristics from the pie charts"""
        if not soup:
            return {}
            
        try:
            characteristics = {
                'scent_type': {},  # Dufttyp - chart4
                'style': {},       # Stil - chart1
                'season': {},      # Jahreszeit - chart3
                'occasion': {}     # Anlass - chart2
            }
            
            # Find all script tags containing chart data
            scripts = soup.find_all('script')
            for script in scripts:
                if not script.string:
                    continue
                    
                # Process each chart's data
                for chart_id, category in [
                    ('chart4.data', 'scent_type'),
                    ('chart1.data', 'style'),
                    ('chart3.data', 'season'),
                    ('chart2.data', 'occasion')
                ]:
                    if chart_id in script.string:
                        # Extract the data array
                        data_start = script.string.find(f'{chart_id} = ') + len(f'{chart_id} = ')
                        data_end = script.string.find('];', data_start) + 1
                        data_str = script.string[data_start:data_end]
                        
                        try:
                            # Parse the JSON data
                            import json
                            chart_data = json.loads(data_str)
                            
                            # Create dictionary of characteristics and their vote counts
                            for item in chart_data:
                                name = item['ct_name']
                                votes = int(item['votes'])
                                characteristics[category][name] = votes
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON for {category}")
                            continue
                        
            return characteristics
        except Exception as e:
            print(f"Error extracting fragrance characteristics: {e}")
            return {}


    def scrape_perfume(self, url):
        """Scrape all information for a single perfume"""
        try:
            print(f"\nScraping: {url}")
            
            # Get main page
            main_soup = self.get_soup(url)
            if not main_soup:
                return None

            # Extract data from main page
            basic_info = self.get_basic_info(main_soup)
            detailed_ratings = self.get_detailed_ratings(main_soup)
            scent_strength = self.get_scent_strength(main_soup)
            top_notes = self.extract_scent_notes(main_soup, 'nb_t')
            middle_notes = self.extract_scent_notes(main_soup, 'nb_m')
            base_notes = self.extract_scent_notes(main_soup, 'nb_b')
            ratings = self.get_ratings(main_soup)

            # Get all notes if structured notes fail
            all_notes = None
            if not (top_notes or middle_notes or base_notes):
                all_notes = [el.text.strip() for el in main_soup.select('span.clickable_note_img span.nowrap.pointer') if el.text.strip()]

            # Get diagram page
            # diagram_url = urljoin(url, '/diagram')
            # diagram_soup = self.get_soup(diagram_url)
            scent_types = self.get_scent_types(main_soup) if main_soup else {}

            return {
                **basic_info,
                "detailed_ratings": detailed_ratings,
                "scent_strength": scent_strength,
                "top_notes": top_notes if top_notes else None,
                "middle_notes": middle_notes if middle_notes else None,
                "base_notes": base_notes if base_notes else None,
                "all_notes": all_notes,
                "ratings": ratings,
                "scent_types": scent_types,
                "url": url
            }

        except Exception as e:
            print(f"Error scraping perfume {url}: {e}")
            return None

    def scrape_all_perfumes(self):
        """Scrape all perfumes with chunking support"""
        results = []
        try:
            with open(self.links_file, 'r') as file:
                links = json.load(file)
            
            chunk_size = len(links) // 8
            chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
            
            while True:
                try:
                    index = int(input("Enter an index between 1 and 8: "))
                    if 1 <= index <= 8:
                        break
                    print("Index must be between 1 and 8.")
                except ValueError:
                    print("Please enter a valid integer.")
            
            selected_chunk = chunks[index - 1]
            for i, link in enumerate(selected_chunk, 1):
                print(f"\nProcessing perfume {i} of {len(selected_chunk)}")
                perfume_data = self.scrape_perfume(link)
                if perfume_data:
                    results.append(perfume_data)
                    self.save_results(results, f'perfumes_data_partial_chunk_{index}.json')
                # time.sleep(2)
                if i == 5:
                    break
                    
            return results
        except Exception as e:
            print(f"Error scraping all perfumes: {e}")
            return results

    def save_results(self, results, output_file='perfumes_data.json'):
        """Save results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    scraper = ParfumoScraper()
    try:
        test_url = "https://www.parfumo.de/Parfums/Kilian/Amber_Oud"
        results = scraper.scrape_all_perfumes()
        scraper.save_results(results, output_file='test.json')
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()