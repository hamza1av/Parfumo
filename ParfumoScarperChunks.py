import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

class ParfumoScraper:
    def __init__(self, cookie_file='cookies.json', header_file='headers.json', links_file='diff_list.json'):
        self.cookie_file = cookie_file
        self.header_file = header_file
        self.links_file = links_file
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Set up Chrome driver with custom options and headers"""
        chrome_options = Options()
        
        # Default headers for parfumo.de
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        
        try:
            with open(self.header_file, 'r') as f:
                headers = json.load(f)
        except FileNotFoundError:
            print("Using default headers.")
            headers = default_headers

        for key, value in headers.items():
            chrome_options.add_argument(f'--header={key}:{value}')

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')  # Set larger window size
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 2)

    def wait_and_find_element(self, by, selector, timeout=2):
        """Wait for and find an element with better error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {selector}")
            return None
        except Exception as e:
            print(f"Error finding element {selector}: {e}")
            return None

    def get_basic_info(self):
        """Extract basic perfume information with improved selectors"""
        try:
            # Wait for the main content to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
            
            name_element = self.wait_and_find_element(By.CSS_SELECTOR, "h1.p_name_h1")
            brand_element = self.wait_and_find_element(By.CSS_SELECTOR, "span.p_brand_name span[itemprop='name']")
            year_element = self.wait_and_find_element(By.CSS_SELECTOR, "span.label_a")
            
            return {
                "name": name_element.text.split("\n")[0] if name_element else None,
                "brand": brand_element.text if brand_element else None,
                "year": year_element.text if year_element else None
            }
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            return {}

    def get_ratings(self):
        """Extract ratings with improved selectors"""
        try:
            # Wait for ratings section to load
            rating_section = self.wait_and_find_element(
                By.CSS_SELECTOR, 
                "div.rating_summary",
                timeout=15
            )
            
            if rating_section:
                rating_spans = rating_section.find_elements(By.CSS_SELECTOR, "span")
                if len(rating_spans) >= 2:
                    return {
                        "rating": rating_spans[0].text,
                        "number_of_ratings": rating_spans[1].text.split(" ")[0]
                    }
            
            return {}
        except Exception as e:
            print(f"Error extracting ratings: {e}")
            return {}

    def get_scent_types(self):
        """Extract scent types with improved handling"""
        try:
            # Scroll to ensure the diagram is in view
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight * 0.5);"
            )
            time.sleep(2)  # Wait for diagram to load
            
            # Wait for SVG to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
            time.sleep(1)  # Additional wait for text elements
            
            # Find all text elements in the SVG
            scent_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "svg tspan"
            )
            
            scents = {}
            for element in scent_elements:
                text = element.text
                if text and '%' in text:
                    try:
                        name, percentage = text.rsplit(' ', 1)
                        percentage = float(percentage.replace('%', ''))
                        scents[name] = percentage
                    except ValueError:
                        continue
                    
            return scents
        except Exception as e:
            print(f"Error extracting scent types: {e}")
            return {}

    def extract_scent_notes(self, category_class):
        """Extract scent notes with improved error handling"""
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, category_class)))
            category_block = self.driver.find_element(By.CLASS_NAME, category_class)
            scent_note_elements = category_block.find_elements(
                By.CSS_SELECTOR, 'span.clickable_note_img span.nowrap.pointer'
            )
            return [element.text for element in scent_note_elements if element.text.strip()]
        except TimeoutException:
            print(f"Timeout waiting for {category_class} notes")
            return []
        except Exception as e:
            print(f"Error extracting {category_class} notes: {e}")
            return []

    def get_scent_strength(self):
        """Extract scent strength with improved handling"""
        scent_data = {}
        try:
            containers = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".s-circle-container")
                )
            )
            
            for container in containers:
                try:
                    scent_name = container.find_element(
                        By.CSS_SELECTOR, ".text-xs.grey"
                    ).text
                    circle = container.find_element(By.CSS_SELECTOR, ".s-circle")
                    class_list = circle.get_attribute("class").split()
                    size_classes = [cls for cls in class_list if "s-circle_" in cls]
                    
                    if size_classes:
                        size = size_classes[0].split("_")[-1]
                        scent_data[scent_name] = size
                except Exception as e:
                    continue
                    
            return scent_data
        except Exception as e:
            print(f"Error extracting scent strength: {e}")
            return {}

    def get_detailed_ratings(self):
        """
        Extract detailed ratings (rating value and number of ratings) for each category.
        """
        detailed_ratings = {}
        try:
            # Wait for the ratings section to load
            self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "barfiller_element"))
            )

            # Find all rating elements
            rating_elements = self.driver.find_elements(By.CLASS_NAME, "barfiller_element")

            for element in rating_elements:
                try:
                    # Extract the category name (e.g., "Duft", "Haltbarkeit")
                    category = element.find_element(By.CLASS_NAME, "text-xs.upper.grey").text

                    # Extract the rating value (e.g., "7.5")
                    rating_value = element.find_element(
                        By.CSS_SELECTOR, ".text-lg.bold"
                    ).text

                    # Extract the number of ratings (e.g., "18 Bewertungen")
                    num_ratings_text = element.find_element(
                        By.CSS_SELECTOR, ".lightgrey.text-2xs.upper"
                    ).text

                    # Safely extract the number of ratings
                    num_ratings = None
                    if num_ratings_text:  # Check if the text is not empty
                        parts = num_ratings_text.split()
                        if parts:  # Check if the split result is not empty
                            num_ratings = parts[0]  # Extract the first part (number)

                    # Add to the detailed_ratings dictionary
                    detailed_ratings[category] = {
                        "rating": rating_value,
                        "number_of_ratings": num_ratings,
                    }
                except NoSuchElementException as e:
                    print(f"Element not found for category {category}: {e}")
                    continue
                except Exception as e:
                    print(f"Error extracting ratings for category {category}: {e}")
                    continue

            return detailed_ratings

        except Exception as e:
            print(f"Error extracting detailed ratings: {e}")
            return {}

    def scrape_perfume(self, url):
        """
        Scrape all information for a single perfume, including diagram data
        accessed through navigation
        """
        try:
            print(f"\nScraping: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for initial page load

            # Extract basic information first
            basic_info = self.get_basic_info()
            print("Basic info extracted:", basic_info)

            # Extract detailed ratings
            detailed_ratings = self.get_detailed_ratings()
            print("Detailed ratings extracted:", detailed_ratings)

            scent_strength = self.get_scent_strength()
            print("Scent strength extracted:", scent_strength)

            # Extract scent notes
            top_notes = self.extract_scent_notes('nb_t')
            middle_notes = self.extract_scent_notes('nb_m')
            base_notes = self.extract_scent_notes('nb_b')

            # If structured notes fail, get all notes
            all_notes = None
            if not (top_notes or middle_notes or base_notes):
                try:
                    elements = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        'span.clickable_note_img span.nowrap.pointer'
                    )
                    all_notes = [el.text for el in elements if el.text.strip()]
                except Exception as e:
                    print(f"Error getting all notes: {e}")

            ratings = self.get_ratings()
            print("Ratings extracted:", ratings)

            # Navigate to Diagram section
            try:
                # Wait for the Diagram button to be clickable
                diagram_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '/html/body/div[4]/div/div[1]/div[1]/nav/div[6]/span'
                    ))
                )

                # Click the button
                print("Clicking Diagram button...")
                self.driver.execute_script("arguments[0].click();", diagram_button)

                # Wait for diagram to load
                time.sleep(2)

                # Wait for SVG to be present
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))

                # Extract scent types from the diagram
                scent_types = self.get_scent_types()
                print("Scent types extracted from diagram:", scent_types)

            except TimeoutException:
                print("Timeout waiting for Diagram button")
                scent_types = {}
            except Exception as e:
                print(f"Error navigating to diagram: {e}")
                scent_types = {}

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

    # def scrape_perfume(self, url):
    #     """
    #     Scrape all information for a single perfume, including diagram data
    #     accessed through navigation
    #     """
    #     try:
    #         print(f"\nScraping: {url}")
    #         self.driver.get(url)
    #         time.sleep(2)  # Wait for initial page load
    #         
    #         # Extract basic information first
    #         basic_info = self.get_basic_info()
    #         print("Basic info extracted:", basic_info)
    #         
    #         scent_strength = self.get_scent_strength()
    #         print("Scent strength extracted:", scent_strength)
    #         
    #         # Extract scent notes
    #         top_notes = self.extract_scent_notes('nb_t')
    #         middle_notes = self.extract_scent_notes('nb_m')
    #         base_notes = self.extract_scent_notes('nb_b')
    #         
    #         # If structured notes fail, get all notes
    #         all_notes = None
    #         if not (top_notes or middle_notes or base_notes):
    #             try:
    #                 elements = self.driver.find_elements(
    #                     By.CSS_SELECTOR, 
    #                     'span.clickable_note_img span.nowrap.pointer'
    #                 )
    #                 all_notes = [el.text for el in elements if el.text.strip()]
    #             except Exception as e:
    #                 print(f"Error getting all notes: {e}")
    #         
    #         ratings = self.get_ratings()
    #         print("Ratings extracted:", ratings)
    #         
    #         # Navigate to Diagram section
    #         try:
    #             # Wait for the Diagram button to be clickable
    #             diagram_button = WebDriverWait(self.driver, 2).until(
    #                 EC.element_to_be_clickable((
    #                     By.XPATH, 
    #                     '/html/body/div[4]/div/div[1]/div[1]/nav/div[6]/span'
    #                 ))
    #             )
    #             
    #             # Click the button
    #             print("Clicking Diagram button...")
    #             self.driver.execute_script("arguments[0].click();", diagram_button)
    #             
    #             # Wait for diagram to load
    #             time.sleep(2)
    #             
    #             # Wait for SVG to be present
    #             self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "svg")))
    #             
    #             # Extract scent types from the diagram
    #             scent_types = self.get_scent_types()
    #             print("Scent types extracted from diagram:", scent_types)
    #             
    #         except TimeoutException:
    #             print("Timeout waiting for Diagram button")
    #             scent_types = {}
    #         except Exception as e:
    #             print(f"Error navigating to diagram: {e}")
    #             scent_types = {}
    #         
    #         return {
    #             **basic_info,
    #             "scent_strength": scent_strength,
    #             "top_notes": top_notes if top_notes else None,
    #             "middle_notes": middle_notes if middle_notes else None,
    #             "base_notes": base_notes if base_notes else None,
    #             "all_notes": all_notes,
    #             "ratings": ratings,
    #             "scent_types": scent_types,
    #             "url": url
    #         }
    #         
    #     except Exception as e:
    #         print(f"Error scraping perfume {url}: {e}")
    #         return None

    def get_scent_types(self):
        """Extract scent types from diagram with improved handling"""
        try:
            # Wait for SVG elements after diagram navigation
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "svg tspan")))
            time.sleep(1)  # Additional wait for text elements
            
            # Find all text elements in the SVG
            scent_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "svg tspan"
            )
            
            scents = {}
            for element in scent_elements:
                text = element.text
                if text and '%' in text:
                    try:
                        # Split the text into name and percentage
                        name, percentage = text.rsplit(' ', 1)
                        percentage = float(percentage.replace('%', ''))
                        scents[name] = percentage
                        print(f"Found scent type: {name}: {percentage}%")
                    except ValueError:
                        # Skip if the text cannot be split properly
                        continue
                    
            return scents
        except Exception as e:
            print(f"Error extracting scent types from diagram: {e}")
            return {}

    def scrape_all_perfumes(self):
        """Scrape all perfumes with improved error handling"""
        results = []
        try:
            with open(self.links_file, 'r') as file:
                links = json.load(file)
            
            # Split the links into 8 chunks
            chunk_size = len(links) // 8
            chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
            
            # Get user input for the chunk to process
            while True:
                try:
                    index = int(input("Enter an index between 1 and 8: "))
                    if 1 <= index <= 8:
                        break
                    else:
                        print("Index must be between 1 and 8.")
                except ValueError:
                    print("Please enter a valid integer.")
            
            # Process the selected chunk
            selected_chunk = chunks[index - 1]
            for i, link in enumerate(selected_chunk, 1):
                print(f"\nProcessing perfume {i} of {len(selected_chunk)}")
                perfume_data = self.scrape_perfume(link)
                if perfume_data:
                    results.append(perfume_data)
                    # Save intermediate results
                    self.save_results(results, f'perfumes_data_partial_chunk_{index}.json')
                time.sleep(2)  # Delay between requests
                    
            return results
        except Exception as e:
            print(f"Error scraping all perfumes: {e}")
            return results  # Return partial results if available

    def save_results(self, results, output_file='perfumes_data_ccc.json'):
        """Save results with error handling"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    scraper = ParfumoScraper()
    try:
        scraper.setup_driver()
        
        # Test with a single URL first
        test_url = "https://www.parfumo.de/Parfums/Kilian/Amber_Oud"
        # result = scraper.scrape_perfume(test_url)
        
        # if result:
        if True:
            print("\nTest scrape successful!")
            # scraper.save_results([result], 'test_perfume.json')
            
            # If test successful, proceed with all perfumes
            results = scraper.scrape_all_perfumes()
            scraper.save_results(results)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
